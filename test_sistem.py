import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import matplotlib.pyplot as plt
import os

# 1. AYARLAR VE YOLLAR
model_path = 'en_iyi_model_final.h5'
data_dir = "data/final_dataset/train"
test_image_path = "testedelim_resim.jpg"

# 2. SINIF İSİMLERİNİ ÇEKME
class_names = sorted(os.listdir(data_dir))

# 3. SİSTEMİ AYAĞA KALDIR
print("\n--- Sistem ayağa kaldırılıyor, KDS Modeli Yükleniyor... ---")
model = tf.keras.models.load_model(model_path)
print("--- Model Yüklendi! Teşhis Başlıyor... ---\n")


# 4. TEŞHİS VE GÖRSELLEŞTİRME FONKSİYONU
def predict_disease_and_show(img_path):
    try:
        # Resmi model için hazırla
        img = image.load_img(img_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)

        # Tahmin yap
        predictions = model.predict(img_array)
        score = predictions[0]

        # Sonuçları hesapla
        predicted_class = class_names[np.argmax(score)]
        confidence = 100 * np.max(score)

        # --- YENİ EKLENEN KISIM (THRESHOLD) ---
        plt.figure(figsize=(8, 6))
        plt.imshow(img)

        # Eğer güven oranı %60'tan düşükse:
        if confidence < 60:
            plt.title(f"Sistem Emin Değil\nEn Yakın Tahmin: {predicted_class} (%{confidence:.2f})",
                      fontsize=14, color='orange', fontweight='bold')
            print(f"⚠️ UYARI: Model bu resimden emin olamadı (Güven: %{confidence:.2f})")
        else:
            # Güven yüksekse normal çalışsın
            title_color = 'green' if "healthy" in predicted_class.lower() else 'red'
            plt.title(f"Sistem Kararı: {predicted_class}\nGüven Oranı: %{confidence:.2f}",
                      fontsize=14, color=title_color, fontweight='bold')

        plt.axis('off')
        plt.tight_layout()
        plt.show()
        # --------------------------------------

        # Terminal Çıktısı
        print(f"🌿 TEŞHİS SONUCU 🌿")
        print(f"------------------------")
        print(f"Görsel: {img_path}")
        print(f"Teşhis: {predicted_class}")
        print(f"Güven Oranı: %{confidence:.2f}")
        print(f"------------------------\n")


        plt.figure(figsize=(8, 6))

        plt.imshow(img)


        title_color = 'green' if confidence > 80 else 'red'
        plt.title(f"Sistem Kararı: {predicted_class}\nGüven Oranı: %{confidence:.2f}",
                  fontsize=14, color=title_color, fontweight='bold')

        plt.axis('off')
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"HATA: Resim yüklenirken veya işlenirken bir sorun oluştu: {e}")



predict_disease_and_show(test_image_path)