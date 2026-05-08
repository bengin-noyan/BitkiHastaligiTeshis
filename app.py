import sqlite3
from datetime import datetime
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# ─── SQL VERİTABANI BAĞLANTISI VE KURULUMU ──────────────────
conn = sqlite3.connect('tarimsal_analiz.db', check_same_thread=False)
c = conn.cursor()

def veritabani_kurulumu():
    # 1. Kullanıcılar Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            sifre TEXT,
            kayit_tarihi TEXT
        )
    ''')
    
    # 2. Analiz Geçmişi Tablosu
    c.execute('''
        CREATE TABLE IF NOT EXISTS analiz_gecmisi (
            islem_id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT,
            bitki_turu TEXT,
            hastalik_durumu TEXT,
            guven_skoru REAL,
            tarih TEXT
        )
    ''')
    
    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''
        INSERT OR IGNORE INTO kullanicilar (kullanici_adi, sifre, kayit_tarihi) 
        VALUES ('admin', 'ybs2026', ?)
    ''', (su_an,))
    conn.commit()

# --- ANALİZ KAYIT FONKSİYONU ---
def analizi_kaydet(kullanici, bitki, hastalik, skor):
    try:
        conn_kayit = sqlite3.connect('tarimsal_analiz.db', check_same_thread=False)
        c_kayit = conn_kayit.cursor()
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c_kayit.execute('''
            INSERT INTO analiz_gecmisi (kullanici_adi, bitki_turu, hastalik_durumu, guven_skoru, tarih)
            VALUES (?, ?, ?, ?, ?)
        ''', (kullanici, bitki, hastalik, skor, tarih))
        conn_kayit.commit()
        conn_kayit.close()
    except Exception as e:
        print(f"SQL Kayıt Hatası: {e}")

veritabani_kurulumu()
# ────────────────────────────────────────────────────────────

st.set_page_config(page_title="Tarımsal Analiz Sistemi", page_icon="🌿", layout="wide")

# ══════════════════════════════════════════════════════════
#  GLOBAL CSS — Minimalist tek renk tema (Senin Tasarımın)
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ===== GENEL SIFIRLA ===== */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }

/* ===== KÖK DEĞİŞKENLER — Sade tek renk paleti ===== */
:root {
    --primary:        #7DA78C;
    --primary-dark:   #6A937A;
    --primary-soft:   #f0f5f2;
    --primary-border: #c5dccd;
    --primary-text:   #4a6e57;
    
    --amber:          #d97706;
    --amber-soft:     #fffbeb;
    --red:            #dc2626;
    --red-soft:       #fef2f2;
    
    --text-dark:      #0f172a;
    --text-mid:       #334155;
    --text-soft:      #64748b;
    --text-muted:     #94a3b8;
    --bg-page:        #fafafa;
    --bg-card:        #ffffff;
    --border:         #e5e7eb;
    --border-soft:    #f3f4f6;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-dark);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp { background: var(--bg-page) !important; }

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: 
        radial-gradient(ellipse 900px 500px at 0% 0%, rgba(125,167,140,0.04), transparent),
        radial-gradient(ellipse 700px 400px at 100% 100%, rgba(125,167,140,0.03), transparent);
    pointer-events: none;
    z-index: 0;
}

.main .block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}

.stApp p, .stApp span, .stApp div, .stApp li, .stApp label,
.stApp small, .stApp strong, .stApp em, .stApp a { color: var(--text-mid); }

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 { 
    color: var(--text-dark) !important; 
    letter-spacing: -0.02em;
}
.stApp .stMarkdown p     { color: var(--text-mid) !important; }
.stApp .stMarkdown strong { color: var(--text-dark) !important; }

[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px 22px !important;
    transition: all 0.2s ease;
    box-shadow: none;
}
[data-testid="stMetric"]:hover {
    border-color: var(--primary-border) !important;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(125,167,140,0.08);
}
[data-testid="stMetric"] * { color: var(--text-mid) !important; }
[data-testid="stMetricLabel"] { 
    color: var(--text-muted) !important; 
    font-weight: 600 !important; 
    font-size: 0.7rem !important; 
    letter-spacing: 0.1em; 
    text-transform: uppercase; 
}
[data-testid="stMetricValue"] { 
    color: var(--text-dark) !important; 
    font-weight: 800 !important; 
    font-size: 1.85rem !important;
    letter-spacing: -0.03em;
}
[data-testid="stMetricDelta"] { font-weight: 600 !important; font-size: 0.78rem !important; }

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *, .stCaption, figcaption { 
    color: var(--text-muted) !important; font-size: 0.78rem !important; text-align: center; 
}

[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden;
    box-shadow: none;
    transition: all 0.2s ease;
}
[data-testid="stExpander"]:hover { border-color: var(--primary-border) !important; }
[data-testid="stExpander"] details summary {
    padding: 16px 20px !important;
    background: var(--border-soft);
    font-weight: 600 !important;
}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--text-dark) !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 18px 20px !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] * { color: var(--text-mid) !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] strong { color: var(--text-dark) !important; }

