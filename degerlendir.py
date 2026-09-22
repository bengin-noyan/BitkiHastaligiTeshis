"""
Model hangi sınıfı hangisiyle karıştırıyor diye bakmak için yazdım.

çalıştırmak için:  python degerlendir.py

runs/detect/<val-klasoru>/ içine şunlar çıkıyor:
  - confusion_matrix.png            : hangi sınıf hangi sınıfla karışmış
  - confusion_matrix_normalized.png : aynısının yüzdelik hali, okuması daha kolay
  - sınıf bazlı mAP tablosu da terminale yazılıyor, düşük olanlar sorunlu demek
"""
import os
from ultralytics import YOLO

# ayarlar (gerekirse burayı değiştir)
MODEL = "plantdoc_150epoch.pt"
DATA = "datasets/PlantDoc/plantdoc.v7i.yolov8/data.yaml"
SPLIT = "test"   # "test" yoksa "val" yap
IMGSZ = 640
# ------------------------------

if __name__ == "__main__":
    if not os.path.exists(MODEL):
        raise SystemExit(f"Model bulunamadi: {MODEL}")
    if not os.path.exists(DATA):
        raise SystemExit(f"data.yaml bulunamadi: {DATA}\n"
                         f"Dogru yolu MODEL/DATA degiskenlerinde guncelle.")

    model = YOLO(MODEL)

    # bazı veri setlerinde test split'i yok, o zaman val'e düşüyoruz
    try:
        metrics = model.val(data=DATA, split=SPLIT, imgsz=IMGSZ, plots=True)
    except Exception as e:
        print(f"[uyari] split='{SPLIT}' calismadi ({e}); split='val' deneniyor...")
        metrics = model.val(data=DATA, split="val", imgsz=IMGSZ, plots=True)

    print("\n" + "=" * 60)
    print("GENEL SONUCLAR")
    print("=" * 60)
    print(f"mAP50    : {metrics.box.map50:.4f}")
    print(f"mAP50-95 : {metrics.box.map:.4f}")

    # sınıf bazlı mAP50, düşükten yükseğe sıralı (en sorunlular en üstte)
    print("\n" + "=" * 60)
    print("SINIF BAZLI mAP50 (dusuk = problemli sinif)")
    print("=" * 60)
    names = model.names
    per_class = list(zip(metrics.box.ap_class_index, metrics.box.ap50))
    per_class.sort(key=lambda x: x[1])  # mAP50'ye göre artan
    for cls_idx, ap50 in per_class:
        print(f"  {ap50:6.3f}   {names[int(cls_idx)]}")

    # çıktıların nereye kaydedildiğini yaz
    print("\n" + "=" * 60)
    print(f"Gorseller kaydedildi: {metrics.save_dir}")
    print("  -> confusion_matrix.png  ve  confusion_matrix_normalized.png")
    print("=" * 60)
