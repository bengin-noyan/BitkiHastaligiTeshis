# -*- coding: utf-8 -*-
"""
Bitki Hastalığı Teşhis - FastAPI Backend Sunucusu
==================================================
YOLOv8 modeli ile bitki hastalığı tespiti yapan REST API sunucusu.
Firebase Firestore'dan tedavi bilgileri, SQLite'dan kullanıcı doğrulama sağlar.
"""

import base64
import io
import os
import sqlite3
from typing import Optional

import firebase_admin
import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, firestore
from PIL import Image
from pydantic import BaseModel
from ultralytics import YOLO

# ──────────────────────────────────────────────
# Uygulama yapılandırması
# ──────────────────────────────────────────────

# Proje kök dizini (bu dosyanın bulunduğu klasör)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Model ve veritabanı dosya yolları
MODEL_PATH = os.path.join(BASE_DIR, "plantdoc_150epoch.pt")
FIREBASE_KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")
SQLITE_DB_PATH = os.path.join(BASE_DIR, "tarimsal_analiz.db")

# Hastalık anahtar kelimeleri — sınıf adlarında bunlar aranır
DISEASE_KEYWORDS = [
    "scab", "rust", "mold", "virus", "spot",
    "blight", "curl", "rot", "mildew", "scorch",
]

# İngilizce → Türkçe sınıf adı sözlüğü
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
}

# ──────────────────────────────────────────────
# FastAPI uygulaması oluşturma
# ──────────────────────────────────────────────

app = FastAPI(
    title="Bitki Hastalığı Teşhis API",
    description="YOLOv8 tabanlı bitki hastalığı tespit servisi",
    version="1.0.0",
)

# Geliştirme ortamı için CORS — tüm kaynaklara izin ver
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# Global değişkenler (başlangıçta yüklenir)
# ──────────────────────────────────────────────

model: Optional[YOLO] = None  # YOLOv8 modeli
db_firestore = None            # Firestore istemcisi


# ──────────────────────────────────────────────
# Başlangıç olayı — model ve bağlantıları yükle
# ──────────────────────────────────────────────

@app.on_event("startup")
def startup_event():
    """Sunucu başlarken modeli ve Firebase bağlantısını hazırla."""
    global model, db_firestore

    # --- YOLOv8 Modelini Yükle ---
    if not os.path.exists(MODEL_PATH):
        print(f"[UYARI] Model dosyası bulunamadı: {MODEL_PATH}")
    else:
        model = YOLO(MODEL_PATH)
        print(f"[BİLGİ] YOLOv8 modeli yüklendi: {MODEL_PATH}")

    # --- Firebase Admin SDK Başlat ---
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


# ──────────────────────────────────────────────
# Pydantic modelleri
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Giriş isteği için veri modeli."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Giriş yanıtı için veri modeli."""
    success: bool
    username: str = ""


# ──────────────────────────────────────────────
# Yardımcı fonksiyonlar
# ──────────────────────────────────────────────

def get_sqlite_connection() -> sqlite3.Connection:
    """SQLite veritabanına bağlantı aç ve döndür."""
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def translate_class_name(class_name: str) -> str:
    """
    İngilizce sınıf adını Türkçeye çevir.
    Örnek: 'Tomato leaf bacterial spot' → 'Domates Yaprağı Bakteriyel Lekesi'
    """
    words = class_name.lower().replace("_", " ").split()
    translated_words = [CLASS_TR.get(w, w.capitalize()) for w in words]
    return " ".join(translated_words)


def extract_disease_keyword(class_name: str) -> Optional[str]:
    """
    Sınıf adından hastalık anahtar kelimesini çıkar.
    Örnek: 'Tomato leaf bacterial spot' → 'spot'
    """
    lower_name = class_name.lower()
    for keyword in DISEASE_KEYWORDS:
        if keyword in lower_name:
            return keyword
    return None


