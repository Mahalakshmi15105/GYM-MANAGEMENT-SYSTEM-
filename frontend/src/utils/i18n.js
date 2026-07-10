import { useState, useEffect, useMemo } from 'react';

export const DEFAULT_LANGUAGE = 'en';
export const LANGUAGE_STORAGE_KEY = 'flexigym_language';
const LANGUAGE_CHANGE_EVENT = 'flexigym-language-change';

// Get gym-specific storage key
export function getGymLanguageKey(gymId) {
  return gymId ? `${LANGUAGE_STORAGE_KEY}_${gymId}` : LANGUAGE_STORAGE_KEY;
}

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語' },
  { code: 'fr', name: 'French', nativeName: 'Français' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية' },
  { code: 'zh', name: 'Chinese', nativeName: '中文' },
  { code: 'ko', name: 'Korean', nativeName: '한국어' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский' }
];

const LANGUAGE_MAP = Object.fromEntries(
  SUPPORTED_LANGUAGES.map(lang => [lang.code, lang])
);

// Translation storage
let translations = {};

export function getLanguageOptions() {
  return SUPPORTED_LANGUAGES;
}

export function getLanguage(languageCode = DEFAULT_LANGUAGE) {
  return LANGUAGE_MAP[languageCode] || LANGUAGE_MAP[DEFAULT_LANGUAGE];
}

export function getStoredLanguageCode(gymId = null) {
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE;
  }

  const storageKey = getGymLanguageKey(gymId);
  const storedLanguage = window.localStorage.getItem(storageKey);
  return LANGUAGE_MAP[storedLanguage]?.code || DEFAULT_LANGUAGE;
}

export function setStoredLanguageCode(languageCode, gymId = null) {
  const normalizedLanguage = LANGUAGE_MAP[languageCode]?.code || DEFAULT_LANGUAGE;

  if (typeof window !== 'undefined') {
    const storageKey = getGymLanguageKey(gymId);
    window.localStorage.setItem(storageKey, normalizedLanguage);
    window.dispatchEvent(
      new CustomEvent(LANGUAGE_CHANGE_EVENT, {
        detail: { languageCode: normalizedLanguage, gymId }
      })
    );
  }

  return normalizedLanguage;
}

export function loadTranslations(languageCode) {
  if (translations[languageCode]) {
    return translations[languageCode];
  }

  try {
    // Dynamic import for translations
    const translationModule = require(`../translations/${languageCode}.js`);
    translations[languageCode] = translationModule.default || translationModule;
    return translations[languageCode];
  } catch (error) {
    console.warn(`Failed to load translations for ${languageCode}:`, error);
    // Fallback to English
    if (languageCode !== DEFAULT_LANGUAGE) {
      return loadTranslations(DEFAULT_LANGUAGE);
    }
    return {};
  }
}

export function translate(key, languageCode = getStoredLanguageCode(), fallback = key) {
  const translation = loadTranslations(languageCode);
  
  // Support nested keys like "dashboard.title"
  const keys = key.split('.');
  let value = translation;
  
  for (const k of keys) {
    if (value && typeof value === 'object' && k in value) {
      value = value[k];
    } else {
      value = undefined;
      break;
    }
  }
  
  if (typeof value === 'string') {
    return value;
  }
  
  // Fallback to English if not found and not already English
  if (languageCode !== DEFAULT_LANGUAGE) {
    return translate(key, DEFAULT_LANGUAGE, fallback);
  }
  
  return fallback;
}

export function useTranslation(gymId = null) {
  const [languageCode, setLanguageCode] = useState(getStoredLanguageCode(gymId));

  useEffect(() => {
    const handleLanguageChange = (event) => {
      // Only update if the event is for this gym or no gym specified
      if (!gymId || event.detail?.gymId === gymId) {
        setLanguageCode(event.detail?.languageCode || getStoredLanguageCode(gymId));
      }
    };

    const handleStorageChange = (event) => {
      const storageKey = getGymLanguageKey(gymId);
      if (event.key === storageKey) {
        setLanguageCode(event.newValue || DEFAULT_LANGUAGE);
      }
    };

    window.addEventListener(LANGUAGE_CHANGE_EVENT, handleLanguageChange);
    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener(LANGUAGE_CHANGE_EVENT, handleLanguageChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [gymId]);

  const language = useMemo(() => getLanguage(languageCode), [languageCode]);
  
  const t = useMemo(() => {
    return (key, fallback = key) => translate(key, languageCode, fallback);
  }, [languageCode]);

  return {
    languageCode: language.code,
    languageName: language.name,
    languageOptions: SUPPORTED_LANGUAGES,
    t,
    setLanguage: (code) => setStoredLanguageCode(code, gymId)
  };
}