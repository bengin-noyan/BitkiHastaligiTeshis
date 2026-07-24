# 🌱 Veri Ekleme Rehberi — Karışan Sınıfları İyileştirme

**Amaç:** Confusion matrix'te düşük başarım gösteren sınıflara temiz veri ekleyip
Roboflow'da yeni bir versiyon (v8) oluşturmak, sonra Kaggle'da yeniden eğitmek.
**29 sınıf korunur** (birleştirme yok — öneriler hastalığa göre farklı).

Roboflow projesi: **`chainfly-kbwvw / plantdoc-rcmou`** (mevcut v7'nin üstüne v8 kurulacak).

---

## 1) Hangi sınıfa ne kadar veri? (ölçülen verilere göre öncelik)

| Öncelik | Sınıf | Mevcut durum | Sorun | Hedef (yeni görsel) |
|---------|-------|--------------|-------|---------------------|
| 🔴 1 | `Tomato leaf bacterial spot` | recall **0.49** | Yarısını kaçırıyor / Septoria sanıyor | **+150-200** |
| 🔴 2 | `Tomato Early blight leaf` | mAP 0.765, test'te sadece **9 örnek** | Çok az veri | **+150-200** |
| 🟠 3 | `Corn Gray leaf spot` | mAP 0.799 | Corn leaf blight'a karışıyor | **+100-150** |
| 🟠 4 | `Potato leaf early blight` | mAP 0.802 | Az/gürültülü | **+100** |
| 🟡 5 | `Tomato leaf yellow virus` | mAP 0.838 | İyi ama geliştirilebilir | **+50-100** |
| 🟡 6 | `Peach leaf` | mAP 0.831 | Az örnek | **+50** |

> **Kural:** Zayıf sınıfları en az **2 katına** çıkarmayı ve sınıflar arası dengeyi
> korumayı hedefle. Bir sınıfta 800, diğerinde 40 örnek olması başarımı düşürür.
> İyi durumdaki sınıflara (Apple rust 0.99, Raspberry 0.97) **dokunma.**

---

## 2) Kaliteli görsel nereden bulunur?

Öncelik sırasına göre kaynaklar:

1. **Roboflow Universe** (en pratik) — https://universe.roboflow.com
   - Hastalık adını ara (ör. "tomato bacterial spot"), hazır etiketli datasetlerden
     görselleri kendi projene aktar. Aynı formatta olduğu için en hızlısı.
2. **PlantVillage** (Kaggle: "plantvillage dataset") — devasa, etiketli.
   - Not: Bunlar düz arka planlı stüdyo görselleri; senin uygulaman saha fotoğrafıyla
     çalışıyor. Bu yüzden PlantVillage'ı **tek başına değil**, saha fotoğraflarıyla
     **karışık** kullan (çeşitlilik için).
3. **Kendi/saha fotoğrafların** — en değerlisi; gerçek kullanım koşuluna en yakın.
4. **Google Görseller** — dikkatli ve az; lisans ve kalite kontrolü şart.

**Çeşitlilik önemli:** farklı ışık, açı, arka plan, hastalık şiddeti (hafif→ağır)
karışık olsun. Hepsi aynı tip fotoğraf olursa model gerçek dünyada zorlanır.

---

## 3) Roboflow'da ekleme + etiketleme

1. Roboflow → **`plantdoc-rcmou`** projesini aç.
2. Sol menü **Upload** → yeni görselleri sürükle-bırak.
3. **Annotate** sekmesinde her görseli aç:
   - Hastalıklı yaprağın etrafına **bounding box** çiz.
   - Sınıfı **TAM olarak mevcut isimle** seç (ör. `Tomato leaf bacterial spot`).
     ⚠️ Yeni/yanlış yazımla sınıf oluşturma — 29 sınıf sabit kalmalı.
   - Bir görselde birden çok hastalıklı yaprak varsa hepsini kutula.
4. Etiketlenen görselleri **Add to Dataset** ile sete kat (train/valid/test dağıtımını
   Roboflow otomatik yapar; ~%70/20/10).

**Etiket kalitesi = model kalitesi.** Kutular yaprağı tam sarsın, hastalık belirtisini
içersin, gereksiz arka planı dışarıda bıraksın.

---

## 4) Preprocessing & Augmentation ayarları (KRİTİK)

Yeni **Version** oluştururken:

- **Preprocessing:**
  - `Auto-Orient` ✅
  - `Resize → 640×640` ✅
- **Augmentation:** **HEPSİNİ KAPAT** ❌
  - Sebep: Augmentation'ı eğitimde YOLO anlık (on-the-fly) yapacak. Diske gömülü
    augmentation hem seti şişirir hem daha kötü sonuç verir.
  - (Mevcut v7 gömülü augmentation'lı; v8'i temiz tutuyoruz.)

---

## 5) v8 versiyonunu oluştur ve dışa aktar

1. **Generate New Version** → yukarıdaki ayarlarla oluştur → **v8**.
2. **Export Dataset → Format: YOLOv8 → download zip** (veya "show download code").
3. Kaggle'a iki yoldan verebilirsin:
   - **Roboflow API** ile doğrudan notebook'tan indir (`kaggle_egitim.ipynb`'deki
     hücre — `VERSION = 8` yap), **veya**
   - zip'i **Kaggle Dataset** olarak yükle, `DATA_YAML` yolunu ona ayarla.

---

## 6) Kaggle'da eğit ve karşılaştır

`kaggle_egitim.ipynb`'yi kullan:

- Model: `yolo11m.pt` (sıfırdan — eski modelin üstüne DEĞİL).
- Reçete hazır: 150 epoch, AdamW, cos_lr, on-the-fly augmentation, patience=30.
- Eğitim sonrası `val()` çalışır, **yeni confusion matrix + sınıf-bazlı mAP** üretir.

**Başarı ölçütü:** yeni modelde
- `Tomato leaf bacterial spot` recall'u **0.49'un belirgin üstünde**,
- genel **mAP50 ≥ 0.89** (eski skoru korumalı/aşmalı),
- confusion matrix'te domates-leke ve mısır kutularının **soluklaşması**.

Sağlanıyorsa: `best.pt`'yi indir → `app.py`'deki `load_model()` içinde dosya adını
değiştir. Sağlanmıyorsa eski model yerinde durur, kayıp yok.

---

## 7) Yapılacaklar / Yapılmayacaklar özeti

✅ **Yap:**
- Zayıf sınıflara çeşitli, temiz, doğru etiketli görsel ekle
- Sınıflar arası dengeyi koru
- Augmentation'ı Roboflow'da kapat, YOLO'ya bırak
- Her adımda `val()` ile ölç, gözle karar verme

❌ **Yapma:**
- Aynı v7 verisini tekrar eğitme (yeni bilgi yok)
- İyi sınıfları bozacak şekilde gereksiz veri ekleme
- Yeni/yanlış isimli sınıf oluşturma
- Tek tip (hep aynı ışık/arka plan) görsel yığma
