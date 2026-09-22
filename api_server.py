# -*- coding: utf-8 -*-
"""
Mobil uygulamanın backend'i.
Streamlit tarafıyla (app.py) aynı modeli ve aynı veritabanını kullanıyor,
burası sadece dışarı REST olarak açıyor.
"""

import base64
import io
import os
import sqlite3
from datetime import datetime
from typing import Optional

import firebase_admin
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore
from PIL import Image
from pydantic import BaseModel
from ultralytics import YOLO

# ---------- ayarlar ----------

# bu dosyanın durduğu klasör
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# dosya yolları
MODEL_PATH = os.path.join(BASE_DIR, "plantdoc_150epoch.pt")
FIREBASE_KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "tarimsal_analiz.db")

# sınıf adının içinde bunlardan biri geçiyorsa bitki hasta demektir
DISEASE_KEYWORDS = [
    "scab", "rust", "mold", "virus", "spot",
    "blight", "curl", "rot", "mildew", "scorch",
]

# model ingilizce isim veriyor, türkçeye burada çeviriyoruz
CLASS_TR = {
    "apple": "Elma", "tomato": "Domates", "grape": "Üzüm",
    "corn": "Mısır", "potato": "Patates", "cherry": "Kiraz",
    "strawberry": "Çilek", "bell_pepper": "Biber", "pepper": "Biber",
    "peach": "Şeftali", "squash": "Kabak", "soybean": "Soya Fasulyesi",
    "raspberry": "Ahududu", "healthy": "Sağlıklı",
    "leaf": "Yaprağı", "leaves": "Yaprakları",
    "scab": "Karaleke", "rust": "Pas", "virus": "Virüs",
    "blight": "Yanıklık", "spot": "Lekesi", "spots": "Lekeleri",
    "mold": "Küf", "mildew": "Külleme", "rot": "Çürüklük",
    "early": "Erken", "late": "Geç", "black": "Siyah",
    "bacterial": "Bakteriyel", "mosaic": "Mozaik",
    # bunları sonradan ekledim, app.py'dekiyle aynı olması lazım
    "yellow": "Sarı", "blueberry": "Yaban Mersini", "gray": "Gri",
    "soyabean": "Soya Fasulyesi", "septoria": "Septoria",
    "two": "İki", "spotted": "Noktalı", "spider": "Örümcek",
    "mites": "Akarı",
    # bilerek boş, etikete yazdırmak istemiyoruz
    "powdery": "",
}

# ---------- FastAPI ----------

app = FastAPI(
    title="Bitki Hastalığı Teşhis API",
    description="YOLOv8 tabanlı bitki hastalığı tespit servisi",
    version="1.0.0",
)

# CORS şimdilik herkese açık, geliştirirken uğraşmayalım diye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# startup'ta doldurulan global'ler

model: Optional[YOLO] = None  # YOLOv8 modeli
db_firestore = None            # Firestore istemcisi


# ---------- sunucu açılırken ----------

@app.on_event("startup")
def startup_event():
    """Model ve Firebase bağlantısı bir kere burada kuruluyor."""
    global model, db_firestore

    # modeli yükle
    if not os.path.exists(MODEL_PATH):
        print(f"[UYARI] Model dosyası bulunamadı: {MODEL_PATH}")
    else:
        model = YOLO(MODEL_PATH)
        print(f"[BİLGİ] YOLOv8 modeli yüklendi: {MODEL_PATH}")

        # ilk analiz çok yavaş açılıyordu, o yüzden boş bir görselle bir kere
        # çalıştırıyorum. imgsz gerçek analizle aynı olmazsa ısınma işe yaramıyor.
        try:
            warmup_image = Image.new("RGB", (800, 800), (0, 0, 0))
            model.predict(source=warmup_image, imgsz=800, verbose=False)
            print("[BİLGİ] Model ısıtıldı (warm-up tamamlandı).")
        except Exception as e:
            print(f"[UYARI] Model ısıtma başarısız (kritik değil): {e}")

    # firebase
    if not os.path.exists(FIREBASE_KEY_PATH):
        print(f"[UYARI] Firebase anahtar dosyası bulunamadı: {FIREBASE_KEY_PATH}")
    else:
        try:
            cred = credentials.Certificate(FIREBASE_KEY_PATH)
            firebase_admin.initialize_app(cred)
            db_firestore = firestore.client()
            print("[BİLGİ] Firebase Firestore bağlantısı kuruldu.")
        except Exception as e:
            print(f"[HATA] Firebase başlatılamadı: {e}")


