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

export interface RegisterResult {
  success: boolean;
  message: string;
}

export interface HistoryRecord {
  islem_id: number;
  bitki_turu: string;
  hastalik_durumu: string;
  guven_skoru: number;
  tarih: string;
}

export interface HistoryResult {
  success: boolean;
  records: HistoryRecord[];
  message?: string;
}

export interface HistoryDeleteResult {
  success: boolean;
  deleted: number;
  message?: string;
}

// ─── Hata tipi ───────────────────────────────────────────────────────

/**
 * Ağ/sunucu hatalarını dilden bağımsız bir `code` ile taşır; ekranlar bu kodu
 * seçili dile göre metne çevirir (bkz. constants/i18n.ts → apiErrorText).
 * `message` alanı Türkçe varsayılan metni tutmaya devam eder.
 */
export type ApiErrorCode = 'network' | 'timeout' | 'server';

export class ApiError extends Error {
  code: ApiErrorCode;

  constructor(code: ApiErrorCode, message: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
  }
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
      throw new ApiError(
        'server',
        error.response.data?.detail ||
          'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'timeout',
        'Bağlantı zaman aşımına uğradı. Tekrar deneyin.'
      );
    }
    throw new ApiError(
      'network',
      'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.'
    );
  }
}

// ─── Register ────────────────────────────────────────────────────────

export async function register(
  username: string,
  password: string
): Promise<RegisterResult> {
  try {
    const response = await withRetry(() =>
      apiClient.post<RegisterResult>(
        API_ENDPOINTS.REGISTER,
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
      throw new ApiError(
        'server',
        error.response.data?.detail || 'Kayıt başarısız. Lütfen tekrar deneyin.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'timeout',
        'Bağlantı zaman aşımına uğradı. Tekrar deneyin.'
      );
    }
    throw new ApiError(
      'network',
      'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.'
    );
  }
}

// ─── History ─────────────────────────────────────────────────────────

export async function fetchHistory(username: string): Promise<HistoryResult> {
  try {
    const response = await withRetry(() =>
      apiClient.get<HistoryResult>(API_ENDPOINTS.HISTORY, {
        params: { username },
        timeout: 15000,
      })
    );
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new ApiError(
        'server',
        error.response.data?.detail || 'Kayıtlar okunamadı.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'timeout',
        'Bağlantı zaman aşımına uğradı. Tekrar deneyin.'
      );
    }
    throw new ApiError(
      'network',
      'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.'
    );
  }
}

export async function deleteHistoryRecords(
  username: string,
  ids: number[]
): Promise<HistoryDeleteResult> {
  try {
    const response = await withRetry(() =>
      apiClient.post<HistoryDeleteResult>(
        API_ENDPOINTS.HISTORY_DELETE,
        { username, ids },
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 15000,
        }
      )
    );
    return response.data;
  } catch (error: any) {
    if (error.response) {
      throw new ApiError(
        'server',
        error.response.data?.detail || 'Kayıtlar silinemedi.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'timeout',
        'Bağlantı zaman aşımına uğradı. Tekrar deneyin.'
      );
    }
    throw new ApiError(
      'network',
      'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.'
    );
  }
}

// ─── Analyze Image ───────────────────────────────────────────────────

export async function analyzeImage(
  imageUri: string,
  confidence?: number,
  model: string = ANALYSIS_MODEL,
  // Analizi geçmişe kaydetmek için: kullanıcı adı ve kayıt metinlerinin dili
  username?: string,
  lang: 'tr' | 'en' = 'tr'
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

    // Dil, kutucuk etiketlerinin ve geçmiş kaydının dilini belirler.
    formData.append('lang', lang);

    // Kullanıcı adı gönderilirse backend sonucu analiz_gecmisi tablosuna yazar.
    if (username) {
      formData.append('username', username);
    }

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
      throw new ApiError(
        'server',
        error.response.data?.detail ||
          'Analiz sırasında bir hata oluştu. Tekrar deneyin.'
      );
    }
    if (error.code === 'ECONNABORTED') {
      throw new ApiError(
        'timeout',
        'Analiz zaman aşımına uğradı. Fotoğraf boyutunu küçültüp tekrar deneyin.'
      );
    }
    throw new ApiError(
      'network',
      'Sunucuya bağlanılamadı. İnternet bağlantınızı ve sunucu adresini kontrol edin.'
    );
  }
}
