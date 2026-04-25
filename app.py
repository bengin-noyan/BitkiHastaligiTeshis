import streamlit as st
from ultralytics import YOLO
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 1. Sayfa Ayarları (En üstte olmak zorundadır)
st.set_page_config(page_title="Tarımsal Analiz Sistemi", page_icon="🌿", layout="wide")

# --- FIREBASE BULUT BAĞLANTISI ---
# Streamlit sayfayı her yenilediğinde Firebase'i tekrar tekrar başlatmaya çalışıp çökmesin diye bu kontrolü yapıyoruz.
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- OTURUM (SESSION) KONTROLÜ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Modeli Yükleme (Önbellekli)
@st.cache_resource
def load_model():
    return YOLO("plantdoc_150epoch.pt") 

model = load_model()

# --- DİL VE ÇEVİRİ AYARLARI (Sözlükler) ---
LANGS = {
    "Türkçe": {
        "sidebar_title": "⚙️ Kontrol Paneli",
        "sidebar_info": "YBS Bitirme Projesi\nYOLOv8m Şampiyon Model",
        "conf_label": "Yapay Zeka Güven Skoru (Confidence)",
        "upload_label": "📸 Yaprak Fotoğrafı Yükle",
        "main_title": "🌿 Tarımsal Verimlilik ve Akıllı İlaçlama Analiz Sistemi",
        "main_desc": "Yapay zeka tabanlı anlık hastalık teşhisi ve tarımsal risk analizi paneli.",
        "info_upload": "👈 Lütfen analize başlamak için sol menüden bir yaprak fotoğrafı yükleyin.",
        "col1_sub": "👁️ Yapay Zeka Görsel Analizi",
        "img_caption_orig": "Yüklenen Orijinal Görsel",
        "analyze_btn": "🚀 Derin Öğrenme Analizini Başlat",
        "spinner": "Şampiyon model hücre seviyesinde inceliyor... 🕵️‍♂️",
        "img_caption_res": "Teşhis Edilen Hastalıklar",
        "col2_sub": "📊 Tarımsal Verimlilik Raporu",
        "plant_type_label": "🔎 Analiz Edilen Bitki Türü",
        "warning_no_plant": "⚠️ Tanımlanamayan Nesne: Sistem bu görselde analiz edilebilir bir tarım ürünü veya yaprak tespit edemedi.",
        "metric_risk_label": "Tahmini Verim Kaybı Riski",
        "metric_no_analysis": "Analiz Yapılamadı",
        "success_healthy": "✅ Analiz sonucu: Tespit edilen **{}** yaprakları tamamen sağlıklı kategorisinde.",
        "warning_disease": "⚠️ Dikkat! Görselde {} adet hastalıklı bölge tespit edildi.",
        "action_plan_title": "### 💊 İlaçlama ve Eylem Planı (Öneri)",
        "fungal_msg": "Mantar (Fungal) kaynaklı enfeksiyon. Acil Fungisit uygulaması yapılmalıdır.",
        "virus_msg": "Virüs kaynaklı anomali. Taşıyıcı böceklerle mücadele edilmelidir.",
        "bacterial_msg": "Bakteriyel/Fungal lekelenme veya çürüme. Gerekli zirai ilaçlar önerilir.",
        "expander_title": "🚨 {} İçin Detaylı Mücadele Raporu",
        "label_ilac": "💉 Önerilen Etken Madde",
        "label_beklenti": "🌱 Zirai Beklenti",
        "label_ekonomi": "💰 Ekonomik Etki Analizi",
        "db_error": "Bulut veritabanına bağlanılamadı."
    },
    "English": {
        "sidebar_title": "⚙️ Control Panel",
        "sidebar_info": "MIS Graduation Project\nYOLOv8m Champion Model",
        "conf_label": "AI Confidence Score",
        "upload_label": "📸 Upload Leaf Photo",
        "main_title": "🌿 Agricultural Productivity and Smart Spraying Analysis System",
        "main_desc": "AI-based instant disease diagnosis and agricultural risk analysis panel.",
        "info_upload": "👈 Please upload a leaf photo from the sidebar to start analysis.",
        "col1_sub": "👁️ AI Visual Analysis",
        "img_caption_orig": "Uploaded Original Image",
        "analyze_btn": "🚀 Start Deep Learning Analysis",
        "spinner": "Champion model is scanning at cell level... 🕵️‍♂️",
        "img_caption_res": "Diagnosed Diseases",
        "col2_sub": "📊 Agricultural Productivity Report",
        "plant_type_label": "🔎 Analyzed Plant Type",
        "warning_no_plant": "⚠️ Unidentified Object: The system could not detect any analyzable agricultural product or leaf.",
        "metric_risk_label": "Estimated Yield Loss Risk",
        "metric_no_analysis": "Analysis Failed",
        "success_healthy": "✅ Analysis result: Detected **{}** leaves are in the perfectly healthy category.",
        "warning_disease": "⚠️ Attention! {} diseased areas were detected in the image.",
        "action_plan_title": "### 💊 Spraying and Action Plan (Recommendation)",
        "fungal_msg": "Fungal infection. Urgent Fungicide application is required.",
        "virus_msg": "Viral anomaly. Vector insects should be controlled.",
        "bacterial_msg": "Bacterial/Fungal spotting or rot. Specific pesticides are recommended.",
        "expander_title": "🚨 Detailed Treatment Report for {}",
        "label_ilac": "💉 Recommended Active Ingredient",
        "label_beklenti": "🌱 Agricultural Expectation",
        "label_ekonomi": "💰 Economic Impact Analysis",
        "db_error": "Could not connect to the cloud database."
    }
}