[data-testid="stAlert"] { 
    border-radius: 10px !important; 
    border-left-width: 3px !important;
    padding: 12px 16px !important;
    box-shadow: none !important;
}
[data-testid="stAlert"] * { color: var(--text-mid) !important; }
[data-testid="stNotificationContentSuccess"] * { color: var(--primary-text) !important; }
[data-testid="stNotificationContentInfo"] * { color: #1e40af !important; }
[data-testid="stNotificationContentWarning"] * { color: #92400e !important; }
[data-testid="stNotificationContentError"] * { color: #991b1b !important; }

[data-testid="stHeadingWithActionElements"] * { color: var(--text-dark) !important; font-weight: 700 !important; }

.stSlider label { color: var(--text-soft) !important; font-size: 0.85rem !important; font-weight: 500 !important; }
.stSlider [data-testid="stThumbValue"] { color: var(--primary) !important; font-weight: 700 !important; }
.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] { color: var(--text-muted) !important; }

.stRadio > label { color: var(--text-soft) !important; }
.stRadio [role="radiogroup"] label { color: var(--text-soft) !important; }

[data-testid="stFileUploader"] label { color: var(--text-soft) !important; font-weight: 500 !important; }
[data-testid="stFileUploadDropzone"] * { color: var(--text-soft) !important; }
[data-testid="stFileUploader"] section * { color: var(--text-soft) !important; }

.stSpinner > div { border-top-color: var(--primary) !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: none;
}
section[data-testid="stSidebar"]::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--primary);
}
section[data-testid="stSidebar"], section[data-testid="stSidebar"] * { color: var(--text-mid) !important; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] strong { color: var(--text-dark) !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border-soft) !important; margin: 1rem 0 !important; }

section[data-testid="stSidebar"] [role="radiogroup"] label {
    background: #f8fafc !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
    padding: 5px 14px !important; color: var(--text-soft) !important; transition: all 0.2s ease !important; font-weight: 500 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: var(--primary-soft) !important; border-color: var(--primary-border) !important; color: var(--primary-text) !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"], section[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] {
    background: var(--primary-soft) !important; border-color: var(--primary) !important; color: var(--primary-text) !important; font-weight: 600 !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: var(--primary-soft); border: 1.5px dashed var(--primary-border) !important; border-radius: 10px !important;
    padding: 10px !important; transition: all 0.2s ease;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"]:hover { border-color: var(--primary) !important; }

.stButton { width: 100% !important; }
.stButton > button {
    width: 100% !important; border-radius: 10px !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important; border: 1px solid transparent !important; font-size: 0.9rem !important;
    padding: 0.7rem 1.4rem !important; letter-spacing: 0.01em; box-shadow: none !important;
}

.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--primary) !important; color: #ffffff !important; border: 1px solid var(--primary) !important;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: var(--primary-dark) !important; border-color: var(--primary-dark) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(125,167,140,0.20) !important;
}
.stButton > button[kind="primary"] *, .stButton > button[data-testid="stBaseButton-primary"] * { color: #ffffff !important; }
.stButton > button[kind="primary"]:active { transform: translateY(0) !important; }

.stButton > button[kind="secondary"], .stButton > button[data-testid="stBaseButton-secondary"] {
    background: #ffffff !important; color: var(--text-mid) !important; border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"] * { color: var(--text-mid) !important; }
.stButton > button[kind="secondary"]:hover { background: var(--border-soft) !important; border-color: var(--text-muted) !important; }

section[data-testid="stSidebar"] .stButton > button { background: #ffffff !important; color: var(--red) !important; border: 1px solid #fecaca !important; }
section[data-testid="stSidebar"] .stButton > button * { color: var(--red) !important; }
section[data-testid="stSidebar"] .stButton > button:hover { background: var(--red-soft) !important; border-color: #fca5a5 !important; }

.stApp img { border-radius: 12px !important; border: 1px solid var(--border) !important; box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important; transition: all 0.25s ease !important; }
.stApp img:hover { box-shadow: 0 6px 18px rgba(125,167,140,0.08) !important; }

.stTextInput { width: 100% !important; }

/* Wrapper container — owns the border + radius (single layer, no overlap) */
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
}
.stTextInput [data-baseweb="input"]:focus-within,
.stTextInput [data-baseweb="base-input"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(125,167,140,0.15) !important;
}

/* Input itself — transparent, no border, no radius (avoids the double corner) */
.stTextInput input {
    width: 100% !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: var(--text-dark) !important;
    padding: 0.7rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    box-shadow: none !important;
    height: auto !important;
    outline: none !important;
}
.stTextInput input:focus { box-shadow: none !important; border: none !important; }
.stTextInput input::placeholder { color: var(--text-muted) !important; }
.stTextInput label { color: var(--text-soft) !important; font-weight: 500 !important; font-size: 0.85rem !important; }

/* Password visibility (eye) button — match the input background, remove dark fill */
.stTextInput button,
.stTextInput [data-baseweb="input"] button,
.stTextInput [data-testid="stTextInputRootElement"] button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-muted) !important;
    margin-right: 4px !important;
}
.stTextInput button:hover,
.stTextInput [data-baseweb="input"] button:hover,
.stTextInput [data-testid="stTextInputRootElement"] button:hover {
    background: transparent !important;
    background-color: transparent !important;
    color: var(--text-mid) !important;
}
.stTextInput button svg { fill: currentColor !important; }

.stApp hr { border-color: var(--border-soft) !important; margin: 2rem 0 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--border-soft); }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

@keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to   { opacity: 1; transform: translateY(0); } }
.stApp [data-testid="stVerticalBlock"] > div { animation: fadeInUp 0.35s ease-out; }
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE BAĞLANTISI ────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

@st.cache_resource
def load_model():
    return YOLO("plantdoc_150epoch.pt")
model = load_model()

# ─── DİL AYARLARI ────────────────────────────────────────────
LANGS = {
    "Türkçe": {
        "sidebar_title": "Kontrol Paneli",
        "sidebar_info":  "YBS Bitirme Projesi · 2026",
        "conf_label":    "Yapay Zekâ Güven Skoru",
        "upload_label":  "Yaprak Fotoğrafı Yükle",
        "main_title":    "Tarımsal Analiz Sistemi",
        "main_desc":     "Yapay zekâ destekli anlık bitki hastalığı teşhisi ve tarımsal verim analizi platformu.",
        "info_upload":   "Analize başlamak için sol menüden bir görsel yükleyin.",
        "col1_sub":      "Görsel Analiz",
        "img_cap_orig":  "Yüklenen Görsel",
        "analyze_btn":   "Analizi Başlat",
        "spinner":       "Görsel inceleniyor...",
        "img_cap_res":   "Teşhis Sonucu",
        "col2_sub":      "Verimlilik Raporu",
        "plant_label":   "Analiz Edilen Bitki",
        "no_plant":      "Sistem bu görselde bir tarım ürünü tespit edemedi.",
        "risk_label":    "TAHMİNİ VERİM KAYBI RİSKİ",
        "waiting":       "Bekleniyor",
        "healthy":       "Tespit edilen **{}** yaprakları tamamen sağlıklı.",
        "disease":       "Görselde {} adet enfekte bölge tespit edildi.",
        "plan_title":    "### İlaçlama ve Eylem Planı",
        "exp_title":     "{} İçin Mücadele Raporu",
        "lbl_ilac":      "Önerilen İlaç",
        "lbl_sonuc":     "Zirai Beklenti",
        "lbl_ekonomi":   "Finansal Etki",
        "db_err":        "Bulut bağlantı hatası.",
        "step1":         "Görsel Yükle",
        "step1d":        "JPG veya PNG formatında yaprak fotoğrafı yükleyin.",
        "step2":         "Yapay Zekâ Analizi",
        "step2d":        "YOLOv8 modelimiz görseli gerçek zamanlı tarar.",
        "step3":         "Rapor Al",
        "step3d":        "Teşhis sonuçlarını ve ilaçlama önerilerini görüntüleyin.",
        "ready":         "Analize Hazır",
        "how":           "Nasıl Çalışır?",
        "feature_title": "Akıllı Tarım Teknolojisi",
        "feature_desc":  "Üretici dostu, yüksek doğruluklu, hızlı analiz sunan bir teşhis sistemi.",
    },
    "English": {
        "sidebar_title": "Control Panel",
        "sidebar_info":  "MIS Graduation Project · 2026",
        "conf_label":    "AI Confidence Score",
        "upload_label":  "Upload Leaf Photo",
        "main_title":    "Agricultural Analysis System",
        "main_desc":     "AI-powered instant plant disease diagnosis and agricultural productivity analysis platform.",
        "info_upload":   "Upload an image from the sidebar to begin.",
        "col1_sub":      "Visual Analysis",
        "img_cap_orig":  "Uploaded Image",
        "analyze_btn":   "Start Analysis",
        "spinner":       "Analyzing image...",
        "img_cap_res":   "Diagnosis Result",
        "col2_sub":      "Productivity Report",
        "plant_label":   "Analyzed Plant",
        "no_plant":      "No agricultural product detected in this image.",
        "risk_label":    "YIELD LOSS RISK",
        "waiting":       "Waiting",
        "healthy":       "**{}** leaves are perfectly healthy.",
        "disease":       "{} infected areas detected.",
        "plan_title":    "### Action Plan",
        "exp_title":     "Treatment Report for {}",
        "lbl_ilac":      "Prescribed Medicine",
        "lbl_sonuc":     "Agronomic Expectation",
        "lbl_ekonomi":   "Financial Impact",
        "db_err":        "Cloud connection error.",
        "step1":         "Upload Image",
        "step1d":        "Upload a leaf photo in JPG or PNG format.",
        "step2":         "AI Analysis",
        "step2d":        "Our YOLOv8 model scans the image in real time.",
        "step3":         "Get Report",
        "step3d":        "View diagnosis results and treatment recommendations.",
        "ready":         "Ready for Analysis",
        "how":           "How It Works",
        "feature_title": "Smart Agriculture Technology",
        "feature_desc":  "A farmer-friendly, high-accuracy, fast-analysis diagnostic system.",
    },
}

