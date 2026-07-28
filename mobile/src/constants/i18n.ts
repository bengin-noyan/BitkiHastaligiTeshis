// ─────────────────────────────────────────────────────────────────────
// Çoklu dil sözlüğü — app.py'deki LANGS yapısının mobil karşılığı.
// Anahtar adları mümkün olduğunca app.py ile aynı tutuldu ki iki taraf
// birlikte güncellenebilsin.
// ─────────────────────────────────────────────────────────────────────

export type Lang = 'tr' | 'en';

export const LANG_OPTIONS: { key: Lang; label: string }[] = [
  { key: 'tr', label: 'Türkçe' },
  { key: 'en', label: 'English' },
];

const tr = {
  // ── Giriş ekranı ──
  lang_label: 'Dil / Language',
  tab_login: 'Giriş Yap',
  tab_register: 'Kayıt Ol',
  username: 'Kullanıcı Adı',
  password: 'Şifre',
  username_ph: 'Kullanıcı adınızı girin',
  password_ph: 'Şifrenizi girin',
  new_username: 'Yeni Kullanıcı Adı',
  new_password: 'Yeni Şifre',
  confirm_password: 'Şifre Doğrulama',
  new_username_ph: 'Bir kullanıcı adı belirleyin',
  new_password_ph: 'Bir şifre belirleyin',
  confirm_password_ph: 'Şifrenizi tekrar girin',
  btn_login: 'Giriş Yap',
  btn_register: 'Kayıt Ol',
  loading_login: 'Giriş yapılıyor...',
  loading_register: 'Kaydediliyor...',
  err_enter_user: 'Lütfen kullanıcı adınızı girin.',
  err_enter_pass: 'Lütfen şifrenizi girin.',
  err_invalid: 'Kullanıcı adı veya şifre hatalı!',
  warn_fill_all: 'Lütfen tüm alanları doldurun.',
  err_mismatch: 'Şifreler eşleşmiyor, lütfen kontrol edin!',
  err_user_taken: 'Bu kullanıcı adı zaten alınmış. Lütfen farklı bir tane deneyin.',
  err_generic: 'Bir hata oluştu. Lütfen tekrar deneyin.',
  err_register: 'Kayıt sırasında bir hata oluştu.',
  err_network: 'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.',
  err_timeout: 'Bağlantı zaman aşımına uğradı. Tekrar deneyin.',
  success_reg:
    "Harika! {} başarıyla kaydedildi. 'Giriş Yap' sekmesinden giriş yapabilirsin.",
  pill_accuracy: 'Doğruluk',
  pill_analysis: 'Analiz',
  pill_classes: 'Analiz Sınıfı',
  copyright: '© 2026 PlantDetective · Tüm hakları saklıdır',

  // ── Ana ekran (analiz) ──
  header_sub: 'Bitki hastalığı teşhisi & tarımsal verimlilik analizi',
  btn_logout: 'Çıkış',
  logout_title: 'Çıkış',
  logout_msg: 'Çıkış yapmak istediğinize emin misiniz?',
  cancel: 'İptal',
  logout_confirm: 'Çıkış Yap',
  greeting: 'Hoş geldiniz, ',
  sec_photo: 'Fotoğraf',
  photo_ph: 'Yaprak fotoğrafı çekin veya seçin',
  photo_hint: 'Aşağıdaki butonları kullanarak başlayın',
  btn_camera: 'Kamera',
  btn_gallery: 'Galeri',
  btn_analyze: 'Analiz Et',
  analyzing: 'Analiz ediliyor...',
  perm_title: 'İzin Gerekli',
  perm_camera: 'Fotoğraf çekebilmek için kamera izni vermeniz gerekmektedir.',
  perm_gallery: 'Galeriye erişebilmek için fotoğraf izni vermeniz gerekmektedir.',
  ok: 'Tamam',
  err_camera: 'Kamera açılırken bir hata oluştu.',
  err_gallery: 'Galeri açılırken bir hata oluştu.',
  err_analyze: 'Analiz sırasında beklenmeyen bir hata oluştu.',

  // ── Sonuçlar ──
  results_title: 'Analiz Sonuçları',
  res_plant: 'Tespit Edilen Bitki',
  no_plant: 'Bitki türü tespit edilemedi',
  res_health: 'Sağlık Durumu',
  healthy: 'Sağlıklı',
  diseases_found: '{} Hastalık Tespit Edildi',
  risk_label: 'Tahmini Verim Kaybı',
  risk_low: 'Düşük Kayıp',
  risk_mid: 'Orta Kayıp',
  risk_high: 'Yüksek Kayıp',
  res_detections: 'Tespit Detayları',
  disease_section: 'Hastalık Bilgileri ve Tedavi Önerileri',
  lbl_ilac: 'Önerilen İlaç',
  lbl_sonuc: 'Zirai Beklenti',
  lbl_ekonomi: 'Finansal Etki',
  no_info: 'Bilgi mevcut değil',
  btn_new_analysis: 'Yeni Analiz',

  // ── Navigasyon (app.py sidebar menüsü) ──
  nav_home: 'Ana Sayfa / Analiz',
  nav_history: 'Geçmiş Analizlerim',

  // ── Ana sayfa vitrin bölümü ──
  nav_powered: 'YAPAY ZEKÂ DESTEKLİ',
  main_title: 'Bitki Hastalığı Teşhis Sistemi',
  main_desc:
    'Yaprak fotoğrafını yükle, YOLOv8 modeli saniyeler içinde hastalığı tespit etsin; tedavi önerisi ve verim kaybı tahminiyle birlikte raporunu al.',
  kpi_acc: 'Model Doğruluğu',
  kpi_acc_d: 'YOLOv8 Medium',
  kpi_time: 'Analiz Süresi',
  kpi_time_d: 'Gerçek zamanlı',
  kpi_dis: 'Analiz Sınıfı',
  kpi_dis_d: 'PlantDoc veri seti',
  kpi_plants: 'Desteklenen Bitki',
  kpi_plants_d: 'Ürün çeşidi',
  conf_label: 'Güven Eşiği',
  conf_hint:
    'Eşiği yükseltirsen yalnızca kesin tespitler gösterilir; düşürürsen daha fazla tespit çıkar ama yanlış tespit riski artar.',
  how_title: 'Üç adımda teşhis',
  step1_t: 'Fotoğraf Yükle',
  step1_d: 'Şüpheli yaprağı doğal ışıkta, net biçimde fotoğrafla.',
  step2_t: 'Yapay Zekâ Analiz Etsin',
  step2_d: 'YOLOv8 modeli saniyeler içinde bitkiyi ve hastalığı tanır.',
  step3_t: 'Raporu İncele',
  step3_d: 'Teşhis, tedavi önerisi ve verim kaybı tahmini anında ekranda.',

  // ── Geçmiş analizler sayfası ──
  hist_tag: 'ANALİZ GEÇMİŞİ',
  hist_title: 'Geçmiş Analizlerim',
  hist_desc:
    'Veritabanında saklanan tüm analizlerinin özeti, dağılımı ve detaylı kayıt listesi.',
  hist_loading: 'Kayıtlar yükleniyor...',
  info_empty:
    'Henüz kayıtlı analizin yok. Ana sayfadan ilk analizini yap, sonuçlar burada görünsün.',
  err_db_read: 'Kayıtlar okunamadı.',
  err_session: 'Oturum bilgisi alınamadı. Lütfen tekrar giriş yapın.',
  kpi_total: 'Toplam Analiz Sayısı',
  kpi_common: 'En Sık Tespit Edilen Hastalık',
  no_disease: 'Tespit edilen hastalık bulunamadı.',
  chart1_t: 'Bitki Türü Dağılımı',
  chart1_d: 'Analiz edilen ürünlerin sıklık dağılımı',
  chart2_t: 'Sağlık Durumu Oranı',
  chart2_d: 'Sağlıklı ve enfekte örneklerin genel dağılımı',
  status_healthy: 'Sağlıklı',
  status_infected: 'Enfekte',
  table_t: 'Detaylı Analiz Kayıtları',
  table_d: 'Tüm kayıtlar en yeniden eskiye sıralanır',
  select_mode: 'Seç',
  select_cancel: 'Vazgeç',
  delete_count: '{} kayıt seçildi',
  delete_btn: 'Seçili Kayıtları Sil',
  delete_title: 'Kayıtları Sil',
  delete_confirm: '{} kayıt kalıcı olarak silinecek. Onaylıyor musun?',
  delete_ok: '{} kayıt silindi.',
  delete_err: 'Kayıtlar silinemedi.',
  refresh: 'Yenile',
};

