import { computed, ref } from "vue"

import { LOCALES, messages, type Locale, type MessageKey } from "../i18n/messages"

const STORAGE_KEY = "ask-about-bali.locale"

function detectInitialLocale(): Locale {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === "id" || stored === "en") return stored
  return navigator.language?.toLowerCase().startsWith("id") ? "id" : "en"
}

const locale = ref<Locale>(detectInitialLocale())

export function useI18n() {
  function t(key: MessageKey, vars?: Record<string, string | number>): string {
    const raw: string = messages[locale.value][key] ?? key
    if (!vars) return raw
    return Object.entries(vars).reduce(
      (acc, [name, value]) => acc.replaceAll(`{${name}}`, String(value)),
      raw,
    )
  }

  function setLocale(next: Locale): void {
    locale.value = next
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.setAttribute("lang", next)
  }

  function toggleLocale(): void {
    setLocale(locale.value === "id" ? "en" : "id")
  }

  return {
    locale,
    locales: LOCALES,
    t,
    setLocale,
    toggleLocale,
    isIndonesian: computed(() => locale.value === "id"),
  }
}
