<script setup lang="ts">
import { useI18n } from "../composables/useI18n"
import type { MessageKey } from "../i18n/messages"

const { t } = useI18n()

const topics: { icon: string; key: MessageKey }[] = [
  { icon: "◈", key: "hero.topic.culture" },
  { icon: "⛰", key: "hero.topic.places" },
  { icon: "⛩", key: "hero.topic.rules" },
  { icon: "⛵", key: "hero.topic.transport" },
  { icon: "⌂", key: "hero.topic.stay" },
  { icon: "✦", key: "hero.topic.facilities" },
]
</script>

<template>
  <section class="hero">
    <div class="hero__content">
      <p class="hero__eyebrow">{{ t("hero.topics") }}</p>
      <h1 class="hero__title">{{ t("hero.title") }}</h1>
      <p class="hero__subtitle">{{ t("hero.subtitle") }}</p>

      <ul class="hero__topics">
        <li v-for="topic in topics" :key="topic.key" class="topic">
          <span class="topic__icon" aria-hidden="true">{{ topic.icon }}</span>
          <span class="topic__label">{{ t(topic.key) }}</span>
        </li>
      </ul>

      <p class="hero__note">{{ t("hero.note") }}</p>
    </div>

    <div class="hero__art" aria-hidden="true">
      <svg viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
        <circle cx="120" cy="120" r="104" fill="none" stroke="currentColor" stroke-width="1" opacity="0.35" />
        <circle cx="120" cy="120" r="76" fill="none" stroke="currentColor" stroke-width="1" opacity="0.5" />
        <path
          d="M120 34c26 24 40 48 40 71 0 19-9 35-23 46 4-9 6-18 6-27 0-18-7-36-23-52 7 18 11 35 11 52 0 9-2 18-6 27 14-11 23-27 23-46 0-9-2-17-6-24"
          fill="none"
          stroke="currentColor"
          stroke-width="2.4"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M120 206c-19 0-35-8-47-25 15 5 31 8 47 8s32-3 47-8c-12 17-28 25-47 25Z"
          fill="none"
          stroke="currentColor"
          stroke-width="2.4"
          stroke-linejoin="round"
        />
      </svg>
    </div>
  </section>
</template>

<style scoped>
.hero {
  max-width: 72rem;
  margin: 0 auto;
  padding: 4rem 1.5rem 3.5rem;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.65fr);
  align-items: center;
  gap: 2.5rem;
}

.hero__content {
  min-width: 0;
}

.hero__eyebrow {
  margin: 0 0 0.9rem;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.hero__title {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.35rem);
  line-height: 1.12;
  letter-spacing: -0.02em;
  max-width: 18ch;
  text-wrap: balance;
}

.hero__subtitle {
  margin: 1.1rem 0 0;
  max-width: 52ch;
  font-size: clamp(0.98rem, 1.4vw, 1.08rem);
  line-height: 1.65;
  color: var(--color-muted);
}

.hero__topics {
  list-style: none;
  margin: 1.75rem 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
}

.topic {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  font-size: 0.86rem;
  color: var(--color-text-soft);
  white-space: nowrap;
}

.topic__icon {
  color: var(--color-accent);
  font-size: 0.9rem;
  line-height: 1;
}

.hero__note {
  margin: 1.6rem 0 0;
  font-size: 0.85rem;
  color: var(--color-muted);
}

.hero__art {
  display: grid;
  place-items: center;
  color: var(--color-accent);
  opacity: 0.9;
}

.hero__art svg {
  width: min(100%, 17rem);
  height: auto;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: minmax(0, 1fr);
    padding: 3rem 1.25rem 2.75rem;
    text-align: left;
  }

  .hero__art {
    order: -1;
  }

  .hero__art svg {
    width: min(70%, 11rem);
  }
}
</style>
