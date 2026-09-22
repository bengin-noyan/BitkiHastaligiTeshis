// Renkler ve fontlar tek yerde dursun diye burada topladım.
// app.py'deki :root css değişkenlerinin react native hali,
// mobil ve web aynı görünsün diye aynı değerleri kullanıyorum.

export const COLORS = {
  // ana renk (app.py'deki --primary ile aynı)
  primary: '#2FA85A',
  primaryDark: '#248C49',
  primarySoft: '#e7f7ee',
  primaryBorder: '#a6e2be',
  primaryText: '#1e7d42',

  // başarı / sağlıklı
  success: '#065f46',
  successSoft: '#ecfdf5',
  successBorder: '#a7f3d0',

  // uyarı
  amber: '#d97706',
  amberSoft: '#fffbeb',
  amberBorder: '#fde68a',

  // hata / yüksek risk
  red: '#dc2626',
  redSoft: '#fef2f2',
  redBorder: '#fecaca',

  // bilgi mavisi, tedavi maddelerini ayırmak için
  info: '#2563eb',

  // yazı renkleri
  textDark: '#0f172a',
  textMid: '#334155',
  textSoft: '#64748b',
  textMuted: '#94a3b8',

  // zemin ve kartlar
  bgPage: '#fafafa',
  bgCard: '#ffffff',
  border: '#e5e7eb',
  borderSoft: '#f3f4f6',
  // input'lar (app.py login formundaki açık gri zemin)
  inputBg: '#eef2f7',
  inputBorder: '#cbd5e1',

  // sidebar'ın koyu yeşil tonları
  darkGreen: '#1c4030',
  darkGreenMid: '#14301f',
  darkGreenDeep: '#10241b',
  darkGreenActive: '#2e7d50',
  darkGreenText: '#cddbd2',
  darkGreenMuted: '#7d9a8a',

  white: '#ffffff',
} as const;

// app.py'de gölge rgba(15,23,42,x), yani lacivert tonlu. yeşil gölge kullanmıyoruz
export const SHADOW_TINT = '#0f172a';

// Inter fontu _layout.tsx içinde yükleniyor
export const FONTS = {
  regular: 'Inter_400Regular',
  medium: 'Inter_500Medium',
  semibold: 'Inter_600SemiBold',
  bold: 'Inter_700Bold',
  extrabold: 'Inter_800ExtraBold',
  black: 'Inter_900Black',
} as const;

// risk skoruna göre renk: düşük yeşil, orta sarı, yüksek kırmızı
export const riskColor = (score: number): string => {
  if (score < 30) return COLORS.primary;
  if (score < 60) return COLORS.amber;
  return COLORS.red;
};
