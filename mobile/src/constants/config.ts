// API adresi. gerçek telefonda test ederken localhost çalışmıyor,
// bilgisayarın yerel IP'sini yazmak lazım (örn: http://192.168.1.100:8000)
export const API_BASE_URL = 'http://192.168.1.176:8000';

export const API_ENDPOINTS = {
  ANALYZE: `${API_BASE_URL}/analyze`,
  LOGIN: `${API_BASE_URL}/login`,
  REGISTER: `${API_BASE_URL}/register`,
  HISTORY: `${API_BASE_URL}/history`,
  HISTORY_DELETE: `${API_BASE_URL}/history/delete`,
};

export const DEFAULT_CONFIDENCE = 0.25;

// Analizde kullanılacak model dosyası.
// backend şu an modeli global yüklüyor ama ileride seçim eklersek diye
// isteğe bu alanı da koyuyorum.
export const ANALYSIS_MODEL = 'plantdoc_150epoch.pt';
