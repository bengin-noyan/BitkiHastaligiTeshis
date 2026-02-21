import os

# Veri setinin olduğu klasör yolunu buraya yaz
data_dir = "data/final_dataset/train"

# Klasör isimlerini alfabetik sırayla çek
class_names = sorted(os.listdir(data_dir))

print(f"\n--- Toplam {len(class_names)} Sınıf Mevcut ---\n")
for i, name in enumerate(class_names, 1):
    print(f"{i}. {name}")