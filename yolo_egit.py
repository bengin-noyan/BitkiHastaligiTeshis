from ultralytics import YOLO

# 1. Modeli Yükle
# "yolov8n.pt" --> Nano model. En hızlısı ve en hafifi budur.
# İlk çalıştırmada internetten otomatik indirecek.
model = YOLO("yolov8n.pt")

# 2. Eğitimi Başlat
# data: İndirdiğimiz klasörün içindeki yol haritası (data.yaml)
# epochs: Model veriyi kaç kez baştan sona dönecek? (25 tur yeterli)
# imgsz: Resim boyutu (Standart 640 piksel)
results = model.train(data="Plant-Disease-1/data.yaml", epochs=25, imgsz=640)