# ---------- request / response modelleri ----------

class LoginRequest(BaseModel):
    """Giriş isteği için veri modeli."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Giriş yanıtı için veri modeli."""
    success: bool
    username: str = ""


class RegisterRequest(BaseModel):
    """Kayıt isteği için veri modeli."""
    username: str
    password: str


class RegisterResponse(BaseModel):
    """Kayıt yanıtı için veri modeli."""
    success: bool
    message: str = ""


class HistoryRecord(BaseModel):
    """analiz_gecmisi tablosundaki tek bir kayıt."""
    islem_id: int
    bitki_turu: str = ""
    hastalik_durumu: str = ""
    guven_skoru: float = 0.0
    tarih: str = ""


class HistoryResponse(BaseModel):
    """Geçmiş analiz listesi yanıtı."""
    success: bool
    records: list[HistoryRecord] = []
    message: str = ""


class HistoryDeleteRequest(BaseModel):
    """Seçili geçmiş kayıtlarını silme isteği."""
    username: str
    ids: list[int]


class HistoryDeleteResponse(BaseModel):
    """Silme işlemi yanıtı."""
    success: bool
    deleted: int = 0
    message: str = ""


# ---------- yardımcı fonksiyonlar ----------

def get_sqlite_connection() -> sqlite3.Connection:
    """SQLite veritabanına bağlantı aç ve döndür."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def translate_class_name(class_name: str) -> str:
    """
    İngilizce sınıf adını türkçeye çevirir.
    örnek: 'Tomato leaf bacterial spot' -> 'Domates Yaprağı Bakteriyel Lekesi'
    """
    words = class_name.lower().replace("_", " ").split()
    # karşılığı boş olan kelimeleri (powdery gibi) hiç eklemiyoruz,
    # app.py'deki sinif_ismi_ceviri de aynısını yapıyor
    translated_words = [
        tr for w in words if (tr := CLASS_TR.get(w, w.capitalize()))
    ]
    return " ".join(translated_words)


def draw_annotated_image(result, lang: str = "tr"):
    """
    Kutucukları app.py'deki analiz_gorseli_ciz ile aynı şekilde çiziyor:
    etiket seçili dilde, güven skoru da yüzde olarak (%94 / 94%).
    Geriye BGR numpy array dönüyor.
    """
    # import'u burada bırakıyorum, yukarı alınca sunucu açılışı yavaşlıyor
    from ultralytics.utils.plotting import Annotator, colors

    is_tr = lang != "en"
    names = result.names if hasattr(result, "names") else model.names
    labels = (
        {k: translate_class_name(v) for k, v in names.items()}
        if is_tr
        else dict(names)
    )

    # example'a türkçe karakter verince Annotator PIL moduna geçiyor,
    # yoksa ş ğ ü harfleri bozuk çıkıyor
    annotator = Annotator(result.orig_img.copy(), example=str(labels))

    boxes = result.boxes
    if boxes is not None:
        for box in boxes:
            cls_id = int(box.cls)
            yuzde = int(round(float(box.conf) * 100))
            ad = labels.get(cls_id, str(cls_id))
            etiket = f"{ad} %{yuzde}" if is_tr else f"{ad} {yuzde}%"
            annotator.box_label(box.xyxy.squeeze(), etiket, color=colors(cls_id, True))

    return annotator.result()


def extract_disease_keyword(class_name: str) -> Optional[str]:
    """
    Sınıf adının içinden hastalık kelimesini bulur.
    örnek: 'Tomato leaf bacterial spot' -> 'spot'
    """
    lower_name = class_name.lower()
    for keyword in DISEASE_KEYWORDS:
        if keyword in lower_name:
            return keyword
    return None


def fetch_treatment_from_firestore(disease_keyword: str) -> dict:
    """
    Firestore'dan tedavi bilgisini çekiyor.
    Her hastalık dokümanında TR ve EN diye iki alan var.
    """
    treatment_tr = {"ilac": "", "sonuc": "", "ekonomi": ""}
    treatment_en = {"ilac": "", "sonuc": "", "ekonomi": ""}

    if db_firestore is None:
        return {"treatment_tr": treatment_tr, "treatment_en": treatment_en}

    try:
        doc_ref = db_firestore.collection("hastaliklar").document(disease_keyword)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()

            # türkçe alan
            tr_data = data.get("TR", {})
            treatment_tr = {
                "ilac": tr_data.get("ilac", ""),
                "sonuc": tr_data.get("sonuc", ""),
                "ekonomi": tr_data.get("ekonomi", ""),
            }

            # ingilizce alan
            en_data = data.get("EN", {})
            treatment_en = {
                "ilac": en_data.get("ilac", ""),
                "sonuc": en_data.get("sonuc", ""),
                "ekonomi": en_data.get("ekonomi", ""),
            }
        else:
            print(f"[UYARI] Firestore'da '{disease_keyword}' belgesi bulunamadı.")

    except Exception as e:
        print(f"[HATA] Firestore sorgusu başarısız ({disease_keyword}): {e}")

    return {"treatment_tr": treatment_tr, "treatment_en": treatment_en}


# ---------- POST /login ----------

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Kullanıcı adı + şifreyi SQLite'tan kontrol ediyor.
    Tablo: kullanicilar (id, kullanici_adi, sifre, kayit_tarihi)
    """
    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?",
            (request.username, request.password),
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return LoginResponse(success=True, username=request.username)
        else:
            return LoginResponse(success=False, username="")

    except Exception as e:
        print(f"[HATA] Giriş sorgusunda hata: {e}")
        return LoginResponse(success=False, username="")