def fetch_treatment_from_firestore(disease_keyword: str) -> dict:
    """
    Firestore'dan hastalık tedavi bilgilerini getir.
    Her hastalık belgesi TR ve EN dil verisi içerir.
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

            # Türkçe tedavi bilgileri
            tr_data = data.get("TR", {})
            treatment_tr = {
                "ilac": tr_data.get("ilac", ""),
                "sonuc": tr_data.get("sonuc", ""),
                "ekonomi": tr_data.get("ekonomi", ""),
            }

            # İngilizce tedavi bilgileri
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


# ──────────────────────────────────────────────
# POST /login — Kullanıcı girişi
# ──────────────────────────────────────────────

@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    SQLite veritabanından kullanıcı adı ve şifre doğrulaması yapar.
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


# ──────────────────────────────────────────────
# POST /analyze — Görüntü analizi
# ──────────────────────────────────────────────

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(..., description="Analiz edilecek bitki görseli"),
    confidence: float = Form(0.25, description="Minimum güven eşiği (0-1)"),
):
    """
    Yüklenen bitki görselini YOLOv8 modeli ile analiz eder.
    Tespit edilen hastalıklar için Firestore'dan tedavi önerileri getirir.
    """
    # Model yüklü mü kontrol et
    if model is None:
        return {"success": False, "error": "Model yüklenemedi. Sunucu yapılandırmasını kontrol edin."}

    try:
        # --- Görseli oku ve PIL Image'a dönüştür ---
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # --- YOLOv8 ile tahmin yap ---
        results = model.predict(source=image, conf=confidence, imgsz=800)

        # --- Tespit edilen sınıfları ve güven skorlarını al ---
        detected_classes = [model.names[int(c)] for c in results[0].boxes.cls]
        confidence_scores = [float(c) for c in results[0].boxes.conf]

        # --- İşaretlenmiş görseli base64'e dönüştür ---
        annotated_bgr = results[0].plot()
        annotated_rgb = annotated_bgr[:, :, ::-1]  # BGR → RGB
        annotated_image = Image.fromarray(annotated_rgb)

        buffer = io.BytesIO()
        annotated_image.save(buffer, format="JPEG", quality=90)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        result_image_b64 = f"data:image/jpeg;base64,{image_base64}"

        # --- Tespit listesini oluştur ---
        detections = []
        for cls_name, conf_score in zip(detected_classes, confidence_scores):
            detections.append({
                "class_name": cls_name,
                "class_name_tr": translate_class_name(cls_name),
                "confidence": round(conf_score, 4),
            })

        # --- Bitki türlerini belirle (sınıf adının ilk kelimesi) ---
        plant_types = list({
            cls.split()[0] for cls in detected_classes if cls.split()
        })
        plant_types_tr = [CLASS_TR.get(p.lower(), p) for p in plant_types]

        # --- Hastalıkları tespit et ---
        sick_detections = []   # Hastalık içeren tespitler
        disease_keywords_found = set()

        for cls_name, conf_score in zip(detected_classes, confidence_scores):
            keyword = extract_disease_keyword(cls_name)
            if keyword:
                sick_detections.append(conf_score)
                disease_keywords_found.add(keyword)

        # --- Sağlıklı mı kontrol et ---
        is_healthy = len(sick_detections) == 0

        # --- Risk skoru hesapla ---
        if sick_detections:
            avg_conf = sum(sick_detections) / len(sick_detections)
            risk_score = min(int(len(sick_detections) * 15 * avg_conf) + 20, 95)
        else:
            risk_score = 0

        # --- Her benzersiz hastalık için tedavi bilgisi getir ---
        diseases_info = []
        for keyword in sorted(disease_keywords_found):
            # Hastalık adını oluştur (keyword'ün geçtiği ilk sınıf adından)
            disease_display_name = keyword  # varsayılan
            for cls_name in detected_classes:
                if keyword in cls_name.lower():
                    # Sınıf adından bitki adını çıkar, geri kalanı hastalık adı
                    parts = cls_name.lower().split()
                    if len(parts) > 1:
                        # İlk kelime bitki adı, geri kalanı hastalık
                        disease_display_name = " ".join(parts[1:])
                    break

            # Türkçe hastalık adı
            disease_name_tr = translate_class_name(disease_display_name)

            # Firestore'dan tedavi bilgilerini getir
            treatment = fetch_treatment_from_firestore(keyword)

            diseases_info.append({
                "name": disease_display_name,
                "name_tr": disease_name_tr,
                "treatment_tr": treatment["treatment_tr"],
                "treatment_en": treatment["treatment_en"],
            })

        # --- Yanıt oluştur ---
        response = {
            "success": True,
            "detections": detections,
            # Mobil uygulamanın kullandığı anahtar — kutucuklu (bounding box)
            # işaretlenmiş görselin tam data URI'si (data:image/jpeg;base64,...)
            "image_base64": result_image_b64,
            # Geriye dönük uyumluluk için mevcut anahtar korunuyor
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


# ──────────────────────────────────────────────
# Sunucu başlatma
# ──────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
