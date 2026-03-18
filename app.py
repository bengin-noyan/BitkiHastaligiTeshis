import streamlit as st
from ultralytics import YOLO
from PIL import Image

# 1. Sayfa Ayarları (Geniş Ekran Dashboard Tasarımı)
st.set_page_config(page_title="Tarımsal Verimlilik Analizi", page_icon="🌿", layout="wide")

# 2. Modeli Yükleme (Önbellekli)
@st.cache_resource
def load_model():
    # Model 148MB olduğu için Drive'dan indirme mantığı buraya eklenecek (Deploy aşamasında)
    return YOLO("plantdoc_150epoch.pt")

model = load_model()

# 3. Sol Menü (Sidebar)
st.sidebar.title("⚙️ Kontrol Paneli")
st.sidebar.info("YBS Bitirme Projesi\nYOLOv8m Şampiyon Model")
conf_threshold = st.sidebar.slider("Yapay Zeka Güven Skoru (Confidence)", min_value=0.10, max_value=1.00, value=0.25, step=0.05)
st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📸 Yaprak Fotoğrafı Yükle", type=["jpg", "jpeg", "png"])

# 4. Ana Ekran Başlığı
st.title("🌿 Tarımsal Verimlilik ve Akıllı İlaçlama Karar Destek Sistemi")
st.markdown("Yapay zeka tabanlı anlık hastalık teşhisi ve tarımsal risk analizi paneline hoş geldiniz.")
st.write("---")

# 5. Dashboard Düzeni
if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("👁️ Yapay Zeka Görsel Analizi")
        image = Image.open(uploaded_file)
        st.image(image, caption="Yüklenen Orijinal Görsel", use_container_width=True)
        
        analiz_butonu = st.button("🚀 Derin Öğrenme Analizini Başlat", use_container_width=True)

    if analiz_butonu:
        with col1:
            with st.spinner('Şampiyon model hücre seviyesinde inceliyor... 🕵️‍♂️'):
                results = model.predict(source=image, conf=conf_threshold, imgsz=800)
                res_plotted = results[0].plot()[:, :, ::-1] # Renk düzeltmesi
                st.image(res_plotted, caption="Teşhis Edilen Hastalıklar", use_container_width=True)
                
                boxes = results[0].boxes
                detected_classes = [model.names[int(c)] for c in boxes.cls]
                confidences = [float(c) for c in boxes.conf]
        
        with col2:
            st.subheader("📊 Tarımsal Verimlilik Raporu")
            
            # --- YENİ MANTIKSAL BÖLÜM: BİTKİ TÜRÜNÜ TESPİT ETME ---
            identified_plants = set()
            if len(detected_classes) > 0:
                for cls_name in detected_classes:
                    # Sınıf adının ilk kelimesini al (Örn: "Apple Scab Leaf" -> "Apple")
                    plant_name = cls_name.split()[0]
                    identified_plants.add(plant_name)
            
            # Bitki adı raporun en başına yazılır (Eğer tespit edildiyse)
            if identified_plants:
                # İngilizce isimleri Türkçeye çevirme (Basit Sözlük)
                translate_dict = {"Apple": "Elma", "Tomato": "Domates", "Grape": "Üzüm", "Corn": "Mısır", "Potato": "Patates"}
                tr_plants = [translate_dict.get(p, p) for p in identified_plants]
                plant_str = ", ".join(tr_plants)
                st.info(f"🔎 Analiz Edilen Bitki Türü: **{plant_str}**")
            # -----------------------------------------------------

            # Eğer hiçbir şey bulamadıysa
            if len(detected_classes) == 0:
                st.success("✅ Görüntüde herhangi bir anomali tespit edilmedi. Bitki sağlıklı.")
                st.metric("Tahmini Verim Kaybı Riski", "%0", "Tehdit Yok")
                st.info("🔎 Bitki Türü: Model resimde belirgin bir yaprak dokusu tespit edemediği için bitki türü belirlenemedi.")
            
            # Tespit varsa
            else:
                hastalik_kelimeleri = ["scab", "rust", "mold", "virus", "spot", "blight", "curl", "rot"]
                hastalikli_yapraklar = [sinif for sinif in detected_classes if any(k in sinif.lower() for k in hastalik_kelimeleri)]
                
                # Sadece sağlıklı yaprak tespit edildiyse (Örn: "Apple Leaf", "Tomato healthy")
                if len(hastalikli_yapraklar) == 0:
                    plant_str = ", ".join([translate_dict.get(p, p) for p in identified_plants]) if identified_plants else "Bitki"
                    st.success(f"✅ Analiz sonucu: Tespit edilen **{plant_str}** yaprakları sağlıklı kategorisinde.")
                    st.metric("Tahmini Verim Kaybı Riski", "%0", "Tehdit Yok")
                
                # Gerçekten hastalık bulduysa
                else:
                    st.warning(f"⚠️ Dikkat! Görselde {len(hastalikli_yapraklar)} adet hastalıklı bölge tespit edildi.")
                    
                    # Risk Skoru Hesaplama
                    ortalama_guven = sum(confidences) / len(confidences)
                    risk_skoru = min(int((len(hastalikli_yapraklar) * 15) * ortalama_guven) + 20, 95)
                    st.metric("Tahmini Verim Kaybı Riski", f"%{risk_skoru}", f"-{risk_skoru}% (Kritik Düşüş)", delta_color="inverse")
                    
                    st.markdown("### 💊 İlaçlama ve Eylem Planı (Öneri)")
                    benzersiz_hastaliklar = set(hastalikli_yapraklar)
                    for hastalik in benzersiz_hastaliklar:
                        h = hastalik.lower()
                        if "scab" in h or "rust" in h or "mold" in h:
                            st.error(f"**{hastalik}**: Mantar (Fungal) kaynaklı enfeksiyon. Acil Fungisit uygulaması yapılmalıdır.")
                        elif "virus" in h or "curl" in h:
                            st.error(f"**{hastalik}**: Virüs kaynaklı anomali. Taşıyıcı böceklerle mücadele edilmelidir.")
                        elif "spot" in h or "blight" in h:
                            st.error(f"**{hastalik}**: Bakteriyel/Fungal lekelenme. Bakır içerikli ilaçlar önerilir.")

else:
    st.info("👈 Lütfen analize başlamak için sol menüden bir yaprak fotoğrafı yükleyin.")