# ---------- POST /register ----------

@app.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest):
    """
    Yeni kullanıcıyı SQLite'a ekliyor, app.py'deki Kayıt Ol sekmesiyle aynı iş.
    Kullanıcı adını küçük harfe çeviriyorum, aynısı varsa zaten IntegrityError atıyor.
    """
    kullanici_adi = request.username.strip().lower()
    sifre = request.password.strip()

    if not kullanici_adi or not sifre:
        return RegisterResponse(success=False, message="Lütfen tüm alanları doldurun.")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, kayit_tarihi) VALUES (?, ?, ?)",
            (kullanici_adi, sifre, su_an),
        )
        conn.commit()
        conn.close()
        return RegisterResponse(success=True, message="Kayıt başarılı.")

    except sqlite3.IntegrityError:
        return RegisterResponse(success=False, message="Bu kullanıcı adı zaten alınmış!")
    except Exception as e:
        print(f"[HATA] Kayıt sorgusunda hata: {e}")
        return RegisterResponse(success=False, message="Kayıt sırasında bir hata oluştu.")


# ---------- analiz geçmişine kayıt ----------

def save_analysis_to_history(
    username: str,
    lang: str,
    plant_types: list,
    plant_types_tr: list,
    diseases_info: list,
    detected_classes: list,
    confidence_scores: list,
) -> None:
    """
    Sonucu analiz_gecmisi tablosuna yazıyor. Yazdığımız metinler app.py ile
    aynı formatta olmalı yoksa web ve mobilde liste farklı görünüyor.
    """
    is_tr = lang != "en"

    plants = plant_types_tr if is_tr else plant_types
    bitki_turu = ", ".join(str(p) for p in plants) if plants else "Bilinmiyor"

    if not detected_classes:
        hastalik = "Tespit Edilemedi"
    elif not diseases_info:
        hastalik = "Sağlıklı" if is_tr else "Healthy"
    else:
        adlar = [
            (d.get("name_tr") if is_tr else d.get("name")) or d.get("name", "")
            for d in diseases_info
        ]
        hastalik = ", ".join(dict.fromkeys(a for a in adlar if a))

    skor = (
        round(sum(confidence_scores) / len(confidence_scores), 2)
        if confidence_scores
        else 0.0
    )

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO analiz_gecmisi (kullanici_adi, bitki_turu, hastalik_durumu, guven_skoru, tarih) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                username.strip().lower(),
                bitki_turu,
                hastalik,
                skor,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[HATA] Analiz geçmişe kaydedilemedi: {e}")


