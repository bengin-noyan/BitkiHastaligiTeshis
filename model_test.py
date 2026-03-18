from ultralytics import YOLO

# Eski model yerine V2 Şampiyonunu sahaya sürüyoruz
model = YOLO("plant_disease_v2.pt")


# 2. Modeli test fotoğrafının üzerine salıyoruz! (Eminlik oranı %50'den yüksekleri göstersin)
sonuc = model.predict(source="test_tomato.jpg", conf=0.25, show=False, save=True)

print("Test tamamlandı! Eğer yaprakta hastalık bulduysa kutu içine almış olmalı.")