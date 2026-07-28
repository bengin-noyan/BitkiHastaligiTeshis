// ─────────────────────────────────────────────────────────────────────
// Dil durumu — app.py'deki st.session_state.lang'ın mobil karşılığı.
// Giriş ekranında seçilen dil, uygulama boyunca (ana ekran dâhil) geçerli
// olsun diye React Context ile paylaşılır.
// ─────────────────────────────────────────────────────────────────────

import React, { createContext, useContext, useMemo, useState } from 'react';
import { LANGS, type Lang } from '../constants/i18n';

type LanguageContextValue = {
  lang: Lang;
  setLang: (lang: Lang) => void;
  /** Seçili dilin çeviri sözlüğü */
  T: (typeof LANGS)['tr'];
};

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Lang>('tr');

  const value = useMemo<LanguageContextValue>(
    () => ({ lang, setLang, T: LANGS[lang] }),
    [lang]
  );

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error('useLanguage, LanguageProvider içinde kullanılmalıdır.');
  }
  return ctx;
}