# ---------- GET /history ----------

@app.get("/history", response_model=HistoryResponse)
def history(username: str):
    """
    Sadece o kullanıcının kayıtlarını yeniden eskiye doğru döndürüyor.
    (app.py'de de aynı mantık var, başkasının kaydı görünmesin)
    """
    kullanici = username.strip().lower()
    if not kullanici:
        return HistoryResponse(success=False, message="Kullanıcı adı gerekli.")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT islem_id, bitki_turu, hastalik_durumu, guven_skoru, tarih "
            "FROM analiz_gecmisi WHERE kullanici_adi = ? ORDER BY tarih DESC, islem_id DESC",
            (kullanici,),
        )
        rows = cursor.fetchall()
        conn.close()

        records = [
            HistoryRecord(
                islem_id=row["islem_id"],
                bitki_turu=row["bitki_turu"] or "",
                hastalik_durumu=row["hastalik_durumu"] or "",
                guven_skoru=row["guven_skoru"] or 0.0,
                tarih=row["tarih"] or "",
            )
            for row in rows
        ]
        return HistoryResponse(success=True, records=records)

    except Exception as e:
        print(f"[HATA] Geçmiş sorgusunda hata: {e}")
        return HistoryResponse(success=False, message="Kayıtlar okunamadı.")


# ---------- POST /history/delete ----------

