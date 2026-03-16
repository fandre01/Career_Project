import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import { translations, type LangCode, type TranslationKeys } from './translations';

interface LanguageContextType {
  lang: LangCode;
  setLang: (lang: LangCode) => void;
  t: TranslationKeys;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: 'en',
  setLang: () => {},
  t: translations.en,
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<LangCode>(() => {
    const saved = localStorage.getItem('careershield_lang') as LangCode | null;
    return saved && translations[saved] ? saved : 'en';
  });

  const setLang = useCallback((code: LangCode) => {
    setLangState(code);
    localStorage.setItem('careershield_lang', code);
    document.documentElement.dir = code === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = code;
  }, []);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t: translations[lang] }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
