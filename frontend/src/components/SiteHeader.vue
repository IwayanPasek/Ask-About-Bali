<script setup lang="ts">
import { useI18n } from "../composables/useI18n"
import { LOCALES, type Locale } from "../i18n/messages"

const { locale, t, setLocale } = useI18n()

const labels: Record<Locale, string> = { id: "ID", en: "EN" }
</script>

<template>
  <header class="header">
    <div class="header__inner">
      <a class="brand" href="#top">
        <span class="brand__mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M16 3c4.5 3.6 7 7.2 7 10.8 0 3.1-1.6 5.7-4 7.6.6-1.7.9-3.4.9-5.1 0-3.1-1.3-6-3.9-8.7 1.2 3 1.8 5.9 1.8 8.7 0 1.7-.3 3.4-.9 5.1 2.4-1.9 4-4.5 4-7.6 0-1.4-.4-2.8-1.1-4.2"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
            <path
              d="M16 29c-3.2 0-5.9-1.4-8-4.2 2.6.9 5.2 1.3 8 1.3s5.4-.4 8-1.3c-2.1 2.8-4.8 4.2-8 4.2Z"
              stroke="currentColor"
              stroke-width="1.6"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <span class="brand__text">
          <span class="brand__name">{{ t("brand.name") }}</span>
          <span class="brand__tagline">{{ t("brand.tagline") }}</span>
        </span>
      </a>

      <div class="header__actions">
        <span class="lang-label" id="lang-label">{{ t("lang.label") }}</span>
        <div class="lang-toggle" role="group" aria-labelledby="lang-label">
          <button
            v-for="code in LOCALES"
            :key="code"
            type="button"
            class="lang-toggle__button"
            :class="{ 'lang-toggle__button--active': locale === code }"
            :aria-pressed="locale === code"
            @click="setLocale(code)"
          >
            {{ labels[code] }}
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: color-mix(in srgb, var(--color-bg) 88%, transparent);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--color-border);
}

.header__inner {
  max-width: 72rem;
  margin: 0 auto;
  padding: 0.85rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  text-decoration: none;
  color: inherit;
  min-width: 0;
}

.brand__mark {
  display: grid;
  place-items: center;
  width: 2.4rem;
  height: 2.4rem;
  flex: none;
  border-radius: 0.7rem;
  background: var(--color-accent-soft);
  color: var(--color-accent);
}

.brand__mark svg {
  width: 1.5rem;
  height: 1.5rem;
}

.brand__text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.brand__name {
  font-weight: 700;
  font-size: 1.05rem;
  letter-spacing: -0.01em;
  line-height: 1.2;
}

.brand__tagline {
  font-size: 0.78rem;
  color: var(--color-muted);
  line-height: 1.3;
}

.header__actions {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.lang-label {
  font-size: 0.78rem;
  color: var(--color-muted);
}

.lang-toggle {
  display: inline-flex;
  padding: 3px;
  gap: 2px;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
}

.lang-toggle__button {
  border: none;
  background: transparent;
  border-radius: 999px;
  padding: 0.3rem 0.75rem;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-muted);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease;
  white-space: nowrap;
}

.lang-toggle__button:hover {
  color: var(--color-text);
}

.lang-toggle__button--active {
  background: var(--color-accent);
  color: #fff;
}

@media (max-width: 480px) {
  .header__inner {
    padding: 0.75rem 1rem;
  }

  .brand__tagline {
    display: none;
  }
}
</style>