@app.post("/history/delete", response_model=HistoryDeleteResponse)
def history_delete(request: HistoryDeleteRequest):
    """Kayıt siler. WHERE'e kullanici_adi de koydum, başkasının kaydını silemesin."""
    kullanici = request.username.strip().lower()
    if not kullanici or not request.ids:
        return HistoryDeleteResponse(success=False, message="Silinecek kayıt seçilmedi.")

    try:
        conn = get_sqlite_connection()
        cursor = conn.cursor()
        placeholders = ",".join("?" * len(request.ids))
        cursor.execute(
            f"DELETE FROM analiz_gecmisi WHERE islem_id IN ({placeholders}) AND kullanici_adi = ?",
            [int(i) for i in request.ids] + [kullanici],
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return HistoryDeleteResponse(success=True, deleted=deleted)

    except Exception as e:
        print(f"[HATA] Kayıt silme hatası: {e}")
        return HistoryDeleteResponse(success=False, message="Kayıtlar silinemedi.")


# ---------- POST /analyze ----------

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(..., description="Analiz edilecek bitki görseli"),
    confidence: float = Form(0.25, description="Minimum güven eşiği (0-1)"),
    username: str = Form("", description="Analizi geçmişe kaydedilecek kullanıcı"),
    lang: str = Form("tr", description="Kayıt metinlerinin dili: tr | en"),
):
    """
    Gelen görseli modelden geçirip sonucu döndürüyor.
    Hastalık bulunursa Firestore'dan tedavi bilgisini de ekliyor.
    """
    # model yüklenmediyse devam etmenin anlamı yok
    if model is None:
        return {"success": False, "error": "Model yüklenemedi. Sunucu yapılandırmasını kontrol edin."}

    try:
        # görseli oku
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # tahmin
        results = model.predict(source=image, conf=confidence, imgsz=800)

        # bulunan sınıflar ve güven skorları
        detected_classes = [model.names[int(c)] for c in results[0].boxes.cls]
        confidence_scores = [float(c) for c in results[0].boxes.conf]

        # kutucuklu görseli base64'e çevir
        # hazır plot() kullanmadım, etiketi ingilizce ve 0.94 gibi basıyor,
        # bize %94 lazımdı
        annotated_bgr = draw_annotated_image(results[0], lang)
        annotated_rgb = annotated_bgr[:, :, ::-1]  # BGR -> RGB
        annotated_image = Image.fromarray(annotated_rgb)

        buffer = io.BytesIO()
        annotated_image.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        result_image_b64 = f"data:image/jpeg;base64,{image_base64}"

        # tespit listesi
        detections = []
        for cls_name, conf_score in zip(detected_classes, confidence_scores):
            detections.append({
                "class_name": cls_name,
                "class_name_tr": translate_class_name(cls_name),
                "confidence": round(conf_score, 4),
            })

        # bitki türü = sınıf adının ilk kelimesi
        plant_types = list({
            cls.split()[0] for cls in detected_classes if cls.split()
        })
        plant_types_tr = [CLASS_TR.get(p.lower(), p) for p in plant_types]

        # hastalıklı olanları ayıkla
        sick_detections = []   # hastalıklı tespitlerin skorları
        disease_keywords_found = set()

        for cls_name, conf_score in zip(detected_classes, confidence_scores):
            keyword = extract_disease_keyword(cls_name)
            if keyword:
                sick_detections.append(conf_score)
                disease_keywords_found.add(keyword)

        # hiç hastalık yoksa sağlıklı sayıyoruz
        is_healthy = len(sick_detections) == 0

        # risk skoru, 95'i geçmesin diye min koydum
        if sick_detections:
            avg_conf = sum(sick_detections) / len(sick_detections)
            risk_score = min(int(len(sick_detections) * 15 * avg_conf) + 20, 95)
        else:
            risk_score = 0

        # her hastalık için tedavi bilgisi çek
        diseases_info = []
        for keyword in sorted(disease_keywords_found):
            # hastalık adını, keyword'ün geçtiği ilk sınıf adından çıkar
            disease_display_name = keyword  # bulamazsa keyword kalsın
            for cls_name in detected_classes:
                if keyword in cls_name.lower():
                    parts = cls_name.lower().split()
                    if len(parts) > 1:
                        # ilk kelime bitki adı, kalanı hastalık
                        disease_display_name = " ".join(parts[1:])
                    break

            # türkçesi
            disease_name_tr = translate_class_name(disease_display_name)

            # tedavi bilgisi
            treatment = fetch_treatment_from_firestore(keyword)

            diseases_info.append({
                "name": disease_display_name,
                "name_tr": disease_name_tr,
                "treatment_tr": treatment["treatment_tr"],
                "treatment_en": treatment["treatment_en"],
            })

        # geçmişe kaydet (app.py'deki analizi_kaydet ile aynı iş)
        if username:
            save_analysis_to_history(
                username=username,
                lang=lang,
                plant_types=plant_types,
                plant_types_tr=plant_types_tr,
                diseases_info=diseases_info,
                detected_classes=detected_classes,
                confidence_scores=confidence_scores,
            )

        # cevabı hazırla
        response = {
            "success": True,
            "detections": detections,
            # mobil bunu okuyor, data:image/jpeg;base64,... şeklinde tam URI
            "image_base64": result_image_b64,
            # eski isim de dursun, silince mobilde patlamıştı
            "result_image_base64": result_image_b64,
            "summary": {
                "plant_types": plant_types,
                "plant_types_tr": plant_types_tr,
                "is_healthy": is_healthy,
                "disease_count": len(disease_keywords_found),
                "risk_score": risk_score,
                "diseases": diseases_info,
            },
        }
        return response

    except Exception as e:
        print(f"[HATA] Analiz sırasında hata oluştu: {e}")
        return {
            "success": False,
            "error": f"Analiz sırasında bir hata oluştu: {str(e)}",
        }


# ---------- çalıştır ----------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
