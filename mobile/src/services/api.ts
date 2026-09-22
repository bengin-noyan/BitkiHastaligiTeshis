import axios from 'axios';
import {
  API_ENDPOINTS,
  DEFAULT_CONFIDENCE,
  ANALYSIS_MODEL,
} from '../constants/config';

// ----- tipler -----

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
  // kutucuklu görselin tam data uri'si (data:image/jpeg;base64,...)
  image_base64: string;
  // eski anahtar, silmedim çünkü eski sürümler hâlâ bunu okuyor
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

// ----- hata tipi -----

/**
 * Hataları dilden bağımsız bir `code` ile taşıyorum, ekranlar bu koda bakıp
 * kendi dilindeki metni basıyor (bkz. constants/i18n.ts, apiErrorText).
 * `message` alanında yine türkçe varsayılan metin duruyor.
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

// ----- api client -----

const apiClient = axios.create({
  timeout: 60000,
  headers: {
    Accept: 'application/json',
  },
});

// telefonun wifi'si uyuyunca ya da ilk istek yavaş olunca bağlantı kopabiliyor.
// sadece sunucudan hiç cevap gelmeyen durumlarda birkaç kez tekrar deniyoruz.
// 4xx/5xx döndüyse sunucu ayakta demektir, tekrar denemeye gerek yok.
function isTransientNetworkError(error: any): boolean {
  // error.response doluysa sunucu cevap vermiş, tekrar deneme.
  // ECONNABORTED (timeout) da tekrar denenmiyor, kullanıcıya haber veriyoruz.
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

// ----- login -----

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

// ----- register -----

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

// ----- history -----

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

// ----- analiz -----

export async function analyzeImage(
  imageUri: string,
  confidence?: number,
  model: string = ANALYSIS_MODEL,
  // geçmişe kaydedebilmek için kullanıcı adı ve dil de gidiyor
  username?: string,
  lang: 'tr' | 'en' = 'tr'
): Promise<AnalysisResult> {
  try {
    const formData = new FormData();

    // dosya adından uzantıyı alıp mime type'ı buluyoruz
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

    // görseli ekle
    formData.append('file', {
      uri: imageUri,
      name: filename,
      type: mimeType,
    } as any);

    // güven eşiği
    formData.append('confidence', String(confidence || DEFAULT_CONFIDENCE));

    // hangi modelle analiz edilecek. backend şu an bunu okumuyor ama
    // göndermek bir şeyi bozmuyor, ileride lazım olur.
    formData.append('model', model);

    // dil hem kutucuk etiketlerini hem geçmiş kaydını etkiliyor
    formData.append('lang', lang);

    // kullanıcı adı gönderilirse backend sonucu analiz_gecmisi'ne yazıyor
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
