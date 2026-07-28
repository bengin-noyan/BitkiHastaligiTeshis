// ─────────────────────────────────────────────────────────────────────
// Tasarım teması — app.py (Streamlit) arayüzünün paletiyle birebir aynı.
// Renk/tipografi tokenları tek yerde toplanır ki mobil ve web görünümü
// aynı "sade & şık" dili paylaşsın. app.py'deki :root CSS değişkenlerinin
// React Native karşılığıdır.
// ─────────────────────────────────────────────────────────────────────

export const COLORS = {
  // Ana renk — canlı/parlak yeşil (app.py :root --primary ile birebir)
  primary: '#2FA85A',
  primaryDark: '#248C49',
  primarySoft: '#e7f7ee',
  primaryBorder: '#a6e2be',
  primaryText: '#1e7d42',

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

  // Bilgi (mavi) — tedavi kalemlerini ayırt etmek için ölçülü aksan
  info: '#2563eb',

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
  // Giriş alanları — app.py login formundaki açık-gri zemin + belirgin kenarlık
  inputBg: '#eef2f7',
  inputBorder: '#cbd5e1',

  // Koyu yeşil admin-panel tonları (app.py sidebar temasının karşılığı)
  darkGreen: '#1c4030',
  darkGreenMid: '#14301f',
  darkGreenDeep: '#10241b',
  darkGreenActive: '#2e7d50',
  darkGreenText: '#cddbd2',
  darkGreenMuted: '#7d9a8a',

  white: '#ffffff',
} as const;

// app.py'nin gölgesi: rgba(15,23,42, x) — slate/lacivert tonlu, yeşil değil
export const SHADOW_TINT = '#0f172a';

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
