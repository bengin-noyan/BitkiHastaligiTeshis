// API sunucu adresi — geliştirme ortamı için localhost
// Gerçek cihazda test için bilgisayarınızın yerel IP adresini kullanın
// Örnek: export const API_BASE_URL = 'http://192.168.1.100:8000';
export const API_BASE_URL = 'http://192.168.1.176:8000';

export const API_ENDPOINTS = {
  ANALYZE: `${API_BASE_URL}/analyze`,
  LOGIN: `${API_BASE_URL}/login`,
};

export const DEFAULT_CONFIDENCE = 0.25;

// Analiz için kullanılacak YOLOv8 model dosyası.
// Backend (api_server.py) şu an modeli global yüklüyor; bu parametre
// isteğe eklenir ki ileride backend model seçimini destekleyebilsin.
export const ANALYSIS_MODEL = 'plantdoc_150epoch.pt';
