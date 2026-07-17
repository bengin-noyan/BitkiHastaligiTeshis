import axios from 'axios';
import {
  API_ENDPOINTS,
  DEFAULT_CONFIDENCE,
  ANALYSIS_MODEL,
} from '../constants/config';

// ─── Type Definitions ────────────────────────────────────────────────

export interface Detection {
  class_name: string;
  class_name_tr: string;
  confidence: number;
}

export interface Disease {
  name: string;
  name_tr: string;
  treatment_tr: { ilac: string; sonuc: string; ekonomi: string };
  treatment_en: { ilac: string; sonuc: string; ekonomi: string };
}

export interface AnalysisSummary {
  plant_types: string[];
  plant_types_tr: string[];
  is_healthy: boolean;
  disease_count: number;
  risk_score: number;
  diseases: Disease[];
}

export interface AnalysisResult {
  success: boolean;
  detections: Detection[];
  // Kutucuklu (bounding box) teşhis görselinin tam data URI'si
  // (data:image/jpeg;base64,...)
  image_base64: string;
  // Geriye dönük uyumluluk için korunan eski anahtar
  result_image_base64?: string;
  summary: AnalysisSummary;
}

export interface LoginResult {
  success: boolean;
  username: string;
}

// ─── API Client ──────────────────────────────────────────────────────

const apiClient = axios.create({
  timeout: 60000,
  headers: {
    Accept: 'application/json',
  },
});

// Anlık ağ kopmalarına (telefon Wi-Fi güç tasarrufu, ilk isteğin yavaşlığı)
// karşı dayanıklılık: SADECE yanıt alınamayan ağ hatalarında birkaç kez
// yeniden dener. Sunucudan HTTP yanıtı geldiyse (4xx/5xx) tekrar denemez.
function isTransientNetworkError(error: any): boolean {
  // error.response varsa sunucu yanıt vermiştir → yeniden deneme.
  // ECONNABORTED (zaman aşımı) da yeniden denenmez; kullanıcıya bilgi verilir.
  return !error?.response && error?.code !== 'ECONNABORTED';
}

async function withRetry<T>(
  fn: () => Promise<T>,
  retries = 2,
  delayMs = 900
): Promise<T> {
  let lastError: any;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await fn();
    } catch (error: any) {
      lastError = error;
      if (attempt < retries && isTransientNetworkError(error)) {
        await new Promise((resolve) => setTimeout(resolve, delayMs));
        continue;
      }
      throw error;
    }
  }
  throw lastError;
}

// ─── Login ───────────────────────────────────────────────────────────

export async function login(
  username: string,
  password: string
): Promise<LoginResult> {
  try {
    const response = await withRetry(() =>
      apiClient.post<LoginResult>(
        API_ENDPOINTS.LOGIN,
        { username, password },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 15000,
        }
      )
    );
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(
        error.response.data?.detail ||
          'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('Bağlantı zaman aşımına uğradı. Tekrar deneyin.');
    }
    throw new Error(
      'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.'
    );
  }
}

// ─── Analyze Image ───────────────────────────────────────────────────

export async function analyzeImage(
  imageUri: string,
  confidence?: number,
  model: string = ANALYSIS_MODEL
): Promise<AnalysisResult> {
  try {
    const formData = new FormData();

    // Extract filename and determine MIME type
    const uriParts = imageUri.split('/');
    const filename = uriParts[uriParts.length - 1] || 'photo.jpg';
    const extension = filename.split('.').pop()?.toLowerCase() || 'jpg';

    const mimeTypes: Record<string, string> = {
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      gif: 'image/gif',
      webp: 'image/webp',
      bmp: 'image/bmp',
    };
    const mimeType = mimeTypes[extension] || 'image/jpeg';

    // Append the image file
    formData.append('file', {
      uri: imageUri,
      name: filename,
      type: mimeType,
    } as any);

    // Append confidence threshold
    formData.append('confidence', String(confidence || DEFAULT_CONFIDENCE));

    // Analiz için kullanılacak modeli parametre olarak gönder
    // (plantdoc_150epoch.pt). Backend bu alanı okumasa da istek bozulmaz.
    formData.append('model', model);

    const response = await withRetry(() =>
      apiClient.post<AnalysisResult>(
        API_ENDPOINTS.ANALYZE,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000,
        }
      )
    );

    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new Error(
        error.response.data?.detail ||
          'Analiz sırasında bir hata oluştu. Tekrar deneyin.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error(
        'Analiz zaman aşımına uğradı. Fotoğraf boyutunu küçültüp tekrar deneyin.'
      );
    }
    throw new Error(
      'Sunucuya bağlanılamadı. İnternet bağlantınızı ve sunucu adresini kontrol edin.'
    );
  }
}
