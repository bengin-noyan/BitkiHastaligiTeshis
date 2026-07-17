// ─────────────────────────────────────────────────────────────────────
// Tasarım teması — app.py (Streamlit) arayüzünün paletiyle birebir aynı.
// Renk/tipografi tokenları tek yerde toplanır ki mobil ve web görünümü
// aynı "sade & şık" dili paylaşsın. app.py'deki :root CSS değişkenlerinin
// React Native karşılığıdır.
// ─────────────────────────────────────────────────────────────────────

export const COLORS = {
  // Ana renk (adaçayı yeşili)
  primary: '#7DA78C',
  primaryDark: '#6A937A',
  primarySoft: '#f0f5f2',
  primaryBorder: '#c5dccd',
  primaryText: '#4a6e57',

  // Başarı / sağlıklı (zümrüt) — app.py'nin ecfdf5 / a7f3d0 / 065f46 üçlüsü
  success: '#065f46',
  successSoft: '#ecfdf5',
  successBorder: '#a7f3d0',

  // Uyarı (amber)
  amber: '#d97706',
  amberSoft: '#fffbeb',
  amberBorder: '#fde68a',

  // Hata / yüksek risk (kırmızı)
  red: '#dc2626',
  redSoft: '#fef2f2',
  redBorder: '#fecaca',

  // Metin tonları
  textDark: '#0f172a',
  textMid: '#334155',
  textSoft: '#64748b',
  textMuted: '#94a3b8',

  // Zemin & yüzeyler
  bgPage: '#fafafa',
  bgCard: '#ffffff',
  border: '#e5e7eb',
  borderSoft: '#f3f4f6',
  inputBg: '#f8faf8',

  white: '#ffffff',
} as const;

// app.py'nin yeşil tonlu yumuşak gölgesi: rgba(125,167,140, x)
export const SHADOW_TINT = '#7DA78C';

// Inter font ailesi — _layout.tsx içinde yüklenir.
export const FONTS = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semibold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
  extrabold: 'Inter_800ExtraBold',
  black: 'Inter_900Black',
} as const;

// Risk skoru rengi — app.py mantığıyla: düşük=yeşil, orta=amber, yüksek=kırmızı
export const riskColor = (score: number): string => {
  if (score < 30) return COLORS.primary;
  if (score < 60) return COLORS.amber;
  return COLORS.red;
};
