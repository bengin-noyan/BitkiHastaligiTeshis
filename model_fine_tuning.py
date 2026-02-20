import tensorflow as tf
from tensorflow.keras.optimizers import Adam

# 1. Mevcut Modeli Yükle
model = tf.keras.models.load_model('bitki_hastaligi_mobileNet_v1.h5')

# 2. Base Model Katmanlarını Bul (Genelde modelin ilk katmanı base_model'dir)
# Modeli nasıl kurduğuna bağlı olarak base_model'e erişiyoruz.
base_model = model.layers[0]

# 3. Katmanları Serbest Bırak
base_model.trainable = True

# --- KRİTİK ADIM ---
# Tüm katmanları eğitmek yerine, sadece son 20 katmanı açıyoruz.
# Bu, modelin temel bilgilerini bozmadan detay öğrenmesini sağlar.
fine_tune_at = 100
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

# 4. Modeli Çok Düşük Bir Öğrenme Oranıyla Yeniden Derle
# Öğrenme oranını çok düşük ($10^{-5}$) tutuyoruz ki modelin "hafızası" silinmesin.
model.compile(
    optimizer=Adam(learning_rate=0.00001),
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

import tensorflow as tf

# Veri yolunu belirle (Görseldeki yolunla aynı olduğundan emin ol)
DATA_DIR = "data/final_dataset/train"

# 1. Eğitim Veri Setini (Train) Oluştur
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2, # %20'sini doğrulama için ayırıyoruz
    subset="training",
    seed=123,
    image_size=(224, 224), # MobileNetV2 için standart boyut
    batch_size=32
)

# 2. Doğrulama Veri Setini (Validation) Oluştur
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=(224, 224),
    batch_size=32
)
""
# --- Performans İyileştirmesi (Opsiyonel ama Önerilir) ---
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

# 5. Ekstra 5-10 Epoch Daha Eğit
# TRAIN_DS ve VAL_DS daha önce tanımladığın veri setleridir.
history_fine = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

# 6. Yeni Modeli Kaydet
model.save('bitki_hastaligi_fine_tuned.h5')