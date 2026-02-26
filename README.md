# 🌿 Bitki Hastalıkları Teşhis Sistemi ve Tarımsal Verimlilik Analizi (YOLOv8)

Bu proje, domates bitkilerindeki hastalıkları ve besin eksikliklerini yapay zeka (derin öğrenme) kullanarak anlık olarak tespit etmek amacıyla geliştirilmiştir. 

## 🚀 Proje Hakkında
Bu çalışma kapsamında, farklı bitki hastalıkları ve kalsiyum eksikliği gibi durumları içeren kapsamlı bir veri seti kullanılmıştır. Model, Yönetim Bilişim Sistemleri (YBS) bitirme çalışmaları kapsamında optimize edilmiştir.

## 📊 Model Performansı (V2 - Kıdemli Model)
Model, Google Colab üzerinde T4 GPU kullanılarak 50 epoch boyunca eğitilmiştir.

* **Mimari:** YOLOv8 Nano
* **Genel Başarı (mAP50):** %85.2
* **Doğruluk Oranları:**
  * Domates Sarı Yaprak Kıvırcıklık Virüsü: %98.5
  * Kalsiyum Eksikliği (Defisiensi Kalsium): %79.5 (V1'e göre %10 iyileşme)
  * Yaprak Yanıklığı: %95.6

## 🛠️ Kullanılan Teknolojiler
* **Dil:** Python
* **Yapay Zeka:** Ultralytics YOLOv8
* **Veri Seti:** Roboflow (Plant-Disease-1)
* **Ortam:** VS Code & Google Colab

## 💻 Nasıl Çalıştırılır?
Projeyi yerel bilgisayarınızda test etmek için:

1. Gerekli kütüphaneleri kurun: `pip install ultralytics`
2. Modeli çalıştırın:
```python
from ultralytics import YOLO
model = YOLO('best.pt')
results = model.predict(source='test_gorseli.jpg', save=True)