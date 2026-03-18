import cv2
from ultralytics import YOLO

# 1. MODELİ YÜKLE
model = YOLO("best.pt")

# 2. TÜM BİTKİLER İÇİN GENİŞLETİLMİŞ BİLGİ TABANI
# Buraya modelinin tanıdığı diğer sınıfları (Apple, Corn vb.) ekleyebilirsin.
BILGI_TABANI = {
    "healthy": {
        "teshis": "Sağlıklı Bitki Dokusu",
        "cozum": "Müdahale gerekmiyor. Mevcut bakım takvimine devam edilsin.",
        "tasarruf_stratejisi": "Gereksiz koruyucu ilaçlama maliyeti %100 önlendi. Toprak ve bitki sağlığı korundu."
    },
    "defisiensi_kalsium": {
        "teshis": "Kalsiyum Eksikliği",
        "cozum": "Yapraktan sıvı kalsiyum nitrat uygulaması.",
        "tasarruf_stratejisi": "Sadece sorunlu bölgelere lokal uygulama ile %60 gübre tasarrufu."
    },
    "Tomato_Leaf_Curl": {
        "teshis": "Domates Kıvırcıklık Virüsü",
        "cozum": "Beyazsinek mücadelesi ve karantina.",
        "tasarruf_stratejisi": "Erken teşhisle ürün kaybı %80'den %10'a düşürüldü."
    },
    "Apple_Scab": { # Eğer elma karalekesi varsa
        "teshis": "Elma Karalekesi (Fungus)",
        "cozum": "Uygun fungisit uygulaması ve nem kontrolü.",
        "tasarruf_stratejisi": "Meyve kalitesi korundu, pazar değeri kaybı önlendi."
    }
}

# 3. ANALİZ FONKSİYONU
def analiz_et(gorsel_yolu):
    results = model.predict(source=gorsel_yolu, conf=0.50)
    
    print("\n" + "="*60)
    print("📋 TARIMSAL KARAR DESTEK VE MALİYET OPTİMİZASYON RAPORU")
    print("="*60)

    for r in results:
        # Eğer model hiçbir kutu bulamadıysa (boş döndüyse)
        if len(r.boxes) == 0:
            print("✅ Sonuç: Bitki üzerinde hastalık belirtisi saptanmadı.")
            print("💰 Strateji: Gereksiz ilaç kullanımı durdurularak maliyet tasarrufu sağlandı.")
        else:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id] # Modelin verdiği isim (Örn: 'healthy')
                conf = float(box.conf[0])
                
                print(f"🔍 Tespit Edilen Sınıf: {label} (Güven: %{conf*100:.1f})")
                
                # Eğer bu sınıf bizim bilgi tabanımızda varsa detayları bas
                if label in BILGI_TABANI:
                    info = BILGI_TABANI[label]
                    print(f"📌 Teşhis           : {info['teshis']}")
                    print(f"🛠️ Önerilen Eylem   : {info['cozum']}")
                    print(f"💎 Ekonomik Çıktı  : {info['tasarruf_stratejisi']}")
                else:
                    print(f"⚠️ Uyarı: '{label}' sınıfı için henüz bir eylem planı tanımlanmadı.")
    
    print("="*60 + "\n")

# 4. ÇALIŞTIR
analiz_et("sagliklielma.jpg")