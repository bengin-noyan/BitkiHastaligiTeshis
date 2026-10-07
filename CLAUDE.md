# CLAUDE.md

Bu dosya Claude Code'un bu projede çalışırken ihtiyaç duyduğu bilgileri içeriyor.

## Proje nedir

Bitki hastalığı teşhis sistemi. YOLOv8 ile yaprak fotoğrafından hastalık tespit
ediyor, sonra tespit edilen hastalık için ilaç/verim kaybı önerisi üretiyor.
YBS bitirme projesi.

İki ayrı arayüz var, ikisi de aynı modeli ve aynı SQLite veritabanını kullanıyor:

- `app.py` — Streamlit web uygulaması (asıl ürün, 2400+ satır tek dosya)
- `api_server.py` + `mobile/` — FastAPI backend ve Expo/React Native mobil uygulama

## Çalıştırma

Sanal ortam `.venv1` (Python 3.12). Bütün bağımlılıklar kurulu durumda.

```bash
# web uygulaması
.venv1/Scripts/python.exe -m streamlit run app.py

# mobil backend (port 8000)
.venv1/Scripts/python.exe api_server.py

# mobil uygulama
cd mobile && npm start
```

Varsayılan `admin` hesabının şifresi `ADMIN_PASSWORD` ortam değişkeninden
okunuyor. Tanımlı değilse hesap hiç oluşturulmuyor. `.env.ornek` dosyasını
`.env` adıyla kopyalayıp doldurun (`.env` gitignore'da). Streamlit tarafı
`.streamlit/secrets.toml` içindeki `ADMIN_PASSWORD` anahtarını da okuyor.

Şifre belirlemek / sıfırlamak için:

```bash
.venv1/Scripts/python.exe sifre_ayarla.py admin
```

Şifreyi komut satırına argüman olarak vermeyin, kabuk geçmişine düşüyor.
Script `getpass` ile soruyor.

Model değerlendirme / confusion matrix için: `python degerlendir.py`
(datasets/ klasörü gerekiyor, repoda yok).

## Dosya haritası

| Dosya | Ne yapıyor |
|---|---|
| `app.py` | Streamlit uygulaması. CSS, DB, model, Gemini, 3 sayfa, hepsi burada |
| `guvenlik.py` | Şifre hash'leme/doğrulama. app.py ve api_server.py ortak kullanıyor |
| `sifre_ayarla.py` | Kullanıcı şifresi belirleme/sıfırlama scripti |
| `.env.ornek` | Ortam değişkeni şablonu. Kopyasını `.env` olarak doldurun |
| `api_server.py` | Mobil için REST uçları: /login /register /analyze /history /history/delete |
| `plantdoc_150epoch.pt` | Eğitilmiş YOLOv8m modeli, 29 sınıf, ~155 MB (gitignore'da) |
| `tarimsal_analiz.db` | SQLite: `kullanicilar` + `analiz_gecmisi` tabloları (gitignore'da) |
| `firebase_key.json` | Firestore servis hesabı anahtarı (gitignore'da) |
| `.streamlit/secrets.toml` | `GEMINI_API_KEY` burada (gitignore'da) |
| `assets/` | Logo ve login arka plan görselleri, base64 olarak CSS'e gömülüyor |
| `degerlendir.py` | Sınıf bazlı mAP ve confusion matrix çıkaran script |
| `VERI_EKLEME_REHBERI.md` | Zayıf sınıflara veri ekleme planı (Roboflow v8 hedefi) |
| `mobile/app/` | expo-router sayfaları: index (login), home, history |
| `mobile/src/` | components, constants (config/i18n/theme), context, services/api.ts |

## app.py yapısı

Tek dosya ama sırası belli:

1. `asset_data_uri()` — görselleri base64 data-uri'ye çeviriyor
2. SQLite kurulumu ve `analizi_kaydet()`
3. Büyük global CSS bloğu (~100-490. satır)
4. `get_db()` Firestore, `load_model()` YOLO (ikisi de `cache_resource`)
5. Gemini öneri katmanı: `_gemini_oneri_cek` → `llm_ile_oneri_getir` → `oneri_getir`
6. `LANGS` dict — bütün TR/EN arayüz metinleri (~667-1003)
7. `CLASS_TR` + `sinif_ismi_ceviri()` — model sınıf isimlerini Türkçeleştiriyor
8. `analiz_gorseli_ciz()` — kutucukları Annotator ile elle çiziyor
9. Sayfalar: `login_page()`, `main_app()`, `ana_analiz_sayfasi()`, `gecmis_analiz_sayfasi()`
10. En altta yönlendirici (`st.session_state.logged_in` kontrolü)

## Dikkat edilmesi gerekenler

**Performans kurguları bilinçli, bozmayın:**
- Ağır import'lar (pandas, plotly, firebase, ultralytics) fonksiyon içinde yapılıyor.
  Tepeye taşınırsa login ekranı çok yavaş açılıyor.
- `modeli_onyukle_arkaplan()` kullanıcı şifre yazarken modeli thread'de yüklüyor.
- `oneri_prefetch_baslat()` tespit biter bitmez Gemini isteklerini paralel atıyor.
  Cache anahtarı `(hastalik, plant_str, lang_key)` üçlüsü. `plant_str` hesabı
  prefetch ile sonuç panelinde **birebir aynı** olmak zorunda, yoksa cache ıskalıyor
  ve boşuna ikinci istek gidiyor.
- `_gemini_oneri_cek()` içinde `st.*` kullanılmıyor, çünkü arka plan thread'inden
  çağrılıyor. API key parametre olarak geçiyor.

**Çoklu dil:** Yeni bir metin eklerken `LANGS` içindeki hem `"Türkçe"` hem
`"English"` bloğuna aynı anahtarla eklemek lazım. Mobilde karşılığı
`mobile/src/constants/i18n.ts`.

**Sınıf isimleri:** `CLASS_TR` kelime kelime çeviri yapıyor, tam cümle eşlemesi
değil. `app.py` ve `api_server.py` içinde iki ayrı kopyası var, birini
değiştirince diğerini de güncellemek gerekiyor.

**Gemini yoksa ne oluyor:** API key yoksa veya istek patlarsa Firestore'daki
hazır `hastaliklar` koleksiyonuna düşüyor. İki yolun da çalıştığını kontrol edin.

**Streamlit API:** `use_container_width` yerine `width="stretch"` kullanılıyor.

**Mobil API adresi:** `mobile/src/constants/config.ts` içindeki `API_BASE_URL`
elle yazılmış yerel IP. Ağ değişince güncellenmesi gerekiyor.

## Model

- Mimari: YOLOv8 Medium, `imgsz=800` ile eğitildi, 150 epoch, Kaggle P100
- Veri: PlantDoc (Roboflow `chainfly-kbwvw/plantdoc-rcmou` v7), 29 sınıf, ~16.6k görsel
- Güven skoru ~%94
- Zayıf sınıflar ve iyileştirme planı `VERI_EKLEME_REHBERI.md` içinde

## Kod stili

- Yorumlar Türkçe ve sade. Em dash, kutu banner, "AI yazmış" hissi veren üslup yok.
- Değişken ve fonksiyon isimleri Türkçe (`hastalik_bilgisi_getir`, `analizi_kaydet`).
- Commit mesajlarına `Co-Authored-By: Claude` eklenmiyor.

## Güvenlik

**Şifreler.** `kullanicilar.sifre` alanında PBKDF2-HMAC-SHA256 hash'i duruyor,
format `pbkdf2_sha256$<iterasyon>$<tuz_b64>$<hash_b64>`. Her kullanıcının kendi
tuzu var. Bütün hash işleri `guvenlik.py` içinde, iki arayüz de oradan import
ediyor. Yeni bir giriş/kayıt yolu eklerseniz şifreyi SQL'de karşılaştırmayın,
kullanıcıyı çekip `sifre_dogrula()` kullanın.

İterasyon sayısını yükseltirseniz eski kayıtlar bozulmuyor: iterasyon hash
string'inin içinde yazılı, `yukseltme_gerekli_mi()` düşük olanları yakalıyor ve
kullanıcı giriş yaptığı anda kayıt sessizce yeni formata çevriliyor.

`veritabani_kurulumu()` her açılışta düz metin kalmış şifreleri hash'liyor
(`duz_metin_sifreleri_hashle`). Bir kere çevrildikten sonra maliyeti sıfır.

**Eksik kalanlar.** Şifre karmaşıklık kuralı yok (`sifre_ayarla.py` 8 karakter
istiyor ama arayüzler istemiyor), kaba kuvvete karşı deneme sınırı yok, oturum
`st.session_state` dışında bir yere bağlı değil. API uçları kimlik doğrulaması
istemiyor; `/history` kullanıcı adını sorgu parametresinden alıyor, yani herkes
herkesin geçmişini okuyabilir. Bunlar bilinen açıklar.

**Sırlar.** `firebase_key.json`, `.env`, `*.db`, `.streamlit/secrets.toml` ve
`*.pt` gitignore'da. Bunların içeriğini commit'e, dokümana veya log'a yazmayın.
Depo public.
