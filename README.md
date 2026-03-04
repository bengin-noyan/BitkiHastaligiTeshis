# 🌿 Bitki Hastalıkları Teşhis Sistemi ve Tarımsal Verimlilik Analizi (YOLOv8)

Bu proje, domates bitkilerindeki hastalıkları ve besin eksikliklerini yapay zeka (derin öğrenme) kullanarak anlık olarak tespit etmek amacıyla geliştirilmiştir. 

## 🚀 Proje Hakkında
Bu çalışma kapsamında, farklı bitki hastalıkları ve kalsiyum eksikliği gibi durumları içeren kapsamlı bir veri seti kullanılmıştır. Model, Yönetim Bilişim Sistemleri (YBS) bitirme çalışmaları kapsamında optimize edilmiştir.

## 📊 Model Performansı (V2 - Kıdemli Model)
Model, Google Colab üzerinde T4 GPU kullanılarak 50 epoch boyunca eğitilmiştir.

## 📊 Model Performansı (V3 - Gelişmiş Görüş Modeli)

Sistemin zorlu saha koşullarındaki tespit hassasiyetini artırmak amacıyla **YOLOv8 Medium (yolov8m)** mimarisine geçiş yapılmıştır. Model, Google Colab üzerinde T4 GPU kullanılarak 90 epoch boyunca eğitilmiş ve Erken Durdurma (Early Stopping) ile aşırı öğrenmesi engellenmiştir.

* **Mimari:** YOLOv8 Medium 
* **Eğitim Süresi:** 90 Epoch (Early Stopping ile optimize edildi)
* **Öne Çıkan Gelişmeler:** Modelin tespit güveninde (confidence score) ciddi bir artış sağlanmıştır. Önceki modelin %34 emin olabildiği silik ve zorlu anomali bölgeleri, V3 modeli tarafından %59 netlikle (yaklaşık 2 kat daha yüksek bir özgüvenle) tespit edilebilmektedir.
* **Sistemdeki Rolü:** Projenin asıl odak noktası olan "Tarımsal Verimlilik Analizi ve İlaçlama Optimizasyonu" algoritmalarının ana teşhis motoru olarak kullanılmaktadır.

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