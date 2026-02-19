"""import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import cv2
import os
import matplotlib.pyplot as plt

# --- 1. VERİ YOLLARI (image_1d2fab.png dosyana göre) ---
TRAIN_DIR = "data/final_dataset/train"
VAL_DIR = "data/final_dataset/val"
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

train_ds = tf.keras.utils.image_dataset_from_directory(TRAIN_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE)
val_ds = tf.keras.utils.image_dataset_from_directory(VAL_DIR, image_size=IMG_SIZE, batch_size=BATCH_SIZE)

# --- 2. MOBILENET V2 İLE TRANSFER LEARNING ---
# ImageNet ile eğitilmiş hazır beyni alıyoruz
base_model = tf.keras.applications.MobileNetV2(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False  # Hazır zekayı başlangıçta donduruyoruz

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.2),
    layers.Dense(38, activation='softmax')  # 38 bitki sınıfın için
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# --- 3. EĞİTİM (10 Epoch Yeterli Olacaktır) ---
print("\n--- PROFESYONEL MOBILENET EĞİTİMİ BAŞLIYOR ---")
history = model.fit(train_ds, validation_data=val_ds, epochs=10)
model.save("bitki_hastaligi_mobileNet_v1.h5")

# --- 4. TEST: ELMA YAPRAĞINI DOĞRU TANIMA ---
kategoriler = sorted(os.listdir(TRAIN_DIR))


def teshis_et(resim_yolu):
    img = cv2.imread(resim_yolu)
    if img is None: return print("Resim bulunamadı!")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224)) / 255.0
    img_array = np.expand_dims(img_resized, axis=0)

    tahmin = model.predict(img_array)
    sonuc_index = np.argmax(tahmin)
    guven = np.max(tahmin) * 100

    print(f"\nTeşhis: {kategoriler[sonuc_index]}")
    print(f"Güven Oranı: %{guven:.2f}")


# Klasöründeki sagliklielma.jpg dosyasını test ediyoruz
teshis_et("sagliklielma.jpg")"""

import tensorflow as tf
import numpy as np
import cv2
import os

# 1. MODELİ VE VERİ SETİNİ BAĞLA
model = tf.keras.models.load_model('bitki_hastaligi_mobileNet_v1.h5')
TRAIN_DIR = "data/final_dataset/train"

# --- KRİTİK ADIM: Gerçek etiket sırasını alıyoruz ---
# sorted(os.listdir) yerine Keras'ın kendi sıralamasını kullanıyoruz
train_ds = tf.keras.utils.image_dataset_from_directory(TRAIN_DIR, image_size=(224, 224))
kategoriler = train_ds.class_names  # Gerçek sıralama budur!


def teshis_et_derinlemesine(resim_yolu):
    img = cv2.imread(resim_yolu)
    if img is None: return print("Resim bulunamadı!")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))

    # MobileNet'in en yüksek güven verdiği formatı kullanıyoruz
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_resized)
    img_array = np.expand_dims(img_array, axis=0)

    tahmin = model.predict(img_array)[0]

    # En yüksek 3 tahmini yazdıralım ki "Apple" nerede görelim
    en_iyi_indeksler = tahmin.argsort()[-3:][::-1]

    print(f"\n--- MODELİN EN GÜÇLÜ 3 TAHMİNİ ---")
    for i in en_iyi_indeksler:
        print(f"{kategoriler[i]}: %{tahmin[i] * 100:.2f}")


teshis_et_derinlemesine("sagliklielma.jpg")