CLASS_TR = {
    "Apple": "Elma", "Tomato": "Domates", "Grape": "Üzüm", "Corn": "Mısır", "Potato": "Patates", 
    "Cherry": "Kiraz", "Strawberry": "Çilek", "Bell_pepper": "Dolmalık Biber", "healthy": "Sağlıklı",
    "scab": "Karaleke", "rust": "Pas", "virus": "Virüs", "blight": "Yanıklık"
}


# ==========================================
# 🔐 MODÜL 1: GİRİŞ (LOGIN) EKRANI
# ==========================================
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center;'>🌿 Sisteme Giriş</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Tarımsal Analiz Paneline erişmek için lütfen yetkili girişi yapın.</p>", unsafe_allow_html=True)
        st.write("---")
        
        username = st.text_input("👤 Kullanıcı Adı")
        password = st.text_input("🔑 Şifre", type="password") 
        
        login_button = st.button("Giriş Yap", width="stretch", type="primary")
        
        if login_button:
            if username.strip().lower() == "admin" and password.strip() == "ybs2026":
                st.session_state.logged_in = True
                st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")


# ==========================================
# 🌿 MODÜL 2: ANA SİSTEM (DASHBOARD)
# ==========================================
def main_app():
    st.sidebar.title("🌐 Dil / Language")
    lang_choice = st.sidebar.radio("", ("Türkçe", "English"))
    T = LANGS[lang_choice]

    st.sidebar.markdown("---")
    st.sidebar.title(T["sidebar_title"])
    st.sidebar.info(T["sidebar_info"])
    conf_threshold = st.sidebar.slider(T["conf_label"], min_value=0.10, max_value=1.00, value=0.25, step=0.05)
    st.sidebar.markdown("---")
    uploaded_file = st.sidebar.file_uploader(T["upload_label"], type=["jpg", "jpeg", "png"], key="resim_yukleyici")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Çıkış Yap / Logout", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.clear() 
        st.rerun()

    st.title(T["main_title"])
    st.markdown(T["main_desc"])
    st.write("---")

    if uploaded_file is not None:
        if "mevcut_resim" not in st.session_state or st.session_state.mevcut_resim != uploaded_file.name:
            st.session_state.analiz_tamamlandi = False
            st.session_state.mevcut_resim = uploaded_file.name

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader(T["col1_sub"])
            image = Image.open(uploaded_file)
            st.image(image, caption=T["img_caption_orig"], width="stretch")
            analiz_butonu = st.button(T["analyze_btn"], width="stretch")

        if analiz_butonu:
            with col1:
                with st.spinner(T["spinner"]):
                    results = model.predict(source=image, conf=conf_threshold, imgsz=800)
                    st.session_state.res_plotted = results[0].plot()[:, :, ::-1]
                    boxes = results[0].boxes
                    st.session_state.detected_classes = [model.names[int(c)] for c in boxes.cls]
                    st.session_state.confidences = [float(c) for c in boxes.conf]
                    st.session_state.analiz_tamamlandi = True

        if st.session_state.get("analiz_tamamlandi", False):
            with col1:
                st.image(st.session_state.res_plotted, caption=T["img_caption_res"], width="stretch")
                
            with col2:
                st.subheader(T["col2_sub"])
                detected_classes = st.session_state.detected_classes
                confidences = st.session_state.confidences
                
                identified_plants = set()
                if len(detected_classes) > 0:
                    for cls_name in detected_classes:
                        plant_key = cls_name.split()[0]
                        identified_plants.add(plant_key)
                
                if identified_plants:
                    if lang_choice == "Türkçe":
                        tr_plants = [CLASS_TR.get(p, p) for p in identified_plants]
                        plant_str = ", ".join(tr_plants)
                    else:
                        plant_str = ", ".join(identified_plants)
                    st.info(f"{T['plant_type_label']}: **{plant_str}**")

                if len(detected_classes) == 0:
                    st.warning(T["warning_no_plant"])
                    st.metric(T["metric_risk_label"], "0%", T["metric_no_analysis"], delta_color="off")
                else:
                    hastalik_kelimeleri = ["scab", "rust", "mold", "virus", "spot", "blight", "curl", "rot", "mildew", "scorch"]
                    hastalikli_yapraklar = [sinif for sinif in detected_classes if any(k in sinif.lower() for k in hastalik_kelimeleri)]
                    
                    if len(hastalikli_yapraklar) == 0:
                        st.success(T["success_healthy"].format(plant_str if identified_plants else "Bitki"))
                        st.metric(T["metric_risk_label"], "%0", "OK", delta_color="normal")
                    else:
                        st.warning(T["warning_disease"].format(len(hastalikli_yapraklar)))
                        ortalama_guven = sum(confidences) / len(confidences)
                        risk_skoru = min(int((len(hastalikli_yapraklar) * 15) * ortalama_guven) + 20, 95)
                        st.metric(T["metric_risk_label"], f"%{risk_skoru}", f"-{risk_skoru}%", delta_color="inverse")
                        
                        st.markdown(T["action_plan_title"])
                        
                        benzersiz_hastaliklar = set(hastalikli_yapraklar)
                        for hastalik in benzersiz_hastaliklar:
                            h = hastalik.lower()
                            display_name = CLASS_TR.get(hastalik, hastalik) if lang_choice == "Türkçe" else hastalik
                            
                            db_key = "default"
                            for key in ["blight", "rust", "scab", "virus", "mold", "mildew", "spot", "rot", "scorch", "curl"]:
                                if key in h:
                                    if key in ["mold", "mildew", "spot", "rot", "scorch"]: 
                                        db_key = "blight" 
                                    elif key == "curl":
                                        db_key = "virus"
                                    else:
                                        db_key = key
                                    break
                                    
                            lang_key = "TR" if lang_choice == "Türkçe" else "EN"
                            
                            # ==========================================
                            # ☁️ GOOGLE FIRESTORE'DAN ANLIK VERİ ÇEKİMİ 
                            # ==========================================
                            try:
                                doc_ref = db.collection("hastaliklar").document(db_key)
                                doc = doc_ref.get()
                                if doc.exists:
                                    bilgi = doc.to_dict().get(lang_key, {})
                                else:
                                    bilgi = {"ilac": T["db_error"], "sonuc": T["db_error"], "ekonomi": T["db_error"]}
                            except Exception as e:
                                bilgi = {"ilac": T["db_error"], "sonuc": T["db_error"], "ekonomi": T["db_error"]}
                            
                            with st.expander(T["expander_title"].format(display_name), expanded=True):
                                st.markdown(f"**{T['label_ilac']}:** {bilgi.get('ilac', '')}")
                                st.markdown(f"**{T['label_beklenti']}:** {bilgi.get('sonuc', '')}")
                                st.markdown(f"**{T['label_ekonomi']}:** {bilgi.get('ekonomi', '')}")
    else:
        st.info(T["info_upload"])

# ==========================================
# 🚦 YÖNLENDİRİCİ (ROUTER) KONTROLÜ
# ==========================================
if not st.session_state.logged_in:
    login_page()
else:
    main_app()