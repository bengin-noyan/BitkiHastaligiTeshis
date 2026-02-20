import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# 1. Model ve Veri Yolu
model = tf.keras.models.load_model('bitki_hastaligi_fine_tuned.h5')
data_dir = "data/final_dataset/train"
class_names = sorted(os.listdir(data_dir))
img_path = 'sagliklielma.jpg'


img = tf.keras.utils.load_img(img_path, target_size=(224, 224))
img_array = tf.keras.utils.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0)
img_array = preprocess_input(img_array) # Modeli "anlayacağı" dile çevirir [-1, 1]

# 3. Tahmin
predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])
result_index = np.argmax(score)
result_name = class_names[result_index]
confidence = 100 * np.max(score)


print(f"Tahmin: {result_name} (%{confidence:.2f})")

plt.imshow(img)
plt.title(f"Tahmin: {result_name} (%{confidence:.2f})")
plt.axis('off')
plt.show() # Bu komut sayesinde resim ekrana gelecek!