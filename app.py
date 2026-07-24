import os
import base64
import threading
import sqlite3
from datetime import datetime
from typing import Any
import streamlit as st
from PIL import Image
# Ağır kütüphaneler (pandas, plotly, firebase) modül açılışında değil,
# yalnızca gerçekten gerektiğinde (analiz/geçmiş sayfalarında) import edilir —
# böylece login ekranı çok daha hızlı açılır.

# ─── GÖRSEL VARLIKLAR (logo / arka plan) ────────────────────
# assets/ klasöründeki görselleri base64 data-URI olarak, önbellekli döndürür;
# böylece HTML/CSS içine gömülebilir ve her rerun'da diskten okunmaz.
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

@st.cache_data(show_spinner=False)
def asset_data_uri(dosya_adi: str) -> str:
    yol = os.path.join(_ASSETS_DIR, dosya_adi)
    try:
        with open(yol, "rb") as f:
            veri = base64.b64encode(f.read()).decode("ascii")
        uzanti = os.path.splitext(dosya_adi)[1].lower().lstrip(".")
        mime = "jpeg" if uzanti in ("jpg", "jpeg") else uzanti
        return f"data:image/{mime};base64,{veri}"
    except Exception:
        return ""

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

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            margin-top: 0 !important;
        }
        header[data-testid="stHeader"] {
            background-color: rgba(0,0,0,0) !important;
            color: #0f172a !important;    
        header {visibility: hidden;} /* Streamlit'in üstteki görünmez header boşluğunu yok eder */
    </style>
    """, unsafe_allow_html=True)

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
/* Sağ üstteki "Deploy" butonu gizlenir (login + ana uygulama). Araç çubuğunun
   tamamını GİZLEME — sidebar aç/kapat düğmesi o bölgede yaşıyor. */
[data-testid="stAppDeployButton"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
/* Sidebar aç/kapat (collapse/expand) kontrolleri HER ZAMAN görünür kalsın */
[data-testid="stSidebarHeader"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    z-index: 1000000 !important;
}

/* ===== KÖK DEĞİŞKENLER — Sade tek renk paleti ===== */
:root {
    /* Canlı/parlak yeşil palet — eski sage (#7DA78C) yerine daha doygun yeşil */
    --primary:        #2FA85A;
    --primary-dark:   #248C49;
    --primary-soft:   #e7f7ee;
    --primary-border: #a6e2be;
    --primary-text:   #1e7d42;
    
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

[data-testid="stFileUploader"] label { color: var(--text-dark) !important; font-weight: 700 !important; }
[data-testid="stFileUploadDropzone"] * { color: var(--text-dark) !important; }
[data-testid="stFileUploader"] section * { color: var(--text-dark) !important; }

/* ── Ana sayfa görsel yükleyici — paletle uyumlu, yumuşak dropzone ─────── */
[data-testid="stFileUploader"] {
    background: linear-gradient(180deg, #ffffff 0%, var(--primary-soft) 100%) !important;
    border: 1.5px dashed var(--primary-border) !important;
    border-radius: 12px !important;
    padding: 10px !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    box-shadow: 0 4px 14px rgba(125,167,140,0.10);
}
[data-testid="stFileUploadDropzone"],
[data-testid="stFileUploader"] section,
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileUploaderDropzoneInstructions"] > div,
[data-testid="stFileUploadDropzoneInstructions"],
[data-testid="stFileUploadDropzoneInstructions"] > div {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploadDropzone"] {
    padding: 14px 16px !important;
}
/* "Drag and drop file here" ana metni — kalın ve okunabilir */
[data-testid="stFileUploaderDropzoneInstructions"] span,
[data-testid="stFileUploadDropzoneInstructions"] span,
[data-testid="stFileUploadDropzone"] > div > span,
[data-testid="stFileUploadDropzone"] section > span {
    color: var(--text-dark) !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: -0.01em;
}
/* "Limit 200MB per file" alt metni — okunabilir ama hafif silik */
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploadDropzoneInstructions"] small,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploadDropzone"] small {
    color: var(--text-mid) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
}
[data-testid="stFileUploadDropzone"] svg { color: var(--primary) !important; fill: var(--primary) !important; }

/* Browse files düğmesi — birincil yeşil */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploadDropzone"] button {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: 1px solid var(--primary) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 2px rgba(125,167,140,0.20) !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploadDropzone"] button:hover {
    background: var(--primary-dark) !important;
    border-color: var(--primary-dark) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(125,167,140,0.22) !important;
}
[data-testid="stFileUploader"] button *,
[data-testid="stFileUploadDropzone"] button * { color: #ffffff !important; }

/* Sidebar içindeki uploader bu kuralları override etmemeli — paneldeki stil ayrı kalır */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
    background: var(--primary) !important;
    color: #ffffff !important;
    border: 1px solid var(--primary) !important;
}

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

/* Form submit butonları (Giriş Yap / Kayıt Ol) — normal primary buton ile birebir aynı görünüm */
[data-testid="stFormSubmitButton"] { width: 100% !important; }
[data-testid="stFormSubmitButton"] button {
    width: 100% !important; border-radius: 10px !important; font-weight: 600 !important; font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important; font-size: 0.9rem !important; padding: 0.7rem 1.4rem !important; letter-spacing: 0.01em;
    background: var(--primary) !important; color: #ffffff !important; border: 1px solid var(--primary) !important; box-shadow: none !important;
}
[data-testid="stFormSubmitButton"] button * { color: #ffffff !important; }
[data-testid="stFormSubmitButton"] button:hover {
    background: var(--primary-dark) !important; border-color: var(--primary-dark) !important; transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(125,167,140,0.20) !important;
}
[data-testid="stFormSubmitButton"] button:active { transform: translateY(0) !important; }

.stApp img { border-radius: 12px !important; border: 1px solid var(--border) !important; box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important; transition: all 0.25s ease !important; }
.stApp img:hover { box-shadow: 0 6px 18px rgba(125,167,140,0.08) !important; }
/* Logo görselleri bu kuralın dışında — etraflarında kutu/kenarlık/gölge OLMASIN */
.stApp img.lp-logo,
section[data-testid="stSidebar"] img { border: none !important; border-radius: 0 !important; box-shadow: none !important; }
.stApp img.lp-logo:hover,
section[data-testid="stSidebar"] img:hover { box-shadow: none !important; }

.stTextInput { width: 100% !important; }

/* Wrapper container — flex layout so input + eye button sit side by side */
.stTextInput [data-baseweb="input"],
.stTextInput [data-baseweb="base-input"] {
    background: #ffffff !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    transition: all 0.2s ease !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: stretch !important;
}
.stTextInput [data-baseweb="input"]:focus-within,
.stTextInput [data-baseweb="base-input"]:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(125,167,140,0.15) !important;
}

/* Input itself — flex:1 leaves room for the eye button, no overlap */
.stTextInput input {
    flex: 1 1 auto !important;
    min-width: 0 !important;
    width: auto !important;
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    color: var(--text-dark) !important;
    caret-color: var(--text-dark) !important;
    padding: 0.7rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    box-shadow: none !important;
    height: auto !important;
    outline: none !important;
}
.stTextInput input:focus { box-shadow: none !important; border: none !important; caret-color: var(--text-dark) !important; }
.stTextInput input::placeholder { color: var(--text-muted) !important; }
.stTextInput label { color: var(--text-soft) !important; font-weight: 500 !important; font-size: 0.85rem !important; }

/* Password visibility (eye) button — fixed width, sits beside input, no overlap */
.stTextInput button,
.stTextInput [data-baseweb="input"] button,
.stTextInput [data-testid="stTextInputRootElement"] button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text-muted) !important;
    flex: 0 0 auto !important;
    width: 42px !important;
    min-width: 42px !important;
    padding: 0 10px !important;
    margin: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    align-self: stretch !important;
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
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE BAĞLANTISI (tembel: yalnızca ilk gerekli olduğunda başlatılır) ───
@st.cache_resource(show_spinner=False)
def get_db():
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    return firestore.client()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "lang" not in st.session_state:
    st.session_state.lang = "Türkçe"

@st.cache_resource(show_spinner=False)
def load_model():
    os.environ["YOLO_VERBOSE"] = "False"  # Ultralytics banner/log çıktısını kapat
    from ultralytics import YOLO
    m = YOLO("plantdoc_150epoch.pt")  # modelin yüklenmesi biraz zaman alır, bu yüzden cache'liyoruz
    # İlk gerçek analizdeki gecikmeyi önlemek için modeli boş bir görselle önceden ısıt
    try:
        m.predict(source=Image.new("RGB", (640, 640)), imgsz=640, verbose=False)
    except Exception:
        pass
    return m

def modeli_onyukle_arkaplan():
    """Kullanıcı login ekranında bilgilerini girerken modeli sessizce, arka planda
    yükler. Böylece giriş sonrası ilk analiz beklemesiz olur; login ekranı ise
    thread UI çizildikten sonra başlatıldığı için hızlı açılmaya devam eder."""
    if st.session_state.get("_model_onyukleme"):
        return
    st.session_state._model_onyukleme = True
    t = threading.Thread(target=load_model, daemon=True)
    try:
        from streamlit.runtime.scriptrunner import add_script_run_ctx
        add_script_run_ctx(t)
    except Exception:
        pass
    t.start()

# Firebase'den hastalık bilgisini önbellekli oku — aynı hastalık için tekrar tekrar
# ağ sorgusu yapılmasını engeller (Streamlit her etkileşimde script'i baştan çalıştırır)
@st.cache_data(ttl=3600, show_spinner=False)
def hastalik_bilgisi_getir(db_key, lang_key):
    try:
        doc: Any = get_db().collection("hastaliklar").document(db_key).get()
        if doc.exists:
            doc_data = doc.to_dict()
            if doc_data and isinstance(doc_data, dict):
                return doc_data.get(lang_key, {})
    except Exception as e:
        print(f"Firebase okuma hatası: {e}")
    return {}

# Gemini ile hastalık için gerçek zamanlı öneri üret — teşhis edilen tam hastalık
# ismini ve bitkiyi modele gönderip yapılandırılmış (JSON) öneri alır.
# Saf fonksiyon: st.* kullanmaz, bu sayede arka plan iş parçacığından da
# güvenle çağrılabilir (prefetch). api_key ana iş parçacığından geçirilir.
def _gemini_oneri_cek(hastalik_ismi, bitki, lang_key, api_key):
    try:
        from google import genai
        client = genai.Client(api_key=api_key)

        dil = "Türkçe" if lang_key == "TR" else "English"
        seviyeler = "Düşük, Orta, Yüksek" if lang_key == "TR" else "Low, Medium, High"
        prompt = (
            f"Sen deneyimli bir zirai uzmansın. '{bitki}' bitkisinde görülen "
            f"'{hastalik_ismi.replace('_', ' ')}' hastalığı için pratik saha önerisi ver. "
            f"Cevabı {dil} dilinde yaz. Yalnızca şu alanları içeren JSON döndür: "
            f"ilac (önerilen ilaç/etken madde ve uygulama), "
            f"sonuc (tedavi edilmezse muhtemel sonuç), "
            f"ekonomi (verim/ekonomik etki ve kısa tavsiye), "
            f"verim_kaybi_aralik (tedavi edilmezse tahmini verim kaybı yüzde aralığı; "
            f"bu aralığı GENEL bir varsayılan değil, TAM OLARAK bu hastalığın bilinen "
            f"zirai şiddetine göre belirle: hafif yaprak lekeleri düşük (ör. %10-20), "
            f"yanıklık/mildiyö/küf orta (ör. %30-45), virüs ve sistemik hastalıklar "
            f"yüksek (ör. %50-70) seyreder — hastalıktan hastalığa DEĞİŞMELİDİR; "
            f"aralığı DAR ve gerçekçi tut — alt ve üst sınır farkı en fazla 15 puan olsun, "
            f"örn '%25-35' gibi), "
            f"verim_kaybi_seviye (yalnızca şu üç değerden biri: {seviyeler}), "
            f"verim_kaybi_aciklama (bu tahminin tek cümlelik kısa gerekçesi). "
            f"ilac, sonuc, ekonomi alanları en fazla 2-3 cümle olsun."
        )

        schema = {
            "type": "object",
            "properties": {
                "ilac":    {"type": "string"},
                "sonuc":   {"type": "string"},
                "ekonomi": {"type": "string"},
                "verim_kaybi_aralik":   {"type": "string"},
                "verim_kaybi_seviye":   {"type": "string"},
                "verim_kaybi_aciklama": {"type": "string"},
            },
            "required": ["ilac", "sonuc", "ekonomi",
                         "verim_kaybi_aralik", "verim_kaybi_seviye", "verim_kaybi_aciklama"],
        }

        resp = client.models.generate_content(
            model="gemini-flash-lite-latest",  # hızlı+ucuz, hep en güncel flash-lite'ı işaret eder
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.3,
                # Küçük bir "düşünme" (reasoning) bütçesi ver: model, verim kaybı
                # aralığını hastalığa özel muhakeme ederek belirlesin. Bütçe 0 iken
                # hastalıktan bağımsız sabit bir aralığa (ör. %40-55) kilitleniyordu.
                # 512 token, hastalığa göre farklılaşma sağlar ama gecikmeyi az artırır.
                "thinking_config": {"thinking_budget": 512},
            },
        )

        import json
        if resp.text is None:
            return None  # boş yanıt → çağıran taraf Firestore fallback'ine düşer
        return json.loads(resp.text)
    except Exception as e:
        print(f"Gemini öneri hatası: {e}")
        return None  # hata → çağıran taraf Firestore fallback'ine düşer


# Önbellekli: aynı hastalık için 24 saat tek çağrı yeter (kota/maliyet/hız).
@st.cache_data(ttl=86400, show_spinner=False)
def llm_ile_oneri_getir(hastalik_ismi, bitki, lang_key):
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key.startswith("BURAYA"):
        return None  # key ayarlı değil → çağıran taraf Firestore'a düşer
    return _gemini_oneri_cek(hastalik_ismi, bitki, lang_key, api_key)


@st.cache_resource(show_spinner=False)
def _oneri_executor():
    from concurrent.futures import ThreadPoolExecutor
    ex = ThreadPoolExecutor(max_workers=4)
    # google.genai import'u ~1 sn sürüyor; ilk Gemini çağrısı bu maliyeti
    # ödemesin diye executor oluşturulur oluşturulmaz arka planda ısıt.
    ex.submit(lambda: __import__("google.genai"))
    return ex


def oneri_prefetch_baslat(det_cls, lang):
    """Tespit biter bitmez hastalık önerilerini arka planda ve PARALEL olarak
    Gemini'den çekmeye başlar. İstekler kutucuklu görsel çizimi, DB kaydı ve
    sayfa render'ı ile örtüştüğü için 'Uzman raporu hazırlanıyor' beklemesi
    belirgin şekilde kısalır; çoklu hastalıkta sıralı çağrı maliyeti kalkar."""
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key or api_key.startswith("BURAYA") or not det_cls:
        return
    dis_keys = ["scab", "rust", "mold", "virus", "spot", "blight", "curl", "rot", "mildew", "scorch"]
    sick = [c for c in det_cls if any(k in c.lower() for k in dis_keys)]
    if not sick:
        return
    # plant_str, sonuç panelindeki üretimle BİREBİR aynı olmalı (önbellek anahtarı uyumu)
    lang_key = "TR" if lang == "Türkçe" else "EN"
    plants = set([cn.split()[0] for cn in det_cls])
    plant_str = ", ".join(CLASS_TR.get(p.lower(), p.replace('_', ' ').capitalize()) for p in plants) if lang == "Türkçe" else ", ".join(p.replace('_', ' ').capitalize() for p in plants)
    futures = st.session_state.setdefault("oneri_futures", {})
    sonuclar = st.session_state.setdefault("oneri_sonuclar", {})
    ex = _oneri_executor()
    for dis in set(sick):
        anahtar = (dis, plant_str, lang_key)
        if anahtar not in futures and anahtar not in sonuclar:
            futures[anahtar] = ex.submit(_gemini_oneri_cek, dis, plant_str, lang_key, api_key)


def oneri_getir(hastalik_ismi, plant_str, lang_key):
    """Önce arka plan prefetch sonucuna bakar (varsa bekler ve oturuma işler),
    sonra oturumdaki hazır sonuçlara; ikisi de yoksa senkron önbellekli çağrıya düşer."""
    anahtar = (hastalik_ismi, plant_str, lang_key)
    sonuclar = st.session_state.setdefault("oneri_sonuclar", {})
    fut = st.session_state.get("oneri_futures", {}).pop(anahtar, None)
    if fut is not None:
        sonuclar[anahtar] = fut.result()
    if anahtar in sonuclar:
        return sonuclar[anahtar]
    return llm_ile_oneri_getir(hastalik_ismi, plant_str, lang_key)

# ─── DİL AYARLARI ────────────────────────────────────────────
LANGS = {
    "Türkçe": {
        "sidebar_title": "Kontrol Paneli",
        "conf_label":    "Yapay Zekâ Güven Skoru",
        "conf_info_title": "Güven Skoru Nedir?",
        "conf_info_body":  "Modelin bir tespiti geçerli sayması için gereken minimum olasılık eşiğidir. Değeri <b>yükseltirseniz</b> yalnızca yüksek olasılıklı (kesin) tespitler gösterilir; <b>düşürürseniz</b> daha fazla tespit listelenir ancak yanlış tespit riski artar.",
        "upload_label":  "Yaprak Fotoğrafı Yükle",
        "upload_dz_main":  "Dosyayı buraya sürükleyip bırakın",
        "upload_dz_sub":   "Dosya başına maksimum 200 MB · JPG, JPEG, PNG",
        "upload_browse":   "Dosyalara göz at",
        "main_title":    "Tarımsal Analiz Sistemi",
        "main_desc":     "Yapay zekâ destekli anlık bitki hastalığı teşhisi ve tarımsal verim analizi platformu.",
        "info_upload":   "Analize başlamak için sol menüden bir görsel yükleyin.",
        "col1_sub":      "Görsel Analiz",
        "img_cap_orig":  "Yüklenen Görsel",
        "analyze_btn":   "Analizi Başlat",
        "spinner":       "Görsel inceleniyor...",
        "spinner_report":  "Uzman raporu hazırlanıyor...",
        "spinner_advice":  "Uzman önerisi hazırlanıyor...",
        "img_cap_res":   "Teşhis Sonucu",
        "col2_sub":      "Verimlilik Raporu",
        "plant_label":   "Analiz Edilen Bitki",
        "no_plant":      "Sistem bu görselde bir tarım ürünü tespit edemedi.",
        "risk_label":    "TAHMİNİ VERİM KAYBI RİSKİ",
        "vk_seviye":     "Risk seviyesi",
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
        "ready":         "Analize Başla",
        "how":           "Nasıl Çalışır?",
        "feature_title": "Akıllı Tarım Teknolojisi",
        "feature_desc":  "Üretici dostu, yüksek doğruluklu, hızlı analiz sunan bir teşhis sistemi.",
        # Login page
        "lang_label":         "Dil / Language",
        "lp_subtitle":        "Yapay zekâ destekli bitki hastalığı teşhisi<br>ve tarımsal verim analizi platformu",
        "tab_login":          "Giriş Yap",
        "tab_register":       "Kayıt Ol",
        "username":           "Kullanıcı Adı",
        "password":           "Şifre",
        "username_ph":        "Kullanıcı adınızı girin",
        "password_ph":        "Şifrenizi girin",
        "new_username":       "Yeni Kullanıcı Adı",
        "new_password":       "Yeni Şifre",
        "confirm_password":   "Şifre Doğrulama",
        "new_username_ph":    "Bir kullanıcı adı belirleyin",
        "new_password_ph":    "Bir şifre belirleyin",
        "confirm_password_ph":"Şifrenizi tekrar girin",
        "btn_login":          "Giriş Yap",
        "btn_register":       "Kayıt Ol",
        "form_enter_hint":    "Giriş yapmak için Enter'a basın",
        "form_enter_hint_register": "Kayıt olmak için Enter'a basın",
        "err_invalid":        "Kullanıcı adı veya şifre hatalı.",
        "warn_fill_all":      "Lütfen tüm alanları doldurun.",
        "err_mismatch":       "Şifreler uyuşmuyor, lütfen kontrol edin!",
        "success_reg":        "Harika! {} başarıyla kaydedildi. 'Giriş Yap' sekmesinden giriş yapabilirsin.",
        "err_user_taken":     "Bu kullanıcı adı zaten alınmış. Lütfen farklı bir ad deneyin.",
        "pill_accuracy":      "Doğruluk",
        "pill_analysis":      "Analiz",
        "pill_classes":       "Toplam Analiz Sınıfı",
        "footer_scroll":      "↓ Sistem hakkında daha fazla bilgi için aşağı kaydır",
        "sec1_tag":           "PROJEMİZ HAKKINDA",
        "sec1_title":         "Tarımda Yapay Zekâ Devrimi",
        "sec1_lede":          "Tarımsal Analiz Sistemi; üretici, ziraat mühendisi ve araştırmacılar için geliştirilmiş, görüntü tabanlı hastalık teşhisi ve tarımsal verimlilik analizi yapan bir sistemdir. Yönetim Bilişim Sistemleri lisans bitirme projesi kapsamında, gerçek tarım sahasında kullanılabilir bir prototip olarak tasarlanmıştır.",
        "mission_title":      "Misyonumuz",
        "mission_text":       "Bitki hastalıklarının erken teşhisini herkes için erişilebilir kılmak, ürün kayıplarını azaltmak ve ilaç kullanımını optimize ederek sürdürülebilir tarımı desteklemek. Tek bir fotoğrafla, saniyeler içinde profesyonel düzeyde ön teşhis sunmayı hedefliyoruz.",
        "tech_title":         "Kullanılan Teknolojiler",
        "tech_text":          "Sistem; <b>YOLOv8 Medium</b> derin öğrenme modeli üzerine kurulu, <b>PlantDoc</b> veri seti ile eğitilmiştir. Arayüz <b>Streamlit</b> ile geliştirilmiş, kullanıcı verileri <b>SQLite</b> ve <b>Firebase Firestore</b> üzerinde hibrit şekilde yönetilmektedir.",
        "sec2_tag":           "NASIL ÇALIŞIR?",
        "sec2_title":         "Üç Adımda Profesyonel Teşhis",
        "sec2_lede":          "Tarladaki yaprak fotoğrafından dijital rapora kadar tüm süreç, kullanıcı deneyimi düşünülerek üç sade adıma indirgendi.",
        "step1_t":            "Fotoğraf Yükle",
        "step1_d":            "Şüphelendiğin bitki yaprağının fotoğrafını çek ve sisteme yükle. JPG, JPEG ve PNG formatları desteklenir. En iyi sonuç için yaprağı doğal ışık altında, net biçimde fotoğraflaman yeterli.",
        "step2_t":            "Yapay Zekâ Analiz Etsin",
        "step2_d":            "YOLOv8 modeli görüntüyü saniyeler içinde işler; bitki türünü tanır ve olası hastalığı yüksek doğrulukla tespit eder. Her tespit, bounding box ve güven skoru ile görselleştirilir.",
        "step3_t":            "Raporu İncele",
        "step3_d":            "Teşhis sonucu anında ekranına gelir; tüm geçmiş analizlerin \"Geçmiş Analizlerim\" panelinde grafik ve tablolarla saklanır. Kayıtlarını dilediğin zaman gözden geçirip silebilirsin.",
        "sec3_tag":           "SİSTEM ÖZELLİKLERİ",
        "sec3_title":         "Neden Bu Platform?",
        "sec3_lede":          "Sadece bir teşhis aracı değil; aynı zamanda kişisel bir tarımsal veri yönetim sistemi.",
        "feat1_t":            "Çoklu Bitki Desteği",
        "feat1_d":            "Domates, elma, üzüm, mısır ve daha pek çok ürün için 13 bitki türü, 29 toplam analiz kapasitesi.",
        "feat2_t":            "Anlık Sonuç",
        "feat2_d":            "Ortalama 1 saniyenin altında analiz süresi. Tarladayken bile pratik karar desteği.",
        "feat3_t":            "Akıllı Dashboard",
        "feat3_d":            "Geçmiş analizlerin KPI metrikleri, dağılım grafikleri ve detaylı tablolarla görselleştirilir.",
        "feat4_t":            "Veri İzolasyonu",
        "feat4_d":            "Her kullanıcı yalnızca kendi kayıtlarına erişebilir. Verilerin güvenli, gizli ve yönetilebilirdir.",
        "copyright":          "© 2026 PlantDetective · Tüm hakları saklıdır",
        # Sidebar / main app shell
        "logo_text":          "Tarımsal Analiz",
        "logo_sub":           "AI DESTEKLİ SİSTEM",
        "menu_title":         "Menü",
        "menu_hint":          "Hangi sayfaya gitmek istersin?",
        "nav_home":           "Ana Sayfa / Analiz",
        "nav_history":        "Geçmiş Analizlerim",
        "btn_logout":         "Çıkış Yap",
        "nav_live":           "CANLI",
        "nav_powered":        "YAPAY ZEKÂ DESTEKLİ",
        # KPI metrics
        "kpi_acc":            "Model Doğruluğu",
        "kpi_acc_d":          "YOLOv8 Medium",
        "kpi_time":           "ANALİZ SÜRESİ",
        "kpi_time_d":         "Gerçek zamanlı",
        "kpi_dis":            "TOPLAM ANALİZ SINIFI",
        "kpi_dis_d":          "PlantDoc Dataset",
        "kpi_plants":         "DESTEKLENEN BİTKİ",
        "kpi_plants_d":       "Tarım ürünleri",
        # Analysis flow
        "toast_saved":        "Analiz başarıyla veritabanına kaydedildi!",
        "err_save":           "Kayıt Hatası: {}",
        "step_title":         "Üç adımda teşhis",
        "step_sub":           "Karmaşık değil — fotoğraf yükle, analiz et, raporu gör.",
        "features_label":     "ÖZELLİKLER",
        "feature_high_acc_t": "Yüksek Doğruluk",
        "feature_high_acc_d": "YOLOv8 Medium modeli ile %94+ doğruluk oranı. PlantDoc veri seti üzerinde 150 epoch eğitildi.",
        "feature_fast_t":     "Hızlı Analiz",
        "feature_fast_d":     "Görsel yüklendikten 1 saniyeden kısa sürede teşhis. Anlık geri bildirim ve raporlama.",
        "feature_smart_t":    "Akıllı Raporlama",
        "feature_smart_d":    "Hastalık teşhisi sonrası ilaçlama önerisi, finansal etki ve zirai beklenti raporu.",
        # History page
        "hist_tag":           "ANALİZ GEÇMİŞİ",
        "hist_title":         "Geçmiş Analizlerim",
        "hist_desc":          "Veritabanına kaydedilen tüm tarımsal analizlerin özeti, dağılımı ve detaylı kayıt tablosu.",
        "err_session":        "Oturum bilgisi alınamadı. Lütfen tekrar giriş yapın.",
        "err_db_read":        "Veritabanı okuma hatası: {}",
        "info_empty":         "Henüz kayıtlı bir analizin bulunmuyor. Ana sayfadan ilk analizini gerçekleştir, sonuçlar burada görüntülenecek.",
        "kpi_total":          "TOPLAM ANALİZ SAYISI",
        "kpi_common":         "En Sık Rastlanan Hastalık",
        "no_disease":         "Tespit edilen bir hastalık bulunmuyor.",
        "chart1_t":           "Bitki Türü Dağılımı",
        "chart1_d":           "Analiz edilen tarım ürünlerinin frekans dağılımı",
        "chart2_t":           "Sağlık Durumu Oranı",
        "chart2_d":           "Sağlıklı ve enfekte örneklerin genel dağılımı",
        "status_healthy":     "Sağlıklı",
        "status_infected":    "Enfekte",
        "chart_plant":        "Bitki Türü",
        "chart_count":        "Analiz Sayısı",
        "chart_status":       "Durum",
        "chart_quantity":     "Sayı",
        "table_t":            "Detaylı Analiz Kayıtları",
        "table_d":            "Tüm kayıtlar yeniden eskiye doğru sıralanmıştır",
        "col_user":           "Kullanıcı Adı",
        "col_plant":          "Bitki Türü",
        "col_disease":        "Hastalık Durumu",
        "col_date":           "Analiz Tarihi",
        "date_format":        "DD.MM.YYYY HH:mm",
        "delete_exp":         "Hatalı veya Eski Analizleri Seç ve Sil",
        "delete_desc":        "Aşağıdaki menüden silmek istediğiniz <b>birden fazla kaydı</b> manuel olarak seçebilirsiniz. <b>Bu işlem geri alınamaz</b> ve kayıtlar veritabanından kalıcı olarak silinir.",
        "delete_label":       "Silinecek Kayıtları Seçin",
        "delete_ph":          "Silmek istediğiniz analizleri tıklayarak seçin...",
        "delete_count":       "**Seçili kayıt sayısı:** {} adet analiz silinecek.",
        "delete_btn":         "Seçili Kayıtları Kalıcı Olarak Sil",
        "delete_ok":          "{} kayıt başarıyla silindi.",
        "delete_warn":        "Kayıtlar silinemedi. Kayıtlar mevcut değil ya da bu kullanıcıya ait değil.",
        "delete_err":         "Silme işlemi sırasında bir hata oluştu: {}",
    },
    "English": {
        "sidebar_title": "Control Panel",
        "conf_label":    "AI Confidence Score",
        "conf_info_title": "What is the Confidence Score?",
        "conf_info_body":  "The minimum probability threshold for the model to accept a detection as valid. <b>Higher values</b> display only high-probability (more certain) detections; <b>lower values</b> list more detections but increase the risk of false positives. Recommended starting value: <b>0.25</b>.",
        "upload_label":  "Upload Leaf Photo",
        "upload_dz_main":  "Drag and drop file here",
        "upload_dz_sub":   "Limit 200 MB per file · JPG, JPEG, PNG",
        "upload_browse":   "Browse files",
        "main_title":    "Agricultural Analysis System",
        "main_desc":     "AI-powered instant plant disease diagnosis and agricultural productivity analysis platform.",
        "info_upload":   "Upload an image from the sidebar to begin.",
        "col1_sub":      "Visual Analysis",
        "img_cap_orig":  "Uploaded Image",
        "analyze_btn":   "Start Analysis",
        "spinner":       "Analyzing image...",
        "spinner_report":  "Preparing expert report...",
        "spinner_advice":  "Preparing expert advice...",
        "img_cap_res":   "Diagnosis Result",
        "col2_sub":      "Productivity Report",
        "plant_label":   "Analyzed Plant",
        "no_plant":      "No agricultural product detected in this image.",
        "risk_label":    "YIELD LOSS RISK",
        "vk_seviye":     "Risk level",
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
        # Login page
        "lang_label":         "Dil / Language",
        "lp_subtitle":        "AI-powered plant disease diagnosis<br>and agricultural productivity analysis platform",
        "tab_login":          "Sign In",
        "tab_register":       "Sign Up",
        "username":           "Username",
        "password":           "Password",
        "username_ph":        "Enter your username",
        "password_ph":        "Enter your password",
        "new_username":       "New Username",
        "new_password":       "New Password",
        "confirm_password":   "Confirm Password",
        "new_username_ph":    "Choose a username",
        "new_password_ph":    "Choose a password",
        "confirm_password_ph":"Re-enter your password",
        "btn_login":          "Sign In",
        "btn_register":       "Sign Up",
        "form_enter_hint":    "Press Enter to sign in",
        "form_enter_hint_register": "Press Enter to sign up",
        "err_invalid":        "Invalid username or password.",
        "warn_fill_all":      "Please fill in all fields.",
        "err_mismatch":       "Passwords do not match, please check!",
        "success_reg":        "Great! {} has been registered successfully. You can sign in from the 'Sign In' tab.",
        "err_user_taken":     "This username is already taken. Please try a different one.",
        "pill_accuracy":      "Accuracy",
        "pill_analysis":      "Analysis",
        "pill_classes":       "Disease Classes",
        "footer_scroll":      "↓ Scroll down for more information about the system",
        "sec1_tag":           "ABOUT THE PROJECT",
        "sec1_title":         "AI Revolution in Agriculture",
        "sec1_lede":          "The Agricultural Analysis System is a decision support platform developed for farmers, agricultural engineers and researchers, performing image-based disease diagnosis. It is designed as a usable prototype for real agricultural fields within the scope of a Management Information Systems undergraduate graduation project.",
        "mission_title":      "Our Mission",
        "mission_text":       "To make early diagnosis of plant diseases accessible to everyone, reduce crop losses, and support sustainable agriculture by optimizing pesticide use. We aim to provide professional-level preliminary diagnosis within seconds, using a single photo.",
        "tech_title":         "Technologies Used",
        "tech_text":          "The system is built on the <b>YOLOv8 Medium</b> deep learning model and trained with the <b>PlantDoc</b> dataset. The interface is developed with <b>Streamlit</b>, while user data is managed in a hybrid manner via <b>SQLite</b> and <b>Firebase Firestore</b>.",
        "sec2_tag":           "HOW IT WORKS?",
        "sec2_title":         "Professional Diagnosis in Three Steps",
        "sec2_lede":          "From a leaf photo in the field to a digital report, the entire process has been reduced to three simple steps with user experience in mind.",
        "step1_t":            "Upload Photo",
        "step1_d":            "Take a photo of the suspect plant leaf and upload it. JPG, JPEG and PNG formats are supported. For best results, photograph the leaf clearly in natural light.",
        "step2_t":            "Let AI Analyze",
        "step2_d":            "The YOLOv8 model processes the image within seconds; it recognizes the plant species and detects possible diseases with high accuracy. Each detection is visualized with a bounding box and confidence score.",
        "step3_t":            "Review the Report",
        "step3_d":            "The diagnosis appears on your screen instantly; all past analyses are stored with charts and tables in the \"My Past Analyses\" panel. You can review or delete your records anytime.",
        "sec3_tag":           "SYSTEM FEATURES",
        "sec3_title":         "Why This Platform?",
        "sec3_lede":          "Not just a diagnostic tool; it is also a personal agricultural data management system.",
        "feat1_t":            "Multi-Plant Support",
        "feat1_d":            "13 plant species and 29 disease classes for tomato, apple, grape, corn and many other crops.",
        "feat2_t":            "Instant Results",
        "feat2_d":            "Average analysis time under 1 second. Practical decision support even while in the field.",
        "feat3_t":            "Smart Dashboard",
        "feat3_d":            "Your past analyses are visualized with KPI metrics, distribution charts and detailed tables.",
        "feat4_t":            "Data Isolation",
        "feat4_d":            "Each user can only access their own records. Your data is secure, private and manageable.",
        "copyright":          "© 2026 PlantDetective · All rights reserved",
        # Sidebar / main app shell
        "logo_text":          "Agri Analysis",
        "logo_sub":           "AI POWERED SYSTEM",
        "menu_title":         "Menu",
        "menu_hint":          "Which page would you like to visit?",
        "nav_home":           "Home / Analysis",
        "nav_history":        "My Past Analyses",
        "btn_logout":         "Sign Out",
        "nav_live":           "LIVE",
        "nav_powered":        "AI POWERED",
        # KPI metrics
        "kpi_acc":            "Model Accuracy",
        "kpi_acc_d":          "YOLOv8 Medium",
        "kpi_time":           "Analysis Time",
        "kpi_time_d":         "Real-time",
        "kpi_dis":            "Total Analysis Classes",
        "kpi_dis_d":          "PlantDoc Dataset",
        "kpi_plants":         "Supported Plants",
        "kpi_plants_d":       "Crops",
        # Analysis flow
        "toast_saved":        "Analysis saved to the database successfully!",
        "err_save":           "Save Error: {}",
        "step_title":         "Diagnosis in three steps",
        "step_sub":           "It's not complicated — upload a photo, analyze, see the report.",
        "features_label":     "FEATURES",
        "feature_high_acc_t": "High Accuracy",
        "feature_high_acc_d": "Over 94% accuracy with the YOLOv8 Medium model. Trained for 150 epochs on the PlantDoc dataset.",
        "feature_fast_t":     "Fast Analysis",
        "feature_fast_d":     "Diagnosis in less than 1 second after upload. Instant feedback and reporting.",
        "feature_smart_t":    "Smart Reporting",
        "feature_smart_d":    "After diagnosis: treatment recommendations, financial impact and agronomic outlook.",
        # History page
        "hist_tag":           "ANALYSIS HISTORY",
        "hist_title":         "My Past Analyses",
        "hist_desc":          "Academic summary, distribution and detailed record table of all agricultural analyses stored in the database.",
        "err_session":        "Session info could not be retrieved. Please sign in again.",
        "err_db_read":        "Database read error: {}",
        "info_empty":         "You don't have any saved analyses yet. Run your first analysis from the home page and results will appear here.",
        "kpi_total":          "Total Number of Analyses",
        "kpi_common":         "Most Common Disease",
        "no_disease":         "No detected disease found.",
        "chart1_t":           "Plant Type Distribution",
        "chart1_d":           "Frequency distribution of analyzed crops",
        "chart2_t":           "Health Status Ratio",
        "chart2_d":           "Overall distribution of healthy and infected samples",
        "status_healthy":     "Healthy",
        "status_infected":    "Infected",
        "chart_plant":        "Plant Type",
        "chart_count":        "Analysis Count",
        "chart_status":       "Status",
        "chart_quantity":     "Count",
        "table_t":            "Detailed Analysis Records",
        "table_d":            "All records are sorted from newest to oldest",
        "col_user":           "Username",
        "col_plant":          "Plant Type",
        "col_disease":        "Disease Status",
        "col_date":           "Analysis Date",
        "date_format":        "MM/DD/YYYY HH:mm",
        "delete_exp":         "Manually Select and Delete Incorrect or Old Analyses",
        "delete_desc":        "From the menu below, you can manually select <b>multiple records</b> to delete. <b>This action cannot be undone</b> and records will be permanently removed from the database.",
        "delete_label":       "Select Records to Delete",
        "delete_ph":          "Click to select the analyses you want to delete...",
        "delete_count":       "**Selected records:** {} analyses will be deleted.",
        "delete_btn":         "Permanently Delete Selected Records",
        "delete_ok":          "{} records successfully deleted.",
        "delete_warn":        "Records could not be deleted. They may not exist or belong to another user.",
        "delete_err":         "An error occurred during deletion: {}",
    },
}

CLASS_TR = {
    "apple":"Elma","tomato":"Domates","grape":"Üzüm","corn":"Mısır","potato":"Patates",
    "cherry":"Kiraz","strawberry":"Çilek","bell_pepper":"Biber","pepper":"Biber",
    "peach":"Şeftali","squash":"Kabak","soybean":"Soya Fasulyesi","raspberry":"Ahududu",
    "healthy":"Sağlıklı","leaf":"Yaprağı","leaves":"Yaprakları",
    "scab":"Karaleke","rust":"Pas","virus":"Virüs","blight":"Yanıklık",
    "spot":"Lekesi","spots":"Lekeleri","mold":"Küf","mildew":"Külleme",
    "rot":"Çürüklük","early":"Erken","late":"Geç","black":"Siyah",
    "bacterial":"Bakteriyel","mosaic":"Mozaik","yellow":"Sarı",
    "blueberry":"Yaban Mersini","gray":"Gri","soyabean":"Soya Fasulyesi",
    "septoria":"Septoria","two":"İki","spotted":"Noktalı","spider":"Örümcek",
    "mites":"Akarı","powdery":""  # 'powdery mildew' -> yalnızca 'Külleme' (mildew) yazılır
}


def sinif_ismi_ceviri(name: str) -> str:
    """Modelin İngilizce sınıf ismini ('Tomato leaf yellow virus') CLASS_TR ile
    Türkçeye çevirir ('Domates Yaprağı Sarı Virüs'). Kelimeler boşlukla ayrılır;
    'Bell_pepper' gibi alt çizgili terimler tek parça olarak sözlükte aranır.
    Eşleşmeyen kelimeler baş harfi büyük tutulur, boş çeviriler (ör. 'powdery') atlanır."""
    parcalar = []
    for token in name.split():
        tr = CLASS_TR.get(token.lower(), token.capitalize())
        if tr:  # boş string dönen kelimeleri (powdery) atla
            parcalar.append(tr)
    return " ".join(parcalar)


def analiz_gorseli_ciz(lang: str):
    """session_state'teki ham tespit sonucunu (result) o anki dile göre kutucuklu
    görsele çevirir. Türkçe seçiliyse etiketler Türkçe, İngilizce seçiliyse orijinal
    İngilizce çizilir. Model yeniden ÇALIŞTIRILMAZ; yalnızca plot() yeniden çizilir —
    böylece dil değişince tekrar analiz (ve tekrar DB kaydı) gerekmez."""
    res_obj = st.session_state.get("result")
    isimler = st.session_state.get("model_names", {})
    if res_obj is None:
        return None
    if lang == "Türkçe":
        res_obj.names = {k: sinif_ismi_ceviri(v) for k, v in isimler.items()}
    else:
        res_obj.names = dict(isimler)
    return res_obj.plot()[:, :, ::-1]


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
    # ─── GİRİŞ EKRANI ARKA PLANI (tarımsal drone görseli) ───
    # Görselin üzerine hafif beyaz bir katman (overlay) koyarak kartların ve
    # yazıların okunaklığını korurken projenin ruhuna uygun bir doku sağlarız.
    _bg = asset_data_uri("login_bg.jpg")
    if _bg:
        st.markdown(f"""
        <style>
        .stApp {{
            background:
                linear-gradient(180deg, rgba(248,250,252,0.12) 0%, rgba(248,250,252,0.10) 45%, rgba(248,250,252,0.22) 78%, rgba(250,250,250,0.40) 100%),
                url("{_bg}") center top / cover no-repeat fixed !important;
        }}
        /* Ana uygulamadaki köşe ışıltıları (radial-gradient) giriş ekranında
           kapatılır; arka plan görseli üzerinde parlama/hâle oluşturmasınlar. */
        .stApp::before {{ background: none !important; }}
        </style>
        """, unsafe_allow_html=True)

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
        background: transparent; border: none; box-shadow: none;
        padding: 8px 0 4px 0;
        animation: cardIn 0.45s cubic-bezier(0.34,1.56,0.64,1); text-align: center; position: relative;
    }
    @keyframes cardIn { from { opacity: 0; transform: translateY(16px); } to   { opacity: 1; transform: translateY(0); } }
    .lp-icon {
        width: 64px; height: 64px; margin: 0 auto 20px auto; background: #ecfdf5; border: 1px solid #a7f3d0;
        border-radius: 16px; display: flex; align-items: center; justify-content: center; font-size: 30px;
    }
    /* Logo — şeffaf zeminli, arka planın üstünde serbest yüzer; drop-shadow ile
       hem parlar hem de metin/emblem arka plandan ayrışıp öne çıkar (kutu YOK). */
    .lp-logo {
        display: block; width: 100%; max-width: 440px; height: auto; margin: 0 auto 6px auto;
        filter:
            drop-shadow(0 0 10px rgba(255,255,255,0.95))
            drop-shadow(0 0 3px rgba(255,255,255,0.95))
            drop-shadow(0 6px 14px rgba(15,23,42,0.28));
    }
    .lp-title { font-size: 1.55rem; font-weight: 800; color: #0f172a !important; margin: 0 0 8px 0; letter-spacing: -0.03em; }
    .lp-sub { font-size: 0.92rem; color: #64748b !important; margin: 0; font-weight: 400; line-height: 1.55; }
    .lp-stats { display: flex; justify-content: center; gap: 8px; margin: 24px 0 4px 0; flex-wrap: wrap; }
    .lp-pill {
        padding: 5px 12px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 100px;
        font-size: 0.74rem; color: #64748b !important; font-weight: 500;
    }
    .lp-pill b { color: #0f172a !important; font-weight: 700; }
    /* Alt not ve telif satırı da görselin üstünde duruyor; .lp-pill ile aynı
       hafif beyaz hap görünümüne alınarak okunaklı hale getirilir. */
    .lp-note-wrap { text-align: center; margin-top: 22px; }
    .lp-footer-note {
        display: inline-block;
        padding: 6px 16px;
        background: rgba(255,255,255,0.92);
        -webkit-backdrop-filter: blur(6px);
        backdrop-filter: blur(6px);
        border: 1px solid #e5e7eb;
        border-radius: 100px;
        font-size: 0.76rem;
        color: #475569 !important;
        font-weight: 500;
    }

    /* ─── GİRİŞ FORMU — DÜZ BEYAZ KART (.st-key-login_panel) ───
       Yalnızca form konteynerine uygulanır; arka plandaki görsel kartın
       çevresinde/üstünde net görünür, form yazıları beyaz zeminde okunur. */
    .st-key-login_panel {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 20px !important;
        padding: 24px 30px 20px 30px !important;
        box-shadow: 0 24px 60px rgba(15,23,42,0.22) !important;
    }
    .st-key-login_panel [data-baseweb="tab"] p { font-weight: 600 !important; }
    /* Etiketler (Kullanıcı Adı / Şifre) koyu ve okunaklı */
    .st-key-login_panel label p { color: #1e293b !important; font-weight: 600 !important; }
    /* Giriş alanları — beyaz kartın üzerinde KAYBOLMASIN diye alan belirgin açık-gri
       zemin + kenarlık alır; yazı KOYU ve KALIN; otomatik-dolu (autofill) durumunda
       da aynı zemin/yazı korunur (Chrome grisini bastırır). */
    .st-key-login_panel [data-baseweb="input"] {
        background: #eef2f7 !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 10px !important;
    }
    .st-key-login_panel [data-baseweb="input"]:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(47,168,90,0.15) !important;
    }
    .st-key-login_panel input {
        background: transparent !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-weight: 600 !important;
    }
    .st-key-login_panel input::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        font-weight: 400 !important;
    }
    .st-key-login_panel input:-webkit-autofill,
    .st-key-login_panel input:-webkit-autofill:hover,
    .st-key-login_panel input:-webkit-autofill:focus,
    .st-key-login_panel input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 1000px #eef2f7 inset !important;
        -webkit-text-fill-color: #0f172a !important;
        caret-color: #0f172a !important;
        transition: background-color 9999s ease-in-out 0s !important;
    }

    /* ─── Landing Page Bölümleri ─── */
    /* Bölüm başlıkları arka plan görselinin doğrudan üstünde duruyordu ve
       yaprak dokusunda okunmuyordu. Kartlarla aynı dili konuşan (beyaz zemin,
       #e5e7eb kenarlık, yuvarlak köşe) hafif buzlu bir panel içine alınır;
       arka plan görseli panelin çevresinde ve altından görünmeye devam eder. */
    .ls-head {
        max-width: 780px;
        margin: 0 auto 32px auto;
        padding: 26px 30px 24px 30px;
        text-align: center;
        background: rgba(255,255,255,0.90);
        -webkit-backdrop-filter: blur(8px);
        backdrop-filter: blur(8px);
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(15,23,42,0.10);
    }
    .ls-section-tag {
        display: inline-block;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 100px;
        padding: 4px 14px;
        font-size: 0.7rem;
        color: #065f46 !important;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .ls-section-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a !important;
        letter-spacing: -0.03em;
        margin: 0 0 12px 0;
        line-height: 1.2;
    }
    .ls-section-lede {
        font-size: 1rem;
        color: #64748b !important;
        font-weight: 400;
        line-height: 1.6;
        margin: 0 0 8px 0;
        max-width: 720px;
    }
    .ls-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 26px 24px;
        height: 100%;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .ls-card:hover {
        border-color: #a7f3d0;
        transform: translateY(-2px);
    }
    .ls-step-num {
        width: 36px;
        height: 36px;
        background: #7DA78C;
        color: #ffffff !important;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 14px;
    }
    .ls-feature-icon {
        width: 44px;
        height: 44px;
        background: #ecfdf5;
        border: 1px solid #a7f3d0;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        margin-bottom: 14px;
    }
    .ls-card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #0f172a !important;
        margin: 0 0 6px 0;
        letter-spacing: -0.01em;
    }
    .ls-card-text {
        font-size: 0.86rem;
        color: #64748b !important;
        line-height: 1.55;
        margin: 0;
    }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { padding-top: 10px; padding-bottom: 10px; }

    /* Login page — language selector as a centered pill-style box */
    .stRadio > div {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    .stRadio [role="radiogroup"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 4px !important;
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 100px !important;
        padding: 4px 6px !important;
        width: fit-content !important;
        margin: 0 auto 14px auto !important;
        box-shadow: 0 1px 3px rgba(15,23,42,0.04) !important;
    }
    .stRadio [role="radiogroup"] label {
        padding: 5px 14px !important;
        margin: 0 !important;
        border-radius: 100px !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: background 0.2s ease !important;
    }
    .stRadio [role="radiogroup"] label:hover { background: #f9fafb !important; }

    /* Login page — şifre alanındaki göz (göster/gizle) düğmesi TERTEMİZ dursun:
       alanın içindeki tüm iç kenarlık/ayraç/zemin/gölge sıfırlanır, yalnızca
       en dıştaki [data-baseweb="input"] çerçevesi kalır. Böylece göz ikonunun
       çevresinde "iç içe geçmiş çizgiler" (ayraç + çerçeve çakışması) oluşmaz. */
    .stTextInput [data-baseweb="input"] > div,
    .stTextInput [data-baseweb="base-input"],
    .stTextInput [data-testid="stTextInputRootElement"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
    }
    .stTextInput [data-baseweb="input"] button {
        border: none !important;
        border-left: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
        padding: 0 6px !important;
        margin: 0 !important;
    }
    .stTextInput [data-baseweb="input"] button:hover {
        background: transparent !important;
        color: var(--primary) !important;
    }
    .stTextInput [data-baseweb="input"] button:focus,
    .stTextInput [data-baseweb="input"] button:focus-visible,
    .stTextInput [data-baseweb="input"] button:active {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ─── DİL SEÇİCİ (LANGUAGE SELECTOR) — ikon kartıyla aynı hizada, sayfada tam ortalı ───
    _, lc, _ = st.columns([1, 0.2, 1])
    with lc:
        st.radio(
            LANGS[st.session_state.lang]["lang_label"],
            ("Türkçe", "English"),
            index=0 if st.session_state.lang == "Türkçe" else 1,
            horizontal=True,
            key="lang",
            label_visibility="collapsed",
        )
    T = LANGS[st.session_state.lang]

    # Streamlit'in İngilizce "Press Enter to submit form" ipucunu gizle; her formun
    # kendi lokalize ve sekmeye özel ipucunu form içinde ayrıca göstereceğiz.
    st.markdown("""
    <style>
    [data-testid="InputInstructions"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ─── LOGO + GİRİŞ FORMU ───
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        # LOGO — arka planın üzerinde serbest yüzer; ÇEVRESİNDE KUTU YOK.
        _logo = asset_data_uri("logo_transparent.png")
        _logo_html = (
            f'<img class="lp-logo" src="{_logo}" alt="PlantDetective" />'
            if _logo else '<div class="lp-icon">🌿</div>'
        )
        st.markdown(f"""
        <div class="lp-card">
            {_logo_html}
        </div>
        """, unsafe_allow_html=True)

        # FORM — okunabilirlik için buzlu cam (frosted) panel. Stil yalnızca bu
        # konteynerin .st-key-login_panel sınıfına uygulanır; logoya sıçramaz.
        with st.container(key="login_panel"):
            # ─── SEKMELER (TABS) BAŞLANGICI ───
            tab_giris, tab_kayit = st.tabs([T["tab_login"], T["tab_register"]])

            # 1. GİRİŞ SEKME İÇERİĞİ
            with tab_giris:
                with st.form("login_form", clear_on_submit=False, border=False):
                    username = st.text_input(T["username"], placeholder=T["username_ph"], key="login_user")
                    password = st.text_input(T["password"], type="password", placeholder=T["password_ph"], key="login_pass")
                    st.write("")
                    giris_yap = st.form_submit_button(T["btn_login"], use_container_width=True, type="primary")
                    st.markdown(f"<div style='text-align:right;font-size:0.72rem;color:#64748b;margin-top:6px;'>{T['form_enter_hint']}</div>", unsafe_allow_html=True)

                if giris_yap:
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
                        st.error(T["err_invalid"])

            # 2. KAYIT SEKME İÇERİĞİ
            with tab_kayit:
                with st.form("register_form", clear_on_submit=False, border=False):
                    new_user = st.text_input(T["new_username"], placeholder=T["new_username_ph"], key="reg_user")
                    new_pass = st.text_input(T["new_password"], type="password", placeholder=T["new_password_ph"], key="reg_pass")
                    new_pass2 = st.text_input(T["confirm_password"], type="password", placeholder=T["confirm_password_ph"], key="reg_pass2")
                    st.write("")
                    kayit_ol = st.form_submit_button(T["btn_register"], use_container_width=True, type="primary")
                    st.markdown(f"<div style='text-align:right;font-size:0.72rem;color:#64748b;margin-top:6px;'>{T['form_enter_hint_register']}</div>", unsafe_allow_html=True)

                if kayit_ol:
                    if not new_user or not new_pass:
                        st.warning(T["warn_fill_all"])
                    elif new_pass != new_pass2:
                        st.error(T["err_mismatch"])
                    else:
                        try:
                            conn = sqlite3.connect('tarimsal_analiz.db', check_same_thread=False)
                            c = conn.cursor()
                            su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                            c.execute("INSERT INTO kullanicilar (kullanici_adi, sifre, kayit_tarihi) VALUES (?, ?, ?)",
                                      (new_user.strip().lower(), new_pass.strip(), su_an))
                            conn.commit()
                            conn.close()
                            st.success(T["success_reg"].format(new_user))
                        except sqlite3.IntegrityError:
                            st.error(T["err_user_taken"])

            # ─── ALT İSTATİSTİKLER ───
            st.markdown(f"""
            <div class="lp-stats">
                <span class="lp-pill"><b>%94+</b> {T["pill_accuracy"]}</span>
                <span class="lp-pill"><b>&lt;1sn</b> {T["pill_analysis"]}</span>
                <span class="lp-pill"><b>29</b> {T["pill_classes"]}</span>
            </div>
            """, unsafe_allow_html=True)

    # Sayfa akışını bildiren alt not — panel dışında, tam ortalı.
    st.markdown(f"""
    <div class="lp-note-wrap"><span class="lp-footer-note">{T["footer_scroll"]}</span></div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    #  LANDING PAGE — Tam Genişlikte Vitrin Bölümleri
    # ══════════════════════════════════════════════════════
    st.write("")
    st.write("")
    st.divider()
    st.write("")

    # ─────────────────────────────────────────────────────
    #  BÖLÜM 1 — PROJEMİZ HAKKINDA
    # ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ls-head">
        <span class="ls-section-tag">{T["sec1_tag"]}</span>
        <h2 class="ls-section-title">{T["sec1_title"]}</h2>
        <p class="ls-section-lede" style="margin:0 auto;">
            {T["sec1_lede"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    h1, h2 = st.columns(2, gap="large")
    with h1:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["mission_title"]}</h3>
            <p class="ls-card-text">
                {T["mission_text"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with h2:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["tech_title"]}</h3>
            <p class="ls-card-text">
                {T["tech_text"]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    # ─────────────────────────────────────────────────────
    #  BÖLÜM 2 — NASIL ÇALIŞIR?
    # ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ls-head">
        <span class="ls-section-tag">{T["sec2_tag"]}</span>
        <h2 class="ls-section-title">{T["sec2_title"]}</h2>
        <p class="ls-section-lede" style="margin:0 auto;">
            {T["sec2_lede"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    a1, a2, a3 = st.columns(3, gap="large")
    with a1:
        st.markdown(f"""
        <div class="ls-card">
            <div class="ls-step-num">1</div>
            <h3 class="ls-card-title">{T["step1_t"]}</h3>
            <p class="ls-card-text">
                {T["step1_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with a2:
        st.markdown(f"""
        <div class="ls-card">
            <div class="ls-step-num">2</div>
            <h3 class="ls-card-title">{T["step2_t"]}</h3>
            <p class="ls-card-text">
                {T["step2_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with a3:
        st.markdown(f"""
        <div class="ls-card">
            <div class="ls-step-num">3</div>
            <h3 class="ls-card-title">{T["step3_t"]}</h3>
            <p class="ls-card-text">
                {T["step3_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    # ─────────────────────────────────────────────────────
    #  BÖLÜM 3 — SİSTEM ÖZELLİKLERİ
    # ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="ls-head">
        <span class="ls-section-tag">{T["sec3_tag"]}</span>
        <h2 class="ls-section-title">{T["sec3_title"]}</h2>
        <p class="ls-section-lede" style="margin:0 auto;">
            {T["sec3_lede"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4, gap="medium")
    with f1:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["feat1_t"]}</h3>
            <p class="ls-card-text">
                {T["feat1_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["feat2_t"]}</h3>
            <p class="ls-card-text">
                {T["feat2_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["feat3_t"]}</h3>
            <p class="ls-card-text">
                {T["feat3_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown(f"""
        <div class="ls-card">
            <h3 class="ls-card-title">{T["feat4_t"]}</h3>
            <p class="ls-card-text">
                {T["feat4_d"]}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────
    #  COPYRIGHT — Sayfa Sonu
    # ─────────────────────────────────────────────────────
    st.write("")
    st.write("")
    st.divider()
    st.markdown(f"""
    <div class="lp-note-wrap" style="padding:20px 0 10px 0;margin-top:0;">
        <span class="lp-footer-note">{T["copyright"]}</span>
    </div>
    """, unsafe_allow_html=True)

    # Login ekranı çizildikten SONRA modeli arka planda yüklemeye başla —
    # kullanıcı giriş bilgilerini girerken model hazırlanır, ilk analiz beklemesiz olur.
    modeli_onyukle_arkaplan()

# ══════════════════════════════════════════════════════════
#  ANA UYGULAMA
# ══════════════════════════════════════════════════════════
def main_app():
    # ══════════════════════════════════════════════════════
    #  SIDEBAR — Logo + Dil + Sayfa Navigasyonu + Çıkış
    # ══════════════════════════════════════════════════════
    T = LANGS[st.session_state.lang]

    # ── SIDEBAR — KOYU YEŞİL ADMIN-PANEL TEMASI (referans görsele göre) ──
    # Koyu yeşil zemin, aktif satırda dolu yeşil vurgu, sage-gri bölüm başlıkları;
    # tıklanabilir satırlar düz/şeffaf (beyaz pill YOK).
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1c4030 0%, #14301f 55%, #10241b 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    section[data-testid="stSidebar"] > div { background: transparent !important; }
    section[data-testid="stSidebar"]::before { background: #34c46a !important; }
    /* Sidebar genel metin rengi (soluk yeşil-beyaz) */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] * { color: #cddbd2 !important; }
    section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; margin: 0.8rem 0 !important; }

    /* Bölüm başlıkları / etiketler — sage-gri (blanket kuralı ezmek için nitelendi) */
    section[data-testid="stSidebar"] .sb-title { color:#7d9a8a !important; font-size:0.7rem !important; font-weight:700 !important;
        letter-spacing:0.12em !important; text-transform:uppercase !important; }
    section[data-testid="stSidebar"] .sb-hint  { color:#7d9a8a !important; font-size:0.74rem !important; font-weight:500 !important; }
    section[data-testid="stSidebar"] .sb-sub   { color:#8fae9d !important; }

    /* Navigasyon & dil satırları — admin panel satır görünümü (beyaz pill YOK) */
    section[data-testid="stSidebar"] [role="radiogroup"] { gap: 5px !important; background: transparent !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        color: #cddbd2 !important;
        padding: 10px 14px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label * { color: #cddbd2 !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.06) !important;
        border-color: rgba(255,255,255,0.08) !important;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover,
    section[data-testid="stSidebar"] [role="radiogroup"] label:hover * { color: #ffffff !important; }
    section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"],
    section[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] {
        background: #2e7d50 !important;
        border-color: #2e7d50 !important;
        box-shadow: 0 4px 14px rgba(46,125,80,0.35) !important;
        font-weight: 600 !important;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"],
    section[data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] *,
    section[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"],
    section[data-testid="stSidebar"] [role="radiogroup"] label[aria-checked="true"] * { color: #ffffff !important; }

    /* Çıkış butonu — koyu zemine uygun, sırıtmayan kırmızı vurgu */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(239,68,68,0.12) !important;
        color: #fca5a5 !important;
        border: 1px solid rgba(239,68,68,0.35) !important;
    }
    section[data-testid="stSidebar"] .stButton > button * { color: #fca5a5 !important; }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(239,68,68,0.22) !important;
        border-color: rgba(239,68,68,0.60) !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover,
    section[data-testid="stSidebar"] .stButton > button:hover * { color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

    _sb_logo = asset_data_uri("logo_sidebar.png")
    _sb_logo_html = (
        f'<img src="{_sb_logo}" alt="PlantDetective" '
        f'style="display:block;width:100%;height:auto;" />'
        if _sb_logo else
        '<div style="width:52px;height:52px;margin:0 auto;background:#ecfdf5;'
        'border:1px solid #a7f3d0;border-radius:14px;display:flex;align-items:center;'
        'justify-content:center;font-size:26px;line-height:1;">🌿</div>'
    )
    # Şeffaf logo, TAM GENİŞLİKTE beyaz bir kart içinde ve büyük gösterilir —
    # referans admin-panelindeki gibi logo karta yakın/dolgun görünür.
    st.sidebar.markdown(f"""
    <div style="padding:4px 0 14px 0;text-align:center;">
        <div style="background:#ffffff;border-radius:14px;padding:16px 18px;
            box-shadow:0 8px 22px rgba(15,23,42,0.22);margin:0 0 12px 0;">
            {_sb_logo_html}
        </div>
        <div class="sb-sub" style="font-size:0.7rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-top:2px;">
            {T["logo_sub"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── DİL SEÇİMİ ───────────────────────────────────────
    st.sidebar.markdown(f"""
    <div style="margin:2px 0 8px 0;">
        <span class="sb-title">{T["lang_label"]}</span>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.radio(
        T["lang_label"],
        ("Türkçe", "English"),
        index=0 if st.session_state.lang == "Türkçe" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key="lang",
    )
    # Dil değişimi sonrası T'yi tazele (radio bu rerun'da güncellemiş olabilir)
    T = LANGS[st.session_state.lang]

    # Dil değiştiğinde sayfa navigasyon seçimini sıfırla
    if st.session_state.get("_lang_cache") != st.session_state.lang:
        st.session_state._lang_cache = st.session_state.lang
        if "page_nav" in st.session_state:
            del st.session_state["page_nav"]

    st.sidebar.divider()

    # ── SAYFA YÖNLENDİRME (NAVİGASYON) ───────────────────
    st.sidebar.markdown(f"""
    <div style="margin-bottom:8px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <span class="sb-title">{T["menu_title"]}</span>
        </div>
        <div class="sb-hint" style="margin-top:3px;">
            {T["menu_hint"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_options = (T["nav_home"], T["nav_history"])
    sayfa = st.sidebar.radio(
        T["menu_title"],
        nav_options,
        label_visibility="collapsed",
        key="page_nav",
    )

    st.sidebar.divider()

    # ── ÇIKIŞ ────────────────────────────────────────────
    if st.sidebar.button(T["btn_logout"], use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.clear()
        st.rerun()

    st.sidebar.markdown("""
    <div style="text-align:center;margin-top:24px;">
        <span style="background:rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.12);border-radius:100px;
            padding:4px 14px;font-size:0.7rem;
            color:#8b98a9 !important;font-weight:600;letter-spacing:0.04em;">
            v2.0
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════
    #  SAYFA YÖNLENDİRİCİSİ
    # ══════════════════════════════════════════════════════
    if sayfa == nav_options[0]:
        ana_analiz_sayfasi(T, st.session_state.lang)
    else:
        gecmis_analiz_sayfasi(T)


# ══════════════════════════════════════════════════════════
#  ANA ANALİZ SAYFASI — Fotoğraf yükleme + YOLOv8 + Rapor
# ══════════════════════════════════════════════════════════
def ana_analiz_sayfasi(T, lang):
   
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
            {T["nav_powered"]}
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
    with c1: st.metric(T["kpi_acc"],    "%94",  T["kpi_acc_d"])
    with c2: st.metric(T["kpi_time"],   "<1 sn", T["kpi_time_d"])
    with c3: st.metric(T["kpi_dis"],    "38",    T["kpi_dis_d"])
    with c4: st.metric(T["kpi_plants"], "14",    T["kpi_plants_d"])

    st.write("")
    st.write("")

    # ── KONTROL PANELİ (Görsel Yükleme + Güven Skoru) ────────
    st.markdown(f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:14px;
        padding:18px 22px 6px 22px;
        margin-bottom:18px;
    ">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="color:#0f172a;font-size:1rem;font-weight:700;letter-spacing:-0.01em;">
                {T['sidebar_title']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    kp1, kp2 = st.columns([1, 1.4], gap="large")
    with kp1:
        # Sabit key: dil değişince label değişse de slider değeri (ve dolayısıyla
        # mevcut analiz sonucu) sıfırlanmaz — aksi halde Streamlit label'ı değişen
        # widget'ı yeni sanıp varsayılana döner ve analizi tekrar yaptırırdı.
        conf = st.slider(T["conf_label"], min_value=0.00, max_value=1.00, value=0.25, step=0.01, key="conf_slider")
        st.markdown(f"""
        <div style="
            background: linear-gradient(180deg, #ffffff 0%, var(--primary-soft) 100%);
            border: 1.5px dashed var(--primary-border);
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 4px;
            transition: all 0.2s ease;
        ">
            <div style="
                color: var(--text-dark);
                font-size: 0.95rem;
                font-weight: 700;
                letter-spacing: -0.01em;
                margin-bottom: 6px;
            ">
                {T['conf_info_title']}
            </div>
            <div style="
                color: var(--text-mid);
                font-size: 0.85rem;
                line-height: 1.55;
                font-weight: 500;
            ">
                {T['conf_info_body']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with kp2:
        # Streamlit'in default İngilizce dropzone metinlerini gizleyip
        # ::before / ::after ile seçili dile göre çevrili metinleri tek seferde yerleştir.
        st.markdown(f"""
        <style>
        /* Dropzone içindeki tüm orijinal metinleri (span/small) gizle */
        [data-testid="stFileUploadDropzone"] span,
        [data-testid="stFileUploadDropzone"] small,
        [data-testid="stFileUploaderDropzoneInstructions"] span,
        [data-testid="stFileUploaderDropzoneInstructions"] small,
        [data-testid="stFileUploadDropzoneInstructions"] span,
        [data-testid="stFileUploadDropzoneInstructions"] small {{
            font-size: 0 !important;
            line-height: 0 !important;
        }}
        /* Ana metni yalnızca instructions konteyneri üzerinde TEK kez bas */
        [data-testid="stFileUploaderDropzoneInstructions"]::before,
        [data-testid="stFileUploadDropzoneInstructions"]::before {{
            content: "{T['upload_dz_main']}";
            display: block;
            color: var(--text-dark) !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
            line-height: 1.4 !important;
            letter-spacing: -0.01em;
        }}
        /* Alt bilgi metni (boyut limiti / format) */
        [data-testid="stFileUploaderDropzoneInstructions"]::after,
        [data-testid="stFileUploadDropzoneInstructions"]::after {{
            content: "{T['upload_dz_sub']}";
            display: block;
            color: var(--text-mid) !important;
            font-weight: 600 !important;
            font-size: 0.78rem !important;
            line-height: 1.4 !important;
        }}
        /* Browse files butonu — orijinal metin + tüm alt elemanları sıfırla, çeviriyi enjekte et */
        [data-testid="stFileUploadDropzone"] button,
        [data-testid="stFileUploadDropzone"] button * {{
            font-size: 0 !important;
            line-height: 0 !important;
        }}
        [data-testid="stFileUploadDropzone"] button::before {{
            content: "{T['upload_browse']}";
            color: #ffffff !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
            line-height: 1.4 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader(T["upload_label"], type=["jpg", "jpeg", "png"], key="img_upload")

    st.write("")

    if uploaded is not None:
        # Görsel veya güven skoru değiştiğinde önceki analiz sonucunu sıfırla.
        # Analiz YALNIZCA "Analizi Başlat"a tıklanınca yapılır/gösterilir; slider
        # oynatmak ya da aynı isimli yeni bir görsel yüklemek eski sonucu göstermez.
        gorsel_kimlik = getattr(uploaded, "file_id", uploaded.name)
        if st.session_state.get("cur_img") != gorsel_kimlik or st.session_state.get("cur_conf") != conf:
            st.session_state.analiz_ok = False
        # Görsel yüklenir yüklenmez executor'ı (ve google.genai import ısıtmasını)
        # başlat: kullanıcı "Analizi Başlat"a basana kadar import çoktan biter.
        _oneri_executor()
        st.session_state.cur_img  = gorsel_kimlik
        st.session_state.cur_conf = conf

        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.subheader(T['col1_sub'])
            img = Image.open(uploaded)
            image_slot = st.empty()
            sonuc_gorsel = analiz_gorseli_ciz(lang) if st.session_state.get("analiz_ok") else None
            if sonuc_gorsel is not None:
                image_slot.image(sonuc_gorsel, caption=T["img_cap_res"], use_container_width=True)
            else:
                # Ham sonuç yoksa (ör. eski oturum state'i) orijinal görseli göster;
                # çökmemesi sayesinde alttaki eylem planı da render edilmeye devam eder.
                image_slot.image(img, caption=T["img_cap_orig"], use_container_width=True)
            st.write("")
            run_btn = st.button(T["analyze_btn"], use_container_width=True, type="primary")

        if run_btn:
            with col1, st.spinner(T["spinner"]):
                model = load_model()
                res = model.predict(source=img, conf=conf, imgsz=640, verbose=False)
                # Ham tespit sonucunu sakla. Kutucuklu görsel, dil değişince yeniden
                # analiz gerektirmeden, o anki dile göre analiz_gorseli_ciz ile çizilir.
                # (Türkçe karakterler için plot() otomatik PIL/Unicode moduna geçer.)
                # classes ise İngilizce model.names'ten okunur; hastalık anahtar-kelime
                # eşleşmesi buna bağlı.
                r0 = res[0]
                boxes = r0.boxes
                st.session_state.result      = r0
                st.session_state.model_names = dict(model.names)
                st.session_state.classes     = [model.names[int(c)] for c in boxes.cls] if boxes is not None else []
                st.session_state.confs       = [float(c) for c in boxes.conf] if boxes is not None else []
                st.session_state.analiz_ok   = True
                # Uzman raporu isteklerini HEMEN arka planda başlat: görsel çizimi,
                # DB kaydı ve render ile paralel yürüsün (bekleme süresini kısaltır).
                oneri_prefetch_baslat(st.session_state.classes, lang)
                # Orijinal görselin yerine tespit sonucunu (bounding box'lı) bas
                _analiz_gorseli = analiz_gorseli_ciz(lang)
                if _analiz_gorseli is not None:
                    image_slot.image(_analiz_gorseli, caption=T["img_cap_res"], use_container_width=True)
                
                # ─── YENİ EKLENEN: SQL KAYIT İŞLEMİ ───
                try:
                    det_cls = st.session_state.classes
                    det_conf = st.session_state.confs
                    
                    plants = set()
                    for cn in det_cls:
                        # Boşlukla ayır; ilk parça bitki türüdür ('Bell_pepper' tek parça kalır)
                        ilk_kelime = cn.split()[0].lower()
                        plants.add(ilk_kelime)

                    if plants:
                        bitki_turu = ", ".join(str(CLASS_TR.get(p, p.replace('_', ' ').capitalize())) for p in plants) if lang == "Türkçe" else ", ".join(str(p).replace('_', ' ').capitalize() for p in plants)
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
                            hastalik = ", ".join(set(sinif_ismi_ceviri(dis) for dis in sick))
                        else:
                            hastalik = ", ".join(set(sick))

                    skor = round(sum(det_conf)/len(det_conf), 2) if det_conf else 0.0
                    kullanici = st.session_state.get("aktif_kullanici", "Bilinmeyen Kullanıcı")

                    analizi_kaydet(kullanici, bitki_turu, hastalik, skor)
                    st.toast(T["toast_saved"])
                except Exception as e:
                    st.error(T["err_save"].format(e))
                # ────────────────────────────────────────

        if st.session_state.get("analiz_ok"):
            with col2:
                st.subheader(T['col2_sub'])
                det_cls  = st.session_state.classes
                det_conf = st.session_state.confs

                # Sınıf isimleri boşlukla ayrılır; ilk parça bitki türüdür
                # ('Bell_pepper' gibi alt çizgili terimler tek parça olarak aranır).
                plants = set([cn.split()[0] for cn in det_cls])
                plant_str = ""
                if plants:
                    plant_str = ", ".join(CLASS_TR.get(p.lower(), p.replace('_', ' ').capitalize()) for p in plants) if lang == "Türkçe" else ", ".join(p.replace('_', ' ').capitalize() for p in plants)
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
                        lang_key = "TR" if lang == "Türkçe" else "EN"

                        # Birincil (en yüksek güvenli) hastalığı seç ve verim kaybını
                        # Gemini'den al. Bu çağrı aşağıdaki öneri döngüsüyle aynı olduğu
                        # için önbellekten gelir — ekstra API maliyeti yoktur.
                        sick_ciftler = [(c, cf) for c, cf in zip(det_cls, det_conf)
                                        if any(k in c.lower() for k in dis_keys)]
                        birincil = max(sick_ciftler, key=lambda x: x[1])[0] if sick_ciftler else sick[0]

                        # Birincil hastalığı burada TEK sefer çek; hem verim kaybı metriği
                        # hem de aşağıdaki öneri kartı bunu kullansın. Böylece aynı hastalık
                        # için ikinci bir bekleme/spinner oluşmaz.
                        onbellek_oneri = {}
                        with st.spinner(T["spinner_report"]):
                            vk = oneri_getir(birincil, plant_str, lang_key)
                        onbellek_oneri[birincil] = vk

                        if vk and vk.get("verim_kaybi_seviye"):
                            seviye = vk.get("verim_kaybi_seviye", "")
                            aralik = vk.get("verim_kaybi_aralik", "")
                            aciklama = vk.get("verim_kaybi_aciklama", "")
                            st.metric(T["risk_label"], aralik)
                            st.markdown(
                                f"<div style='font-size:0.9rem;color:#334155;line-height:1.5;margin-top:2px;'>"
                                f"<b style='color:#0f172a;'>{T['vk_seviye']}:</b> "
                                f"<b>{seviye}</b> — {aciklama}</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            # Gemini yoksa/başarısızsa eski yaklaşık formüle düş
                            avg_conf = sum(det_conf) / len(det_conf)
                            risk = min(int(len(sick) * 15 * avg_conf) + 20, 95)
                            st.metric(T["risk_label"], f"%{risk}", f"-{risk}% Potansiyel Kayıp", delta_color="inverse")

                        st.write("")
                        st.markdown(T["plan_title"])

                        for dis in set(sick):
                            h = dis.lower()
                            display = sinif_ismi_ceviri(dis) if lang == "Türkçe" else dis

                            # Bulunan hastalığın İngilizce anahtar kelimesini belirle
                            db_key = "default"
                            arama_listesi = ["blight", "rust", "scab", "virus", "mold", "mildew", "spot", "rot", "scorch", "curl", "mite"]
                            
                            for k in arama_listesi:
                                if k in h:  # h, modelin bulduğu hastalık ismi (örn: 'grape_leaf_black_rot')
                                    db_key = k # Doğrudan o kelimeyi Firebase ID'si yap (rot ise rot)
                                    break

                            lang_key = "TR" if lang == "Türkçe" else "EN"

                            with st.expander(T["exp_title"].format(display), expanded=True):
                                # 1) Birincil hastalık yukarıda çekildiyse tekrar çekme/spinner gösterme;
                                #    değilse (ek hastalıklar) Gemini'den gerçek zamanlı çek.
                                if dis in onbellek_oneri:
                                    bilgi = onbellek_oneri[dis]
                                else:
                                    with st.spinner(T["spinner_advice"]):
                                        bilgi = oneri_getir(dis, plant_str, lang_key)

                                # 2) Gemini yoksa/başarısızsa mevcut Firestore statik verisine düş
                                if not bilgi:
                                    bilgi = hastalik_bilgisi_getir(db_key, lang_key)

                                # 3) Eksik anahtarlar varsa güvenli varsayılanlardan tamamla
                                fallback = { "ilac": T["db_err"], "sonuc": T["db_err"], "ekonomi": T["db_err"] }
                                bilgi = {**fallback, **bilgi}

                                st.markdown(f"**{T['lbl_ilac']}:** {bilgi.get('ilac','')}")
                                st.markdown(f"**{T['lbl_sonuc']}:** {bilgi.get('sonuc','')}")
                                st.markdown(f"**{T['lbl_ekonomi']}:** {bilgi.get('ekonomi','')}")
    else:
        # ── BOŞ DURUM ────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:16px 24px 8px 24px;">
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
            ">{T['step_title']}</h3>
            <p style="color:#64748b;font-size:0.94rem;margin:0;">
                {T['step_sub']}
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
                {T['features_label']}
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
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    {T['feature_high_acc_t']}
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    {T['feature_high_acc_d']}
                </div>
            </div>""", unsafe_allow_html=True)

        with f2:
            st.markdown(f"""
            <div style="{FEATURE_CARD}">
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    {T['feature_fast_t']}
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    {T['feature_fast_d']}
                </div>
            </div>""", unsafe_allow_html=True)

        with f3:
            st.markdown(f"""
            <div style="{FEATURE_CARD}">
                <div style="font-size:0.98rem;font-weight:700;color:#0f172a;margin-bottom:6px;">
                    {T['feature_smart_t']}
                </div>
                <div style="font-size:0.84rem;color:#64748b;line-height:1.6;">
                    {T['feature_smart_d']}
                </div>
            </div>""", unsafe_allow_html=True)

        st.write("")
        st.write("")
        st.markdown(f"""
        <div style="
            text-align:center;
            padding:24px 0 8px 0;
            border-top:1px solid #e5e7eb;
            margin-top:24px;
            width:100%;
        ">
            <p style="
                color:#94a3b8;
                font-size:0.8rem;
                margin:0 auto;
                font-weight:500;
                text-align:center;
                width:100%;
            ">
                {T['copyright']}
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  GEÇMİŞ ANALİZLERİM — Dashboard (KPI + Grafikler + Tablo)
# ══════════════════════════════════════════════════════════
def gecmis_analiz_sayfasi(T=None):
    # Ağır kütüphaneler yalnızca bu sayfa açıldığında import edilir (login'i yavaşlatmaz)
    import pandas as pd
    import plotly.express as px

    if T is None:
        T = LANGS[st.session_state.lang]

    # ── BAŞLIK BANNERI ────────────────────────────────────
    st.markdown(f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-radius:16px;
        padding:28px 32px;
        margin-bottom:22px;
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
            margin-bottom:12px;
        ">
            {T["hist_tag"]}
        </div>
        <h1 style="
            margin:0 0 8px 0;
            font-size:1.7rem;
            font-weight:800;
            color:#0f172a !important;
            letter-spacing:-0.03em;
            line-height:1.2;
        ">
            {T["hist_title"]}
        </h1>
        <p style="
            margin:0;
            font-size:0.94rem;
            color:#64748b !important;
            font-weight:400;
            line-height:1.55;
            max-width:680px;
        ">
            {T["hist_desc"]}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── AKTİF KULLANICI KONTROLÜ (Veri İzolasyonu) ────────
    aktif_kullanici = st.session_state.get("aktif_kullanici")
    if not aktif_kullanici:
        st.error(T["err_session"])
        return

    # ── VERİ ÇEKME (Sadece Aktif Kullanıcının Kayıtları) ──
    try:
        conn_dash = sqlite3.connect("tarimsal_analiz.db", check_same_thread=False)
        df = pd.read_sql_query(
            "SELECT * FROM analiz_gecmisi WHERE kullanici_adi = ?",
            conn_dash,
            params=[aktif_kullanici],
        )
        conn_dash.close()
    except Exception as e:
        st.error(T["err_db_read"].format(e))
        return

    if df.empty:
        st.info(T["info_empty"])
        return

    # Tarih kolonunu sıralamak için datetime'a çevir
    df["tarih"] = pd.to_datetime(df["tarih"], errors="coerce")

    # ══════════════════════════════════════════════════════
    #  ÜST KATMAN — KPI METRİKLERİ
    # ══════════════════════════════════════════════════════
    toplam_analiz = len(df)

    # En sık tespit edilen hastalık ("Sağlıklı" / "Healthy" ve "Tespit Edilemedi" hariç)
    hastalik_serisi = df["hastalik_durumu"].dropna()
    hastalik_serisi = hastalik_serisi[
        ~hastalik_serisi.str.lower().str.contains("sağlıklı", na=False)
        & ~hastalik_serisi.str.lower().str.contains("healthy", na=False)
        & ~hastalik_serisi.str.lower().str.contains("tespit edilemedi", na=False)
    ]
    if not hastalik_serisi.empty:
        en_sik_hastalik_tam_isim = hastalik_serisi.value_counts().idxmax()
    else:
        en_sik_hastalik_tam_isim = T["no_disease"]

    k1, k2 = st.columns(2)
    with k1:
        st.metric(label=T["kpi_total"], value=f"{toplam_analiz}")
    with k2:
        with st.expander(T["kpi_common"], expanded=False):
            st.markdown(f"<span style='color:#dc2626; font-weight:600;'>{en_sik_hastalik_tam_isim}</span>", unsafe_allow_html=True)

    st.write("")
    st.write("")

    # ══════════════════════════════════════════════════════
    #  ORTA KATMAN — GRAFİKLER (Bar + Donut)
    # ══════════════════════════════════════════════════════
    g1, g2 = st.columns(2, gap="large")

    # ── SOL: Bitki Dağılımı (Bar Chart) ──────────────────
    with g1:
        st.markdown(f"""
        <div style="margin-bottom:8px;">
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;letter-spacing:-0.01em;">
                {T["chart1_t"]}
            </div>
            <div style="font-size:0.78rem;color:#94a3b8;font-weight:500;margin-top:2px;">
                {T["chart1_d"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        bitki_sayim = (
            df["bitki_turu"]
            .fillna("Bilinmiyor")
            .value_counts()
            .reset_index()
        )
        bitki_sayim.columns = [T["chart_plant"], T["chart_count"]]

        fig_bar = px.bar(
            bitki_sayim,
            x=T["chart_plant"],
            y=T["chart_count"],
            color_discrete_sequence=["#7DA78C"],
            text_auto=True
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_family="Inter, sans-serif",
            margin=dict(l=10, r=10, t=10, b=10),
            height=360,
            xaxis=dict(showgrid=False, title=None, tickfont=dict(color="#000000", size=12)),
            yaxis=dict(gridcolor="#e5e7eb", title=None, tickfont=dict(color="#000000", size=12)),
        )
        fig_bar.update_traces(
            textfont_size=12, textangle=0, textposition="outside", cliponaxis=False,
            marker_line_width=0,
            hovertemplate=f"<b>%{{x}}</b><br>{T['chart_count']}: %{{y}}<extra></extra>"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── SAĞ: Sağlıklı vs Enfekte (Donut Chart) ──────────
        with g2:
            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <div style="font-size:0.95rem;font-weight:700;color:#0f172a;letter-spacing:-0.01em;">
                    {T["chart2_t"]}
                </div>
                <div style="font-size:0.78rem;color:#94a3b8;font-weight:500;margin-top:2px;">
                    {T["chart2_d"]}
                </div>
            </div>
            """, unsafe_allow_html=True)

            saglikli_mask = (
                df["hastalik_durumu"].fillna("").str.lower().str.contains("sağlıklı")
                | df["hastalik_durumu"].fillna("").str.lower().str.contains("healthy")
            )
            saglikli_n = int(saglikli_mask.sum())
            enfekte_n = int((~saglikli_mask).sum())

            donut_df = pd.DataFrame({
                T["chart_status"]: [T["status_healthy"], T["status_infected"]],
                T["chart_quantity"]: [saglikli_n, enfekte_n],
            })

            fig_donut = px.pie(
                donut_df,
                names=T["chart_status"],
                values=T["chart_quantity"],
                hole=0.55,
                color=T["chart_status"],
                color_discrete_map={T["status_healthy"]: "#7DA78C", T["status_infected"]: "#dc2626"},
            )

            fig_donut.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_family="Inter, sans-serif",
                margin=dict(l=10, r=10, t=50, b=10),
                height=360,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color="#000000")),
            )

            fig_donut.update_traces(
                textinfo="percent+label",
                textfont_size=14,
                textfont_color="#000000",
                textposition="auto",
                marker=dict(line=dict(color="#ffffff", width=2)),
                hovertemplate="<b>%{label}</b><br>%{value}<br>%{percent}<extra></extra>",
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    # ══════════════════════════════════════════════════════
    #  ALT KATMAN — DETAYLI VERİ TABLOSU
    # ══════════════════════════════════════════════════════
    st.markdown(f"""
    <div style="margin-bottom:10px;">
        <div style="font-size:0.95rem;font-weight:700;color:#0f172a;letter-spacing:-0.01em;">
            {T["table_t"]}
        </div>
        <div style="font-size:0.78rem;color:#94a3b8;font-weight:500;margin-top:2px;">
            {T["table_d"]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_tablo = df.sort_values(by="tarih", ascending=False).reset_index(drop=True)

    st.markdown("""
    <style>
        [data-testid="stDataFrame"] div { color: #0f172a !important; font-weight: 500 !important; }
        [data-testid="stDataFrame"] th { color: #0f172a !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.dataframe(
        df_tablo,
        use_container_width=True,
        hide_index=True,
        column_config={
            "islem_id": None,
            "guven_skoru": None,
            "kullanici_adi": st.column_config.TextColumn(T["col_user"]),
            "bitki_turu": st.column_config.TextColumn(T["col_plant"]),
            "hastalik_durumu": st.column_config.TextColumn(T["col_disease"]),
            "tarih": st.column_config.DatetimeColumn(
                T["col_date"],
                format=T["date_format"],
            ),
        },
    )

    st.write("")

    # ══════════════════════════════════════════════════════
    #  KAYIT YÖNETİMİ — Toplu Silme İşlemi
    # ══════════════════════════════════════════════════════
    with st.expander(T["delete_exp"], expanded=False):
        st.markdown(
            f"<div style='font-size:0.85rem;color:#64748b;margin-bottom:10px;'>{T['delete_desc']}</div>",
            unsafe_allow_html=True,
        )

        secenek_df = df_tablo[["islem_id", "tarih", "bitki_turu", "hastalik_durumu"]].copy()
        secenek_df["tarih_str"] = secenek_df["tarih"].dt.strftime("%d.%m.%Y %H:%M")

        etiket_haritasi = {
            int(row["islem_id"]):
                f"{row['tarih_str']}  |  {row['bitki_turu']}  →  {row['hastalik_durumu']}"
            for _, row in secenek_df.iterrows()
        }

        secilen_idler = st.multiselect(
            T["delete_label"],
            options=list(etiket_haritasi.keys()),
            format_func=lambda x: etiket_haritasi[x],
            key="silinecek_kayitlar_secimi",
            placeholder=T["delete_ph"]
        )

        if secilen_idler:
            st.info(T["delete_count"].format(len(secilen_idler)))

        sil_btn = st.button(
            T["delete_btn"],
            key="kayit_sil_btn",
            type="primary",
            use_container_width=True,
        )

        if sil_btn and secilen_idler:
            try:
                conn_sil = sqlite3.connect("tarimsal_analiz.db", check_same_thread=False)
                c_sil = conn_sil.cursor()

                placeholders = ','.join(['?'] * len(secilen_idler))
                query = f"DELETE FROM analiz_gecmisi WHERE islem_id IN ({placeholders}) AND kullanici_adi = ?"

                params = [int(sid) for sid in secilen_idler] + [aktif_kullanici]

                c_sil.execute(query, params)
                etkilenen = c_sil.rowcount
                conn_sil.commit()
                conn_sil.close()

                if etkilenen > 0:
                    st.toast(T["delete_ok"].format(etkilenen))
                    st.rerun()
                else:
                    st.warning(T["delete_warn"])
            except Exception as e:
                st.error(T["delete_err"].format(e))

# ══════════════════════════════════════════════════════════
#  UYGULAMA YÖNLENDİRİCİ
# ══════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    login_page()
else:
    main_app()