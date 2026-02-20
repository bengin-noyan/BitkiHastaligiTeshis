# 🌿 Bitki Hastalığı Teşhis Sistemi ve Tarımsal Verimlilik Asistanı (MobileNetV2)

Bu proje, derin öğrenme teknikleri kullanılarak bitki yapraklarındaki hastalıkları otonom bir şekilde teşhis etmek için geliştirilmiştir.

##  Proje Durumu
* **Model:** MobileNetV2 (Transfer Learning)
* **Başarı Oranı:** %83,94 Doğrulama Başarısı (Validation Accuracy)
* **Veri Seti:** 38 farklı bitki ve hastalık kategorisi

## Teknik Detaylar
Projede TensorFlow ve Keras kullanılarak görüntü sınıflandırma yapılmıştır. Model, eğitim sürecinde 10 epoch sonunda yüksek bir kararlılığa ulaşmıştır. Şu an etiket eşleşmeleri ve modelin elma/mısır ayrımı üzerindeki ince ayarları (fine-tuning) devam etmektedir.

---
Bengin Noyan 

Güncelleme: Akademik Optimizasyon ve Model Hassas Ayarı (Fine-Tuning)
Projenin ikinci aşamasında, modelin genel başarısını artırmak ve türler arasındaki kararsızlığı (özellikle elma ve mısır karmaşasını) gidermek için Hassas Ayar (Fine-Tuning) yapılmıştır.

 Performans Karşılaştırması
Yapılan optimizasyonlar sonucunda modelin doğruluk oranındaki değişim aşağıdadır:

İlk Model Başarısı: %83.94

Optimize Edilmiş Model Başarısı: %87.14

Kayıp (Loss) Oranı: 0.81'den 0.42'ye düşürülmüştür.

 Hata Giderme ve Test Sonucu
İlk sürümde sağlıklı elma yaprağını mısır pası ile karıştıran etiket hatası, MobileNetV2 mimarisinin son katmanlarının yeniden eğitilmesiyle (unfreezing) çözülmüştür.

Son Test Çıktısı:
(Not: Model artık elmayı %90+ güvenle doğru teşhis etmektedir.)