// İngilizce sözlük — anahtarlar Türkçe sözlükle birebir aynı olmak zorunda
// (TypeScript bunu derleme anında denetler).
const en: typeof tr = {
  // ── Login screen ──
  lang_label: 'Dil / Language',
  tab_login: 'Sign In',
  tab_register: 'Sign Up',
  username: 'Username',
  password: 'Password',
  username_ph: 'Enter your username',
  password_ph: 'Enter your password',
  new_username: 'New Username',
  new_password: 'New Password',
  confirm_password: 'Confirm Password',
  new_username_ph: 'Choose a username',
  new_password_ph: 'Choose a password',
  confirm_password_ph: 'Re-enter your password',
  btn_login: 'Sign In',
  btn_register: 'Sign Up',
  loading_login: 'Signing in...',
  loading_register: 'Registering...',
  err_enter_user: 'Please enter your username.',
  err_enter_pass: 'Please enter your password.',
  err_invalid: 'Invalid username or password.',
  warn_fill_all: 'Please fill in all fields.',
  err_mismatch: 'Passwords do not match, please check!',
  err_user_taken: 'This username is already taken. Please try a different one.',
  err_generic: 'An error occurred. Please try again.',
  err_register: 'An error occurred during registration.',
  err_network: 'Could not reach the server. Please check your connection.',
  err_timeout: 'The request timed out. Please try again.',
  success_reg:
    "Great! {} has been registered successfully. You can sign in from the 'Sign In' tab.",
  pill_accuracy: 'Accuracy',
  pill_analysis: 'Analysis',
  pill_classes: 'Disease Classes',
  copyright: '© 2026 PlantDetective · All rights reserved',

  // ── Home screen (analysis) ──
  header_sub: 'Plant disease diagnosis & agricultural productivity analysis',
  btn_logout: 'Sign Out',
  logout_title: 'Sign Out',
  logout_msg: 'Are you sure you want to sign out?',
  cancel: 'Cancel',
  logout_confirm: 'Sign Out',
  greeting: 'Welcome, ',
  sec_photo: 'Photo',
  photo_ph: 'Take or choose a leaf photo',
  photo_hint: 'Use the buttons below to get started',
  btn_camera: 'Camera',
  btn_gallery: 'Gallery',
  btn_analyze: 'Analyze',
  analyzing: 'Analyzing...',
  perm_title: 'Permission Required',
  perm_camera: 'Camera permission is required to take photos.',
  perm_gallery: 'Photo library permission is required to access the gallery.',
  ok: 'OK',
  err_camera: 'An error occurred while opening the camera.',
  err_gallery: 'An error occurred while opening the gallery.',
  err_analyze: 'An unexpected error occurred during analysis.',

  // ── Results ──
  results_title: 'Analysis Results',
  res_plant: 'Detected Plant',
  no_plant: 'Plant species could not be detected',
  res_health: 'Health Status',
  healthy: 'Healthy',
  diseases_found: '{} Disease(s) Detected',
  risk_label: 'Estimated Yield Loss',
  risk_low: 'Low Loss',
  risk_mid: 'Moderate Loss',
  risk_high: 'High Loss',
  res_detections: 'Detection Details',
  disease_section: 'Disease Information and Treatment Recommendations',
  lbl_ilac: 'Prescribed Medicine',
  lbl_sonuc: 'Agronomic Expectation',
  lbl_ekonomi: 'Financial Impact',
  no_info: 'No information available',
  btn_new_analysis: 'New Analysis',

  // ── Navigation (app.py sidebar menu) ──
  nav_home: 'Home / Analysis',
  nav_history: 'My Past Analyses',

  // ── Home showcase section ──
  nav_powered: 'AI POWERED',
  main_title: 'Plant Disease Diagnosis System',
  main_desc:
    'Upload a leaf photo and let the YOLOv8 model detect the disease within seconds; get your report with treatment advice and an estimated yield loss.',
  kpi_acc: 'Model Accuracy',
  kpi_acc_d: 'YOLOv8 Medium',
  kpi_time: 'Analysis Time',
  kpi_time_d: 'Real-time',
  kpi_dis: 'Disease Classes',
  kpi_dis_d: 'PlantDoc dataset',
  kpi_plants: 'Supported Plants',
  kpi_plants_d: 'Crop types',
  conf_label: 'Confidence Threshold',
  conf_hint:
    'A higher threshold shows only confident detections; a lower one lists more detections but increases false positives.',
  how_title: 'Diagnosis in three steps',
  step1_t: 'Upload Photo',
  step1_d: 'Photograph the suspect leaf clearly, in natural light.',
  step2_t: 'Let AI Analyze',
  step2_d: 'The YOLOv8 model recognizes the plant and disease in seconds.',
  step3_t: 'Review the Report',
  step3_d: 'Diagnosis, treatment advice and yield loss estimate, instantly.',

  // ── History page ──
  hist_tag: 'ANALYSIS HISTORY',
  hist_title: 'My Past Analyses',
  hist_desc:
    'Summary, distribution and detailed record list of all your analyses stored in the database.',
  hist_loading: 'Loading records...',
  info_empty:
    "You don't have any saved analyses yet. Run your first analysis from the home page and results will appear here.",
  err_db_read: 'Records could not be read.',
  err_session: 'Session info could not be retrieved. Please sign in again.',
  kpi_total: 'Total Number of Analyses',
  kpi_common: 'Most Common Disease',
  no_disease: 'No detected disease found.',
  chart1_t: 'Plant Type Distribution',
  chart1_d: 'Frequency distribution of analyzed crops',
  chart2_t: 'Health Status Ratio',
  chart2_d: 'Overall distribution of healthy and infected samples',
  status_healthy: 'Healthy',
  status_infected: 'Infected',
  table_t: 'Detailed Analysis Records',
  table_d: 'All records are sorted from newest to oldest',
  select_mode: 'Select',
  select_cancel: 'Cancel',
  delete_count: '{} record(s) selected',
  delete_btn: 'Delete Selected Records',
  delete_title: 'Delete Records',
  delete_confirm: '{} record(s) will be permanently deleted. Are you sure?',
  delete_ok: '{} record(s) deleted.',
  delete_err: 'Records could not be deleted.',
  refresh: 'Refresh',
};

export const LANGS = { tr, en } as const;

export type TranslationKey = keyof typeof tr;

/** ApiError.code → seçili dildeki kullanıcı mesajı */
export function apiErrorText(
  code: string | undefined,
  T: typeof tr,
  fallback?: string
): string {
  if (code === 'timeout') return T.err_timeout;
  if (code === 'network') return T.err_network;
  return fallback || T.err_generic;
}

// "{}" yer tutucusunu doldurur: format(T.success_reg, 'ali') → "Harika! ali ..."
export function format(template: string, ...values: (string | number)[]): string {
  let out = template;
  for (const value of values) {
    out = out.replace('{}', String(value));
  }
  return out;
}
