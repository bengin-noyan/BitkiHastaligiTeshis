# 🌿 Bitki Hastalıkları Teşhis Sistemi ve Tarımsal Verimlilik Analizi (YOLOv8)

Bu proje, bitkilerdeki hastalıkları ve anomalileri yapay zeka (derin öğrenme) kullanarak anlık ve yüksek doğrulukla tespit etmek amacıyla geliştirilmiştir. Sistem, Yönetim Bilişim Sistemleri (YBS) bitirme çalışmaları kapsamında "Tarımsal Verimlilik Analizi ve İlaçlama Optimizasyonu" algoritmalarının ana teşhis motoru olarak tasarlanmış ve optimize edilmiştir.

## 🚀 Proje Hakkında
Sistemin ilk versiyonlarında spesifik bitkiler (örn. domates) üzerine çalışılmış olup, nihai versiyonda kapasite devasa bir boyuta taşınmıştır. Model şu an **16.600 fotoğraflık** kapsamlı PlantDoc veri seti üzerinde çalışmakta ve elma karalekesinden yaban mersini hastalıklarına kadar **29 farklı sınıfı** tanıyabilmektedir.

## 🏆 Model Performansı (V4 - Şampiyon Model / Güncel)
Sistemin zorlu saha koşullarındaki tespit hassasiyetini ve güven skorunu (confidence) zirveye taşımak amacıyla, modelin mimarisi ve eğitim parametreleri baştan aşağı yenilenmiştir.

* **Mimari:** YOLOv8 Medium (`yolov8m.pt`) - Yüksek parametreli derin öğrenme ağı.
* **Eğitim Ortamı:** Kaggle (GPU P100) - 12 saatlik kesintisiz ağır eğitim (150 Epoch hedefli).
* **Görüntü İşleme:** Modelin minik yaprak lekelerini (scab/rust vb.) büyüteçle görebilmesi için görüntü boyutu endüstri standardının üzerine, `imgsz=800` piksel çözünürlüğüne çıkarılmıştır.
* **Öne Çıkan Gelişmeler (Büyük Sıçrama):** Eski versiyonlarda (V3) %59 seviyelerinde kalan güven skoru, bu modelde **%94 (0.94 Confidence)** gibi altın standart kabul edilen bir seviyeye ulaşmıştır. Sistem sadece ana hastalığı bulmakla kalmaz, arka plandaki diğer yaprakların türünü ve başlangıç seviyesindeki hastalıkları da eşzamanlı olarak başarıyla sınıflandırır.

## 🛠️ Kullanılan Teknolojiler
* **Dil:** Python
* **Yapay Zeka:** Ultralytics YOLOv8 (Medium)
* **Veri Seti:** Roboflow (PlantDoc - 29 Sınıf, 16.6k Görsel)
* **Ortam:** VS Code & Kaggle (Model Eğitimi)

## 💻 Nasıl Çalıştırılır?
Projeyi yerel bilgisayarınızda test etmek için terminale aşağıdaki komutu girmeniz yeterlidir:

```bash
# Gerekli kütüphanelerin kurulumu
pip install ultralytics

# Terminal üzerinden görsel testi (Örnek)
yolo task=detect mode=predict model=plantdoc_150epoch.pt conf=0.25 source="test_gorseli.jpg"