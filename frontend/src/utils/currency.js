import { useEffect, useMemo, useState } from "react";

export const DEFAULT_CURRENCY = "INR";
export const CURRENCY_STORAGE_KEY = "flexigym_currency";
const CURRENCY_CHANGE_EVENT = "flexigym-currency-change";

// Get gym-specific storage key
export function getGymCurrencyKey(gymId) {
  return gymId ? `${CURRENCY_STORAGE_KEY}_${gymId}` : CURRENCY_STORAGE_KEY;
}

const CURRENCY_OPTIONS = [
  { code: "INR", label: "INR (₹)", symbol: "₹", locale: "en-IN" },
  { code: "USD", label: "USD ($)", symbol: "$", locale: "en-US" },
  { code: "EUR", label: "EUR (€)", symbol: "€", locale: "en-GB" },
  { code: "GBP", label: "GBP (£)", symbol: "£", locale: "en-GB" },
  { code: "KES", label: "KES (KSh)", symbol: "KSh", locale: "en-KE" },
  { code: "AED", label: "AED", symbol: "AED", locale: "en-AE" },
  { code: "SGD", label: "SGD", symbol: "S$", locale: "en-SG" },
  { code: "AUD", label: "AUD", symbol: "A$", locale: "en-AU" },
  { code: "CAD", label: "CAD", symbol: "C$", locale: "en-CA" },
  { code: "JPY", label: "JPY (¥)", symbol: "¥", locale: "ja-JP" },
  { code: "CNY", label: "CNY (¥)", symbol: "¥", locale: "zh-CN" },
  { code: "MYR", label: "MYR", symbol: "RM", locale: "ms-MY" },
  { code: "THB", label: "THB", symbol: "฿", locale: "th-TH" },
  { code: "SAR", label: "SAR", symbol: "SAR", locale: "ar-SA" },
  { code: "ZAR", label: "ZAR", symbol: "R", locale: "en-ZA" },
  { code: "NZD", label: "NZD", symbol: "NZ$", locale: "en-NZ" },
  { code: "CHF", label: "CHF", symbol: "CHF", locale: "de-CH" },
  { code: "HKD", label: "HKD", symbol: "HK$", locale: "zh-HK" },
  { code: "PKR", label: "PKR", symbol: "Rs", locale: "en-PK" },
  { code: "BDT", label: "BDT", symbol: "৳", locale: "bn-BD" },
  { code: "LKR", label: "LKR", symbol: "Rs", locale: "si-LK" },
  { code: "NPR", label: "NPR", symbol: "Rs", locale: "ne-NP" },
];

const CURRENCY_MAP = Object.fromEntries(
  CURRENCY_OPTIONS.map((option) => [option.code, option]),
);

export function getCurrencyOptions() {
  return CURRENCY_OPTIONS;
}

export function getCurrencyOption(currencyCode = DEFAULT_CURRENCY) {
  return CURRENCY_MAP[currencyCode] || CURRENCY_MAP[DEFAULT_CURRENCY];
}

export function getStoredCurrencyCode(gymId = null) {
  if (typeof window === "undefined") {
    return DEFAULT_CURRENCY;
  }

  const storageKey = getGymCurrencyKey(gymId);
  const storedCurrency = window.localStorage.getItem(storageKey);
  return CURRENCY_MAP[storedCurrency]?.code || DEFAULT_CURRENCY;
}

export function setStoredCurrencyCode(currencyCode, gymId = null) {
  const normalizedCurrency =
    CURRENCY_MAP[currencyCode]?.code || DEFAULT_CURRENCY;

  if (typeof window !== "undefined") {
    const storageKey = getGymCurrencyKey(gymId);
    window.localStorage.setItem(storageKey, normalizedCurrency);
    window.dispatchEvent(
      new CustomEvent(CURRENCY_CHANGE_EVENT, {
        detail: { currencyCode: normalizedCurrency, gymId },
      }),
    );
  }

  return normalizedCurrency;
}

export function formatCurrency(amount, currencyCode = getStoredCurrencyCode()) {
  if (amount === null || amount === undefined || amount === "") {
    return "-";
  }

  const numericAmount = Number(amount);
  if (Number.isNaN(numericAmount)) {
    return "-";
  }

  const currencyOption = getCurrencyOption(currencyCode);
  return new Intl.NumberFormat(currencyOption.locale, {
    style: "currency",
    currency: currencyOption.code,
    currencyDisplay: "narrowSymbol",
  }).format(numericAmount);
}

export function useCurrency(gymId = null) {
  const [currencyCode, setCurrencyCode] = useState(getStoredCurrencyCode(gymId));

  useEffect(() => {
    const handleCurrencyChange = (event) => {
      // Only update if the event is for this gym or no gym specified
      if (!gymId || event.detail?.gymId === gymId) {
        setCurrencyCode(event.detail?.currencyCode || getStoredCurrencyCode(gymId));
      }
    };

    const handleStorageChange = (event) => {
      const storageKey = getGymCurrencyKey(gymId);
      if (event.key === storageKey) {
        setCurrencyCode(event.newValue || DEFAULT_CURRENCY);
      }
    };

    window.addEventListener(CURRENCY_CHANGE_EVENT, handleCurrencyChange);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener(CURRENCY_CHANGE_EVENT, handleCurrencyChange);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [gymId]);

  const currencyOption = useMemo(
    () => getCurrencyOption(currencyCode),
    [currencyCode],
  );

  return {
    currencyCode: currencyOption.code,
    currencyLabel: currencyOption.label,
    currencySymbol: currencyOption.symbol,
    currencyOptions: CURRENCY_OPTIONS,
    formatCurrency: (amount) => formatCurrency(amount, currencyOption.code),
    setCurrencyCode: (code) => setStoredCurrencyCode(code, gymId),
  };
}
