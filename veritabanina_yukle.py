import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# 1. Firebase'e Maymuncuk Anahtarımızla Bağlanıyoruz
print(" Firebase sunucularına bağlanılıyor...")
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Yükleyeceğimiz O Meşhur Bilgi Tabanı
HASTALIK_VERITABANI = {
    "blight": {
        "TR": {
            "ilac": "Mancozeb, Azoxystrobin veya Bakır Oksiklorür etken maddeli Fungisitler.",
            "sonuc": "Yapraklardaki lezyonların büyümesi durdurulur, bitki yeşil aksamını koruyarak fotosenteze devam eder.",
            "ekonomi": "Erken müdahale edilmezse tarlanın tamamına yayılıp %40-%60 oranında rekolte (verim) kaybına yol açar. İlaçlama maliyeti, kurtarılan ürün değerinin yanında ihmal edilebilir seviyede (%3-5) kalır."
        },
        "EN": {
            "ilac": "Fungicides containing Mancozeb, Azoxystrobin, or Copper Oxychloride.",
            "sonuc": "Lesion growth stops, the plant maintains its green parts and continues photosynthesis.",
            "ekonomi": "If not treated early, it can cause 40-60% yield loss. Spraying cost is negligible (3-5%) compared to the saved crop value."
        }
    },
    "rust": {
        "TR": {
            "ilac": "Tebuconazole veya Propiconazole etken maddeli Sistemik Fungisitler.",
            "sonuc": "Sporların rüzgarla diğer bitkilere sıçraması engellenir, pas lekeleri kurutulur.",
            "ekonomi": "Özellikle mısır ve buğdayda tane tutumunu düşürerek doğrudan piyasa değerini %30 azaltır. Optimizasyonla 10x ROI (Yatırım Getirisi) sağlanır."
        },
        "EN": {
            "ilac": "Systemic Fungicides containing Tebuconazole or Propiconazole.",
            "sonuc": "Windborne spore transmission is blocked, rust spots dry out.",
            "ekonomi": "Reduces grain set and direct market value by 30%. Timely intervention provides a 10x ROI."
        }
    },
    "scab": {
        "TR": {
            "ilac": "Captan veya Difenoconazole etken maddeli koruyucu ve tedavi edici ilaçlar.",
            "sonuc": "Meyve ve yaprak yüzeyindeki mantar kolonileri imha edilir, yeni sürgünler korunur.",
            "ekonomi": "Ağacın veriminden ziyade meyvenin 'kozmetik' kalitesini vurur. İlaçlama yapılmazsa ürünler 1. sınıf kalite yerine 'meyve suyu' (ıskarta) fiyatına satılır, gelir %70 düşer."
        },
        "EN": {
            "ilac": "Protective/curative sprays containing Captan or Difenoconazole.",
            "sonuc": "Fungal colonies on fruits/leaves are destroyed, new shoots are protected.",
            "ekonomi": "Impacts cosmetic quality. Untreated fruits are sold for juice (cull) rather than premium grade, reducing revenue by up to 70%."
        }
    },
    "virus": {
        "TR": {
            "ilac": "Virüsün doğrudan ilacı yoktur! Taşıyıcı böcekler (Beyazsinek vb.) için Imidacloprid içerikli İnsektisit.",
            "sonuc": "Hastalık yayılım zinciri kırılır. Enfekte olan bitkiler sökülüp tarladan uzaklaştırılmalıdır.",
            "ekonomi": "Virüs salgınları tüm serayı/tarlayı 2 hafta içinde yok edebilir (%100 zarar riski). Taşıyıcı böcek mücadelesi en kritik sigorta maliyetidir."
        },
        "EN": {
            "ilac": "No direct cure for viruses! Use Imidacloprid-based Insecticide for vector insects (e.g., whiteflies).",
            "sonuc": "Disease spread chain is broken. Infected plants must be uprooted and removed.",
            "ekonomi": "Viral outbreaks can destroy a field in 2 weeks (100% loss risk). Vector control is the most critical insurance cost."
        }
    },
    "default": {
        "TR": {
            "ilac": "Geniş spektrumlu koruyucu tarım ilaçları veya organik bakır preperatları.",
            "sonuc": "Anomalinin yayılması yavaşlatılır, bitki bağışıklığı desteklenir.",
            "ekonomi": "Risk skoru yüksek olduğundan, acil eylem planı başlatılarak muhtemel pazar kayıpları minimize edilir."
        },
        "EN": {
            "ilac": "Broad-spectrum protective pesticides or organic copper preparations.",
            "sonuc": "Anomaly spread is slowed down, plant immunity is supported.",
            "ekonomi": "Due to high risk score, an emergency action plan minimizes potential market losses."
        }
    }
}

# 3. Verileri Tek Tek Buluta Yazdırıyoruz
print(" Buluta veri aktarımı başlıyor...")
for hastalik_id, bilgiler in HASTALIK_VERITABANI.items():
    # Firestore'da 'hastaliklar' adında bir koleksiyon oluşturup içine atıyoruz
    db.collection("hastaliklar").document(hastalik_id).set(bilgiler)
    print(f"✅ {hastalik_id} veritabanına başarıyla eklendi!")

print(" BÜTÜN VERİLER BAŞARIYLA GOOGLE CLOUD'A YÜKLENDİ!")