CLASS_TR = {
    "apple":"Elma","tomato":"Domates","grape":"Üzüm","corn":"Mısır","potato":"Patates",
    "cherry":"Kiraz","strawberry":"Çilek","bell_pepper":"Dolmalık Biber","pepper":"Biber",
    "peach":"Şeftali","squash":"Kabak","soybean":"Soya Fasulyesi","raspberry":"Ahududu",
    "healthy":"Sağlıklı","leaf":"Yaprağı","leaves":"Yaprakları",
    "scab":"Karaleke","rust":"Pas","virus":"Virüs","blight":"Yanıklık",
    "spot":"Leke","spots":"Lekeleri","mold":"Küf","mildew":"Külleme",
    "rot":"Çürüklük","early":"Erken","late":"Geç","black":"Siyah",
    "bacterial":"Bakteriyel","mosaic":"Mozaik","powdery":"Külleme",
}

# ══════════════════════════════════════════════════════════
#  GİRİŞ SAYFASI — Minimalist tasarım
# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
#  GİRİŞ SAYFASI — Minimalist tasarım
# ══════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════
#  GİRİŞ SAYFASI — Minimalist tasarım
# ══════════════════════════════════════════════════════════
def login_page():
    st.markdown("""
    <style>
    .lp-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 6px 16px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 100px;
        font-size: 0.76rem;
        color: #475569 !important;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .lp-badge-dot { width: 6px; height: 6px; background: #7DA78C; border-radius: 50%; }
    .lp-card {
        background: #ffffff; border: 1px solid #e5e7eb; border-radius: 16px;
        padding: 40px 36px 28px 36px; box-shadow: 0 1px 3px rgba(15,23,42,0.04);
        animation: cardIn 0.45s cubic-bezier(0.34,1.56,0.64,1); text-align: center; position: relative;
    }
    @keyframes cardIn { from { opacity: 0; transform: translateY(16px); } to   { opacity: 1; transform: translateY(0); } }
    .lp-icon {
        width: 64px; height: 64px; margin: 0 auto 20px auto; background: #ecfdf5; border: 1px solid #a7f3d0;
        border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 30px;
    }
    .lp-title { font-size: 1.55rem; font-weight: 800; color: #0f172a !important; margin: 0 0 8px 0; letter-spacing: -0.03em; }
    .lp-sub { font-size: 0.92rem; color: #64748b !important; margin: 0; font-weight: 400; line-height: 1.55; }
    .lp-stats { display: flex; justify-content: center; gap: 8px; margin: 24px 0 4px 0; flex-wrap: wrap; }
    .lp-pill {
        padding: 5px 12px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 100px;
        font-size: 0.74rem; color: #64748b !important; font-weight: 500;
    }
    .lp-pill b { color: #0f172a !important; font-weight: 700; }
    .lp-footer-note { margin-top: 28px; font-size: 0.76rem; color: #94a3b8 !important; text-align: center; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown(
            '<div style="text-align:center;padding:40px 0 20px 0;">'
            '<span class="lp-badge"><span class="lp-badge-dot"></span> Pamukkale Üniversitesi · YBS Bitirme Projesi</span>'
            '</div>',
            unsafe_allow_html=True
        )

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
        <div class="lp-card">
            <div class="lp-icon">🌿</div>
            <div class="lp-title">Tarımsal Analiz Sistemi</div>
            <div class="lp-sub">Yapay zekâ destekli bitki hastalığı teşhisi<br>
            ve tarımsal verim analizi platformu</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")

        # ─── SEKMELER (TABS) BAŞLANGICI ───
        tab_giris, tab_kayit = st.tabs(["Giriş Yap", "Kayıt Ol"])

        # 1. GİRİŞ SEKME İÇERİĞİ
        with tab_giris:
            username = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı girin", key="login_user")
            password = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin", key="login_pass")
            st.write("")
            
            if st.button("Giriş Yap", use_container_width=True, type="primary", key="btn_login"):
                kullanici_adi_girilen = username.strip().lower()
                sifre_girilen = password.strip()

                conn = sqlite3.connect('tarimsal_analiz.db', check_same_thread=False)
                c = conn.cursor()
                c.execute("SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?", (kullanici_adi_girilen, sifre_girilen))
                kullanici_var_mi = c.fetchone()
                conn.close()

                if kullanici_var_mi:
                    st.session_state.logged_in = True
                    st.session_state.aktif_kullanici = kullanici_adi_girilen
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

        # 2. KAYIT SEKME İÇERİĞİ
        with tab_kayit:
            new_user = st.text_input("Yeni Kullanıcı Adı", placeholder="Bir kullanıcı adı belirleyin", key="reg_user")
            new_pass = st.text_input("Yeni Şifre", type="password", placeholder="Bir şifre belirleyin", key="reg_pass")
            new_pass2 = st.text_input("Şifre Doğrulama", type="password", placeholder="Şifrenizi tekrar girin", key="reg_pass2")
            st.write("")

            if st.button("Kayıt Ol", use_container_width=True, type="primary", key="btn_register"):
                if not new_user or not new_pass:
                    st.warning("Lütfen tüm alanları doldurun.")
                elif new_pass != new_pass2:
                    st.error("Şifreler uyuşmuyor, lütfen kontrol edin!")
                else:
                    try:
                        conn = sqlite3.connect('tarimsal_analiz.db', check_same_thread=False)
                        c = conn.cursor()
                        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        c.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, kayit_tarihi) VALUES (?, ?, ?)", 
                                  (new_user.strip().lower(), new_pass.strip(), su_an))
                        conn.commit()
                        conn.close()
                        st.success(f"Harika! {new_user} başarıyla kaydedildi. 'Sisteme Giriş' sekmesinden giriş yapabilirsin.")
                    except sqlite3.IntegrityError:
                        st.error("Bu kullanıcı adı zaten alınmış. Lütfen farklı bir ad deneyin.")

        # ─── ALT İSTATİSTİKLER ───
        st.markdown("""
        <div class="lp-stats">
            <span class="lp-pill"><b>%94+</b> Doğruluk</span>
            <span class="lp-pill"><b>&lt;2sn</b> Analiz</span>
            <span class="lp-pill"><b>38</b> Hastalık Sınıfı</span>
        </div>
        <div class="lp-footer-note">
            © 2026 · Tarımsal Analiz Sistemi · Tüm hakları saklıdır
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  ANA UYGULAMA
# ══════════════════════════════════════════════════════════
def main_app():
    # ── SIDEBAR ──────────────────────────────────────────
    st.sidebar.markdown("""
    <div style="padding:14px 0 18px 0;text-align:center;">
        <div style="
            width:48px;height:48px;
            background:#ecfdf5;
            border:1px solid #a7f3d0;
            border-radius:12px;
            display:flex;align-items:center;justify-content:center;
            font-size:24px;
            margin:0 auto 12px auto;
        ">🌿</div>
        <div style="color:#0f172a;font-size:0.95rem;font-weight:800;letter-spacing:-0.02em;">
            Tarımsal Analiz
        </div>
        <div style="color:#94a3b8;font-size:0.68rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;">
            AI DESTEKLİ SİSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;
        border-radius:8px;padding:8px 14px;margin-bottom:8px;text-align:center;">
        <span style="color:#475569 !important;font-size:0.78rem;font-weight:600;">
            🌐 Dil / Language
        </span>
    </div>
    """, unsafe_allow_html=True)
    lang = st.sidebar.radio("Seçim / Select", ("Türkçe", "English"), horizontal=True, label_visibility="collapsed")
    T = LANGS[lang]

    st.sidebar.divider()

    st.sidebar.markdown(f"""
    <div style="margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:1rem;">⚙️</span>
            <span style="color:#0f172a;font-size:0.98rem;font-weight:700;letter-spacing:-0.01em;">
                {T['sidebar_title']}
            </span>
        </div>
        <div style="color:#94a3b8;font-size:0.74rem;margin-top:2px;font-weight:500;">
            {T['sidebar_info']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.write("")

    conf = st.sidebar.slider(T["conf_label"], min_value=0.10, max_value=1.00, value=0.25, step=0.05)
    st.sidebar.write("")
    uploaded = st.sidebar.file_uploader(T["upload_label"], type=["jpg", "jpeg", "png"], key="img_upload")
    st.sidebar.divider()

    if st.sidebar.button("Çıkış Yap", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown("""
    <div style="text-align:center;margin-top:24px;">
        <span style="background:#f9fafb;
            border:1px solid #e5e7eb;border-radius:100px;
            padding:4px 14px;font-size:0.7rem;
            color:#64748b !important;font-weight:600;letter-spacing:0.04em;">
            v2.0 · YBS 2026
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── ÜST NAVİGASYON BAR ──────────────────────────────
    st.markdown(f"""
    <div style="
        display:flex;align-items:center;justify-content:space-between;
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:12px 20px;
        margin-bottom:20px;
    ">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="
                width:36px;height:36px;
                background:#ecfdf5;
                border:1px solid #a7f3d0;
                border-radius:10px;
                display:flex;align-items:center;justify-content:center;
                font-size:18px;
            ">🌿</div>
            <div>
                <div style="font-size:0.92rem;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">
                    Tarımsal Analiz
                </div>
                <div style="font-size:0.7rem;color:#94a3b8;font-weight:500;">
                    AI Destekli Sistem
                </div>
            </div>
        </div>
        <div>
            <span style="
                display:inline-flex;align-items:center;gap:6px;
                background:#ecfdf5;border:1px solid #a7f3d0;
                color:#065f46 !important;
                border-radius:100px;padding:4px 12px;
                font-size:0.7rem;font-weight:600;letter-spacing:0.06em;
            ">
                <span style="width:6px;height:6px;background:#7DA78C;border-radius:50%;"></span>
                CANLI
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── HERO BANNER — Minimalist ────────────────────────
    st.markdown(f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:16px;
        padding:32px 36px;
        margin-bottom:24px;
    ">
        <div style="
            display:inline-flex;align-items:center;gap:8px;
            background:#ecfdf5;
            border:1px solid #a7f3d0;
            border-radius:100px;
            padding:4px 12px;
            font-size:0.7rem;
            color:#065f46 !important;
            font-weight:600;
            letter-spacing:0.06em;
            margin-bottom:14px;
        ">
            YAPAY ZEKÂ DESTEKLİ
        </div>
        <h1 style="
            margin:0 0 10px 0;
            font-size:2rem;
            font-weight:800;
            color:#0f172a !important;
            letter-spacing:-0.03em;
            line-height:1.2;
        ">
            {T['main_title']}
        </h1>
        <p style="
            margin:0;
            font-size:0.98rem;
            color:#64748b !important;
            font-weight:400;
            line-height:1.55;
            max-width:680px;
        ">
            {T['main_desc']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Model Doğruluğu",   "%94+",  "YOLOv8 Medium")
    with c2: st.metric("Analiz Süresi",     "<2 sn", "Gerçek zamanlı")
    with c3: st.metric("Hastalık Sınıfı",   "38",    "PlantDoc Dataset")
    with c4: st.metric("Desteklenen Bitki", "14",    "Tarım ürünleri")

    st.write("")
    st.write("")

    if uploaded is not None:
        if st.session_state.get("cur_img") != uploaded.name:
            st.session_state.analiz_ok = False
            st.session_state.cur_img   = uploaded.name

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader(f"🖼️ {T['col1_sub']}")
            img = Image.open(uploaded)
            st.image(img, caption=T["img_cap_orig"], use_container_width=True)
            st.write("")
            run_btn = st.button(T["analyze_btn"], use_container_width=True, type="primary")

        if run_btn:
            with col1, st.spinner(T["spinner"]):
                res = model.predict(source=img, conf=conf, imgsz=800)
                st.session_state.plot      = res[0].plot()[:, :, ::-1]
                st.session_state.classes   = [model.names[int(c)] for c in res[0].boxes.cls]
                st.session_state.confs     = [float(c) for c in res[0].boxes.conf]
                st.session_state.analiz_ok = True
                
                # ─── YENİ EKLENEN: SQL KAYIT İŞLEMİ ───
                try:
                    det_cls = st.session_state.classes
                    det_conf = st.session_state.confs
                    
                    plants = set([cn.split()[0] for cn in det_cls])
                    if plants:
                        bitki_turu = ", ".join(CLASS_TR.get(p.lower(), p) for p in plants) if lang == "Türkçe" else ", ".join(plants)
                    else:
                        bitki_turu = "Bilinmiyor"

                    dis_keys = ["scab", "rust", "mold", "virus", "spot", "blight", "curl", "rot", "mildew", "scorch"]
                    sick = [c for c in det_cls if any(k in c.lower() for k in dis_keys)]
                    
                    if not det_cls:
                        hastalik = "Tespit Edilemedi"
                    elif not sick:
                        hastalik = "Sağlıklı"
                    else:
                        if lang == "Türkçe":
                            hastalik = ", ".join(set([" ".join(CLASS_TR.get(w.lower(), w.capitalize()) for w in dis.replace("_", " ").split()) for dis in sick]))
                        else:
                            hastalik = ", ".join(set(sick))

                    skor = round(sum(det_conf)/len(det_conf), 2) if det_conf else 0.0
                    kullanici = st.session_state.get("aktif_kullanici", "Bilinmeyen Kullanıcı")

                    analizi_kaydet(kullanici, bitki_turu, hastalik, skor)
                    st.toast("✅ Analiz başarıyla veritabanına kaydedildi!", icon="💾")
                except Exception as e:
                    st.error(f"Kayıt Hatası: {e}")
                # ────────────────────────────────────────

        if st.session_state.get("analiz_ok"):
            with col1:
                st.image(st.session_state.plot, caption=T["img_cap_res"], use_container_width=True)

            with col2:
                st.subheader(f"📋 {T['col2_sub']}")
                det_cls  = st.session_state.classes
                det_conf = st.session_state.confs

                plants = set([cn.split()[0] for cn in det_cls])
                plant_str = ""
                if plants:
                    plant_str = ", ".join(CLASS_TR.get(p.lower(), p) for p in plants) if lang == "Türkçe" else ", ".join(plants)
                    st.info(f"{T['plant_label']}: **{plant_str}**")

                if not det_cls:
                    st.warning(T["no_plant"])
                    st.metric(T["risk_label"], "0%", T["waiting"], delta_color="off")
                else:
                    dis_keys = ["scab", "rust", "mold", "virus", "spot", "blight", "curl", "rot", "mildew", "scorch"]
                    sick = [c for c in det_cls if any(k in c.lower() for k in dis_keys)]

                    if not sick:
                        st.success(T["healthy"].format(plant_str or "Bitki"))
                        st.metric(T["risk_label"], "%0", "Stabil", delta_color="normal")
                    else:
                        st.warning(T["disease"].format(len(sick)))
                        avg_conf = sum(det_conf) / len(det_conf)
                        risk = min(int(len(sick) * 15 * avg_conf) + 20, 95)
                        st.metric(T["risk_label"], f"%{risk}", f"-{risk}% Potansiyel Kayıp", delta_color="inverse")
                        st.write("")
                        st.markdown(T["plan_title"])

                        for dis in set(sick):
                            h = dis.lower()
                            display = " ".join(CLASS_TR.get(w.lower(), w.capitalize()) for w in dis.replace("_", " ").split()) if lang == "Türkçe" else dis

                            db_key = "default"
                            for k in ["blight", "rust", "scab", "virus", "mold", "mildew", "spot", "rot", "scorch", "curl"]:
                                if k in h:
                                    db_key = ("blight" if k in ["mold", "mildew", "spot", "rot", "scorch"] else ("virus" if k == "curl" else k))
                                    break

                            lang_key = "TR" if lang == "Türkçe" else "EN"
                            try:
                                doc = db.collection("hastaliklar").document(db_key).get()
                                bilgi = doc.to_dict().get(lang_key, {}) if doc.exists else {}
                            except Exception:
                                bilgi = {}

                            fallback = { "ilac": T["db_err"], "sonuc": T["db_err"], "ekonomi": T["db_err"] }
                            bilgi = bilgi or fallback

                            with st.expander(T["exp_title"].format(display), expanded=True):
                                st.markdown(f"**{T['lbl_ilac']}:** {bilgi.get('ilac','')}")
                                st.markdown(f"**{T['lbl_sonuc']}:** {bilgi.get('sonuc','')}")
                                st.markdown(f"**{T['lbl_ekonomi']}:** {bilgi.get('ekonomi','')}")
    else:
        # ── BOŞ DURUM ────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:16px 24px 8px 24px;">
            <div style="
                width:72px;height:72px;
                margin:0 auto 20px auto;
                background:#ecfdf5;
                border:1px solid #a7f3d0;
                border-radius:18px;
                display:flex;align-items:center;justify-content:center;
                font-size:36px;
            ">📸</div>
            <h2 style="
                color:#0f172a !important;
                font-size:1.6rem !important;
                margin:0 0 10px 0;
                font-weight:800;
                letter-spacing:-0.03em;
            ">{T['ready']}</h2>
            <p style="
                color:#64748b;
                font-size:0.96rem;
                max-width:460px;
                margin:0 auto 12px auto;
                line-height:1.55;
            ">{T['info_upload']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="text-align:center;margin:32px 0 24px 0;">
            <div style="
                display:inline-flex;align-items:center;gap:8px;
                background:#ecfdf5;
                border:1px solid #a7f3d0;
                border-radius:100px;
                padding:5px 14px;
                font-size:0.7rem;
                color:#065f46 !important;
                font-weight:700;
                letter-spacing:0.08em;
                text-transform:uppercase;
            ">
                {T['how']}
            </div>
            <h3 style="
                color:#0f172a !important;
                font-size:1.6rem !important;
                margin:14px 0 6px 0;
                font-weight:800;
                letter-spacing:-0.02em;
            ">Üç adımda teşhis</h3>
            <p style="color:#64748b;font-size:0.94rem;margin:0;">
                Karmaşık değil — fotoğraf yükle, analiz et, raporu gör.
            </p>
        </div>
        """, unsafe_allow_html=True)

        CARD_BASE = (
            "background:#ffffff;"
            "border:1px solid #e5e7eb;"
            "border-radius:14px;"
            "padding:28px 24px;"
            "text-align:left;"
            "transition:all 0.2s ease;"
            "height:100%;"
        )

        p1, p2, p3 = st.columns(3, gap="medium")
        with p1:
            st.markdown(f"""
            <div style="{CARD_BASE}">
                <div style="
                    width:40px;height:40px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:10px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.95rem;font-weight:700;
                    color:#065f46;
                    margin-bottom:16px;
                ">01</div>
                <div style="
                    font-size:1rem;font-weight:700;
                    color:#0f172a;margin-bottom:8px;letter-spacing:-0.01em;
                ">{T['step1']}</div>
                <div style="
                    font-size:0.86rem;color:#64748b;line-height:1.6;
                ">{T['step1d']}</div>
            </div>""", unsafe_allow_html=True)

        with p2:
            st.markdown(f"""
            <div style="{CARD_BASE}">
                <div style="
                    width:40px;height:40px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:10px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.95rem;font-weight:700;
                    color:#065f46;
                    margin-bottom:16px;
                ">02</div>
                <div style="
                    font-size:1rem;font-weight:700;
                    color:#0f172a;margin-bottom:8px;letter-spacing:-0.01em;
                ">{T['step2']}</div>
                <div style="
                    font-size:0.86rem;color:#64748b;line-height:1.6;
                ">{T['step2d']}</div>
            </div>""", unsafe_allow_html=True)

        with p3:
            st.markdown(f"""
            <div style="{CARD_BASE}">
                <div style="
                    width:40px;height:40px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:10px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:0.95rem;font-weight:700;
                    color:#065f46;
                    margin-bottom:16px;
                ">03</div>
                <div style="
                    font-size:1rem;font-weight:700;
                    color:#0f172a;margin-bottom:8px;letter-spacing:-0.01em;
                ">{T['step3']}</div>
                <div style="
                    font-size:0.86rem;color:#64748b;line-height:1.6;
                ">{T['step3d']}</div>
            </div>""", unsafe_allow_html=True)

        # ── ÖZELLİKLER ───────────────────────────────────
        st.write("")
        st.write("")
        st.markdown(f"""
        <div style="text-align:center;margin:36px 0 24px 0;">
            <div style="
                display:inline-flex;align-items:center;gap:8px;
                background:#ecfdf5;
                border:1px solid #a7f3d0;
                border-radius:100px;
                padding:5px 14px;
                font-size:0.7rem;
                color:#065f46 !important;
                font-weight:700;
                letter-spacing:0.08em;
                text-transform:uppercase;
            ">
                ÖZELLİKLER
            </div>
            <h3 style="
                color:#0f172a !important;
                font-size:1.6rem !important;
                margin:14px 0 6px 0;
                font-weight:800;
                letter-spacing:-0.02em;
            ">{T['feature_title']}</h3>
            <p style="color:#64748b;font-size:0.94rem;margin:0;">
                {T['feature_desc']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        FEATURE_CARD = (
            "background:#ffffff;"
            "border:1px solid #e5e7eb;"
            "border-radius:14px;"
            "padding:24px 22px;"
            "transition:all 0.2s ease;"
            "height:100%;"
        )

        f1, f2, f3 = st.columns(3, gap="medium")
        with f1:
            st.markdown(f"""
            <div style="{FEATURE_CARD}">
                <div style="
                    width:36px;height:36px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:9px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:18px;
                    margin-bottom:14px;
                ">🎯</div>
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    Yüksek Doğruluk
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    YOLOv8 Medium modeli ile %94+ doğruluk oranı. PlantDoc veri seti üzerinde 150 epoch eğitildi.
                </div>
            </div>""", unsafe_allow_html=True)

        with f2:
            st.markdown(f"""
            <div style="{FEATURE_CARD}">
                <div style="
                    width:36px;height:36px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:9px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:18px;
                    margin-bottom:14px;
                ">⚡</div>
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    Hızlı Analiz
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    Görsel yüklendikten 2 saniyeden kısa sürede teşhis. Anlık geri bildirim ve raporlama.
                </div>
            </div>""", unsafe_allow_html=True)

        with f3:
            st.markdown(f"""
            <div style="{FEATURE_CARD}">
                <div style="
                    width:36px;height:36px;
                    background:#ecfdf5;
                    border:1px solid #a7f3d0;
                    border-radius:9px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:18px;
                    margin-bottom:14px;
                ">📊</div>
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    Akıllı Raporlama
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    Hastalık teşhisi sonrası ilaçlama önerisi, finansal etki ve zirai beklenti raporu.
                </div>
            </div>""", unsafe_allow_html=True)

        st.write("")
        st.write("")
        st.markdown("""
        <div style="
            text-align:center;
            padding:24px 0 8px 0;
            border-top:1px solid #e5e7eb;
            margin-top:24px;
        ">
            <p style="
                color:#94a3b8;
                font-size:0.8rem;
                margin:0;
                font-weight:500;
            ">
                © 2026 Tarımsal Analiz Sistemi · YBS Bitirme Projesi · Tüm hakları saklıdır
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  UYGULAMA YÖNLENDİRİCİ
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    login_page()
else:
    main_app()