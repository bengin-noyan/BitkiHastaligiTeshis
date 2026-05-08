# 🌿 Bitki Hastalıkları Teşhis Sistemi ve Tarımsal Verimlilik Analizi

Bu proje, bitkilerdeki hastalıkları ve anomalileri yapay zeka (derin öğrenme) kullanarak anlık ve yüksek doğrulukla tespit etmek amacıyla geliştirilmiştir. Sistem, Yönetim Bilişim Sistemleri (YBS) bitirme çalışmaları kapsamında "Tarımsal Verimlilik Analizi ve İlaçlama Optimizasyonu" algoritmalarının ana teşhis motoru olarak tasarlanmış ve tam teşekküllü bir web uygulaması olarak hayata geçirilmiştir.

## 🚀 Proje Hakkında
Sistemin ilk versiyonlarında spesifik bitkiler (örn. domates) üzerine çalışılmış olup, nihai versiyonda kapasite devasa bir boyuta taşınmıştır. Model şu an **16.600 fotoğraflık** kapsamlı PlantDoc veri seti üzerinde çalışmakta ve elma karalekesinden yaban mersini hastalıklarına kadar **29 farklı sınıfı** tanıyabilmektedir.

## 🌟 Öne Çıkan Sistem Özellikleri
Proje sadece bir yapay zeka modelinden ibaret değildir; son kullanıcıya hitap eden dinamik bir mimariye sahiptir:
* **Güvenli Kimlik Doğrulama:** Kullanıcıların kendilerine ait hesaplar oluşturabildiği ve güvenli giriş yapabildiği (Login/Register) veritabanı destekli oturum yönetimi.
* **Kurumsal Hafıza (Loglama):** Yapılan her bir yapay zeka analizinin; tarihi, bitki türü, hastalık durumu, yapay zeka güven skoru ve analiz eden kişi bilgisiyle birlikte SQLite veritabanına otomatik ve kalıcı olarak kaydedilmesi.
* **Minimalist UI/UX:** Çiftçilerin ve ziraat mühendislerinin kolayca kullanabileceği, modern ve göz yormayan (Zümrüt Yeşili) web arayüzü tasarımı.
* **Akıllı Raporlama:** Hastalık tespit edildiğinde sadece ismi değil; tahmini verim kaybı riski, eylem planı, önerilen ilaçlar ve finansal etkileri kapsayan dinamik rapor sunumu.

## 🏆 Model Performansı (V4 - Şampiyon Model)
Sistemin zorlu saha koşullarındaki tespit hassasiyetini ve güven skorunu (confidence) zirveye taşımak amacıyla, modelin mimarisi ve eğitim parametreleri baştan aşağı yenilenmiştir.
* **Mimari:** YOLOv8 Medium (`yolov8m.pt`) - Yüksek parametreli derin öğrenme ağı.
* **Eğitim Ortamı:** Kaggle (GPU P100) - 12 saatlik kesintisiz ağır eğitim (150 Epoch hedefli).
* **Görüntü İşleme:** Modelin minik yaprak lekelerini (scab/rust vb.) büyüteçle görebilmesi için görüntü boyutu endüstri standardının üzerine, `imgsz=800` piksel çözünürlüğüne çıkarılmıştır.
* **Öne Çıkan Gelişmeler:** Eski versiyonlarda (V3) %59 seviyelerinde kalan güven skoru, bu modelde **%94 (0.94 Confidence)** gibi altın standart kabul edilen bir seviyeye ulaşmıştır. Sistem sadece ana hastalığı bulmakla kalmaz, arka plandaki diğer yaprakların türünü ve başlangıç seviyesindeki hastalıkları da eşzamanlı olarak başarıyla sınıflandırır.

## 🛠️ Kullanılan Teknolojiler
**Backend & Veritabanı:**
* Python
* SQLite3 (Kullanıcı ve Analiz Geçmişi Yönetimi)

**Yapay Zeka & Veri:**
* Ultralytics YOLOv8 (Medium)
* Roboflow (PlantDoc - 29 Sınıf, 16.6k Görsel)
* Kaggle (Model Eğitimi)

**Frontend (Arayüz):**
* Streamlit (Responsive Web App)
* CSS (Özel Minimalist Tema Tasarımı)

## 💻 Nasıl Çalıştırılır?
Projeyi kendi yerel bilgisayarınızda (localhost) tam arayüzüyle birlikte ayağa kaldırmak için terminale aşağıdaki komutları girmeniz yeterlidir:

```bash
# 1. Gerekli kütüphanelerin kurulumu (Eğer yüklü değilse)
pip install ultralytics streamlit pillow firebase-admin

# 2. Web uygulamasını başlatma
streamlit run app.py