import streamlit as st
from ultralytics import YOLO
from PIL import Image

# 1. SAYFA AYARLARI (Geniş ekran ve temiz tasarım)
st.set_page_config(page_title="Tarımsal Karar Destek Sistemi", layout="wide")


# Modeli belleğe al (Uygulamanın hızlanması için)
@st.cache_resource
def modeli_yukle():
    return YOLO("best.pt")


model = modeli_yukle()

# 2. BİLGİ TABANI (Türkçe ve Kurumsal Dil)
BILGI_TABANI = {
    "healthy": {
        "bitki": "Genel (Türü Belirtilmemiş)",
        "durum": "Sağlıklı",
        "eylem": "Mevcut bakım rutinine devam edin. Herhangi bir müdahaleye gerek yoktur.",
        "ekonomi": "Gereksiz ilaçlama maliyeti %100 oranında önlendi."
    },
    "defisiensi_kalsium": {
        "bitki": "Domates",
        "durum": "Kalsiyum Eksikliği",
        "eylem": "Sıvı kalsiyum nitrat veya klorür içerikli yaprak gübresi uygulayın.",
        "ekonomi": "Sadece sorunlu bölgelere lokal uygulama yapılarak gübre maliyetinden %60 tasarruf sağlandı."
    },
    "Tomato_Leaf_Curl": {
        "bitki": "Domates",
        "durum": "Sarı Yaprak Kıvırcıklık Virüsü",
        "eylem": "Virüsü taşıyan beyazsineklerle acil kimyasal mücadele başlatın ve ağır hastalıklı bitkileri sökün.",
        "ekonomi": "Erken müdahale sayesinde seranın geneline yayılım engellendi, olası %80 rekolte kaybı önlendi."
    }
}

# 3. ANA ARAYÜZ TASARIMI
st.title("🌱 Tarımsal Karar Destek ve Optimizasyon Paneli")
st.markdown(
    "Bu panel, yapay zeka destekli görüntü işleme teknolojilerini kullanarak tarımsal hastalıkları tespit eder ve maliyet optimizasyonu sağlayan yönetimsel eylem planları sunar.")
st.markdown("---")

# 4. YAN PANEL (Dosya Yükleme)
st.sidebar.header("Sistem Kontrolü")
uploaded_file = st.sidebar.file_uploader("Analiz edilecek bitki görselini yükleyin", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Görseli oku ve analize sok
    img = Image.open(uploaded_file)
    results = model.predict(source=img, conf=0.40)

    # Ekranı iki eşit sütuna böl
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Görsel Teşhis Sonucu")
        # Modelin çizdiği kutucuklu resmi göster
        st.image(results[0].plot(), use_container_width=True)

    with col2:
        st.subheader("Yönetimsel Analiz Raporu")

        # Eğer model hiçbir hastalık veya sınıf bulamazsa
        if len(results[0].boxes) == 0:
            st.success("✅ Sistem bu görselde herhangi bir anomali tespit etmedi. Bitki sağlıklı görünmektedir.")
        else:
            # Modelin bulduğu her bir kutucuk için döngü
            for box in results[0].boxes:
                label_raw = model.names[int(box.cls[0])]
                conf = float(box.conf[0])

                # Veritabanında eşleşme ara, bulamazsa varsayılan metni getir
                info = BILGI_TABANI.get(label_raw, {
                    "bitki": "Sistemde Kayıtlı Değil",
                    "durum": label_raw,
                    "eylem": "Sistem bu sınıf için henüz bir eylem planı içermiyor. Uzman incelemesi önerilir.",
                    "ekonomi": "Veri bulunamadı."
                })

                # Temiz ve kurumsal raporlama arayüzü
                st.info(f"🌿 **İncelenen Bitki Türü:** {info['bitki']}")
                st.warning(f"🔍 **Tespit Edilen Durum:** {info['durum']} (Sistem Güveni: %{conf * 100:.1f})")
                st.write(f"🛠️ **Önerilen Eylem Planı:** {info['eylem']}")
                st.success(f"📈 **Finansal Optimizasyon:** {info['ekonomi']}")
                st.markdown("---")
else:
    # Kullanıcı henüz fotoğraf yüklemediyse gösterilecek kibar mesaj
    st.info("Sistemi başlatmak için lütfen sol taraftaki menüden bir görsel yükleyin.")