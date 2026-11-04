<script setup lang="ts">
import { useI18n } from "../composables/useI18n"
import type { AskSource } from "../types"

defineProps<{ sources: AskSource[]; error?: string | null }>()

const { t } = useI18n()
</script>

<template>
  <div v-if="sources.length || error" class="sources">
    <h3 class="sources__title">{{ t("sources.title") }}</h3>

    <p v-if="error" class="sources__error" role="alert">{{ error }}</p>

    <ol class="sources__list">
      <li v-for="(source, index) in sources" :key="`${source.link}-${index}`" class="source">
        <a class="source__link" :href="source.link" target="_blank" rel="noopener noreferrer">
          {{ source.title || source.source_name }}
        </a>
        <p v-if="source.snippet" class="source__snippet">{{ source.snippet }}</p>
        <p class="source__name">{{ source.source_name }}</p>
      </li>
    </ol>
  </div>
</template>

<style scoped>
.sources {
  margin-top: 0.9rem;
}

.sources__title {
  margin: 0 0 0.55rem;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.sources__error {
  margin: 0 0 0.55rem;
  padding: 0.55rem 0.7rem;
  border-radius: 0.5rem;
  background: var(--color-warning-soft, #fdf3e3);
  border: 1px solid var(--color-warning-border, #e8cf9e);
  color: var(--color-warning-text, #8a5a12);
  font-size: 0.83rem;
}

.sources__list {
  margin: 0;
  padding-left: 1.15rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.source__link {
  font-size: 0.87rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
  overflow-wrap: anywhere;
}

.source__link:hover {
  text-decoration: underline;
}

.source__snippet {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
  line-height: 1.5;
  color: var(--color-answer-soft, var(--color-muted));
  overflow-wrap: anywhere;
}

.source__name {
  margin: 0.1rem 0 0;
  font-size: 0.72rem;
  color: var(--color-muted);
  overflow-wrap: anywhere;
}
</style>
