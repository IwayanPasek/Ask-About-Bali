<script setup lang="ts">
import ImageCard from "./ImageCard.vue"
import LocationCard from "./LocationCard.vue"
import SourceCard from "./SourceCard.vue"
import { useI18n } from "../composables/useI18n"
import type { AnswerEntry } from "../types"

defineProps<{ entries: AnswerEntry[]; pending: boolean }>()
const emit = defineEmits<{ (e: "clear"): void }>()

const { t } = useI18n()
</script>

<template>
  <section class="conversation">
    <div class="conversation__head">
      <h2 class="conversation__title">{{ t("ask.yourQuestion") }}</h2>
      <button
        v-if="entries.length"
        type="button"
        class="conversation__clear"
        @click="emit('clear')"
      >
        {{ t("ask.clear") }}
      </button>
    </div>

    <p v-if="!entries.length && !pending" class="conversation__empty">{{ t("ask.empty") }}</p>

    <ul class="conversation__list">
      <li v-for="entry in entries" :key="entry.id" class="entry">
        <div class="entry__meta">
          <span class="entry__badge">
            {{ entry.categoryLabel ?? t("ask.yourQuestion") }}
          </span>
        </div>

        <p class="entry__question">{{ entry.question }}</p>

        <div v-if="entry.error" class="entry__error" role="alert">
          {{ entry.error }}
        </div>

        <template v-else>
          <p
            class="entry__answer"
            :class="{
              'entry__answer--out-of-scope': entry.status === 'out_of_scope',
              'entry__answer--not-found': entry.status === 'not_found',
            }"
          >
            {{ entry.answer }}
          </p>

          <ImageCard v-if="entry.images.length" :images="entry.images" />

          <LocationCard
            v-if="entry.locations.length || entry.locationError"
            :locations="entry.locations"
            :error="entry.locationError"
          />

          <SourceCard
            v-if="entry.sources.length || entry.webSearchError"
            :sources="entry.sources"
            :error="entry.webSearchError"
          />

          <div v-if="entry.searchTip" class="entry__tip">
            <span class="entry__tip-label">{{ t("searchTip.title") }}</span>
            <p class="entry__tip-text">{{ entry.searchTip }}</p>
          </div>
        </template>
      </li>

      <li v-if="pending" class="entry entry--pending">
        <p class="entry__answer entry__answer--muted">{{ t("ask.loading") }}</p>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.conversation {
  max-width: 72rem;
  margin: 0 auto;
  padding: 0 1.5rem 4rem;
}

.conversation__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.conversation__title {
  margin: 0 0 0.9rem;
  font-size: 1.1rem;
}

.conversation__clear {
  border: 1px solid var(--color-border);
  background: transparent;
  border-radius: 999px;
  padding: 0.3rem 0.85rem;
  font: inherit;
  font-size: 0.78rem;
  color: var(--color-muted);
  cursor: pointer;
}

.conversation__empty {
  margin: 0;
  padding: 1.5rem;
  border: 1px dashed var(--color-border);
  border-radius: 0.75rem;
  color: var(--color-muted);
  font-size: 0.9rem;
  text-align: center;
}

.conversation__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.entry {
  padding: 0.85rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  background: var(--color-surface);
}

.entry--pending {
  border-style: dashed;
}

.entry__meta {
  margin-bottom: 0.4rem;
}

.entry__badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-accent);
  background: var(--color-accent-soft);
  padding: 0.15rem 0.55rem;
  border-radius: 999px;
}

.entry__question {
  margin: 0;
  font-weight: 600;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.entry__answer {
  margin: 0.55rem 0 0;
  line-height: 1.65;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  color: var(--color-text-soft);
}

.entry__answer--muted {
  color: var(--color-muted);
  font-style: italic;
}

.entry__answer--out-of-scope {
  padding-left: 0.7rem;
  border-left: 3px solid var(--color-warning-border, #e8cf9e);
}

.entry__answer--not-found {
  padding-left: 0.7rem;
  border-left: 3px solid var(--color-border);
}

.entry__error {
  margin: 0.55rem 0 0;
  padding: 0.55rem 0.7rem;
  border-radius: 0.5rem;
  background: var(--color-warning-soft, #fdf3e3);
  border: 1px solid var(--color-warning-border, #e8cf9e);
  color: var(--color-warning-text, #8a5a12);
  font-size: 0.85rem;
}

.entry__tip {
  margin-top: 0.9rem;
  padding: 0.6rem 0.7rem;
  border-radius: 0.55rem;
  background: var(--color-accent-soft);
  border: 1px solid var(--color-border);
}

.entry__tip-label {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.entry__tip-text {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  line-height: 1.55;
  color: var(--color-answer-soft, var(--color-muted));
  overflow-wrap: anywhere;
}
</style>
