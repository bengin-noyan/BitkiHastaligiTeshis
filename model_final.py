import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
import os


data_dir = "data/final_dataset/train"
batch_size = 16
img_size = (224, 224)

train_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="training", seed=123,
    image_size=img_size, batch_size=batch_size, label_mode='categorical')

val_ds = tf.keras.utils.image_dataset_from_directory(
    data_dir, validation_split=0.2, subset="validation", seed=123,
    image_size=img_size, batch_size=batch_size, label_mode='categorical')

num_classes = len(train_ds.class_names) # 38 sınıfı otomatik algılar

# 3. (Data Augmentation)
# Bu bölüm modelin farklı açılardan öğrenmesini sağlar, ezberlemeyi önler.
data_augmentation = models.Sequential([
    layers.RandomFlip("horizontal_and_vertical"),
    layers.RandomRotation(0.2),
    layers.RandomZoom(0.2),
    layers.RandomContrast(0.1),
])

# 4. HİBRİT MODEL MİMARİSİ (EfficientNetB0)
base_model = EfficientNetB0(input_shape=(224, 224, 3), include_top=False, weights='imagenet')
base_model.trainable = False # İlk aşamada temel katmanları donduruyoruz

model = models.Sequential([
    layers.Input(shape=(224, 224, 3)),
    data_augmentation,
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.3),
    layers.Dense(num_classes, activation='softmax')
])

# 5. DERLEME (Syntax hatası giderildi)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# 6. GÜVENLİK KAYITLARI (Callbacks)

callbacks = [
    tf.keras.callbacks.ModelCheckpoint('en_iyi_model_final.h5', save_best_only=True),
    tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True)
]


print("\n--- Eğitim Başlıyor! Hedef: %95+ Başarı ---")
model.fit(train_ds, validation_data=val_ds, epochs=10, callbacks=callbacks)