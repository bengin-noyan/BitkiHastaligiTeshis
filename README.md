🌿 Tarımsal Verimlilik Analizi: Derin Öğrenme ile Bitki Hastalıkları Teşhisi
Bu proje, sürdürülebilir tarım ve dijital dönüşüm ilkeleri çerçevesinde, bitki hastalıklarını yüksek doğrulukla teşhis ederek tarımsal verimliliği artırmayı hedefleyen bir Karar Destek Sistemi (KDS) modelidir.

🚀 Proje Özeti ve Başarı Milatları
Yönetim Bilişim Sistemleri perspektifiyle geliştirilen bu model, sadece bir sınıflandırma aracı değil, aynı zamanda tarım arazilerindeki ürün kayıplarını minimize etmek için tasarlanmış veriye dayalı bir analiz sistemidir.

Güncel Başarı Oranı: %95,60 Validation Accuracy (Doğrulama Başarısı).

Önceki Model: %87,14 (MobileNetV2 tabanlı).

İyileştirme: Hibrit yaklaşım ve EfficientNetB0 mimarisi ile %8,46'lık net başarı artışı sağlanmıştır.

🛠️ Teknik Mimari ve Teknolojiler
Model, modern derin öğrenme teknikleri ve "Transfer Learning" (Transfer Öğrenme) stratejisi üzerine inşa edilmiştir.

Ana Mimari: EfficientNetB0 (ImageNet ağırlıkları ile).

Veri Seti: 38 farklı bitki ve hastalık sınıfını içeren, toplam 43.427 görselden oluşan geniş kapsamlı veri seti.

Hibrit Yaklaşım: Modelin genel başarısını ve gerçek dünya koşullarına dayanıklılığını artırmak için Data Augmentation (Veri Artırımı) ve Transfer Learning teknikleri birleştirilmiştir.

Optimizasyon: Adam Optimizer (LR: 0.001) ve Categorical Crossentropy kayıp fonksiyonu kullanılmıştır.

📊 Eğitim Sonuçları (Epoch 7 - Peak Performance)
Model, 7. eğitim adımında (epoch) en yüksek performansına ulaşarak Karar Destek Sistemleri için gerekli olan güvenilirlik eşiğini aşmıştır:

Validation Accuracy: 0.9560

Validation Loss: 0.1393

Eğitim Stratejisi: Aşırı öğrenmeyi (overfitting) önlemek için %30 Dropout ve Early Stopping (Erken Durdurma) mekanizmaları uygulanmıştır.

🔮 Gelecek Çalışmalar
Veri Çeşitliliği: Mevcut 38 sınıfa stratejik öneme sahip bitki türlerinin (örneğin: soğan) eklenmesi.

Mobil Entegrasyon: Çiftçilerin tarlada anlık teşhis koyabilmesi için modelin bir mobil uygulama üzerinden servis edilmesi.

Maliyet Analizi: Teşhis edilen hastalıkların ekonomik etkilerini hesaplayan bir maliyet modülünün sisteme entegre edilmesi.