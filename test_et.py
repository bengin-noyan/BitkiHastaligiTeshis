from ultralytics import YOLO

# Şampiyon modeli yüklüyoruz
model = YOLO("best.pt")

# Yeni hastamızı (Tomato Leaf Curl) muayene ediyoruz
results = model.predict(source="Tomato-Leaf-Curl-1600x800.jpg",  save=True)