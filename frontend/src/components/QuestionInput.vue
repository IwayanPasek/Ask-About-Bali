<script setup lang="ts">
import { computed, ref } from "vue"

import { CATEGORIES, type Category } from "../i18n/categories"
import { useI18n } from "../composables/useI18n"

const emit = defineEmits<{ (e: "submit", question: string, categoryId: string | null): void }>()

const { locale, t } = useI18n()

const draft = ref("")
const selected = ref<Category | null>(null)
const maxLength = 2000

const canSubmit = computed(() => draft.value.trim().length > 0)

function toggleCategory(category: Category): void {
  selected.value = selected.value?.id === category.id ? null : category
}

function submit(): void {
  const question = draft.value.trim()
  if (!question) return
  emit("submit", question, selected.value?.id ?? null)
  draft.value = ""
  selected.value = null
}

function sendExample(example: string): void {
  emit("submit", example, selected.value?.id ?? null)
}
</script>

<template>
  <section class="ask">
    <h2 class="ask__title">{{ t("ask.title") }}</h2>

    <div class="categories" role="group" aria-label="Kategori pertanyaan">
      <button
        v-for="category in CATEGORIES"
        :key="category.id"
        type="button"
        class="category"
        :class="{ 'category--active': selected?.id === category.id }"
        :aria-pressed="selected?.id === category.id"
        @click="toggleCategory(category)"
      >
        <span class="category__icon" aria-hidden="true">{{ category.icon }}</span>
        <span class="category__label">{{ t(category.label) }}</span>
      </button>
    </div>

    <div v-if="selected" class="examples">
      <p class="examples__heading">
        {{ t("ask.examples") }}
        <span class="examples__hint">{{ t("ask.examplesHint") }}</span>
      </p>
      <ul class="examples__list">
        <li v-for="example in selected.examples[locale]" :key="example">
          <button type="button" class="example" @click="sendExample(example)">
            {{ example }}
          </button>
        </li>
      </ul>
    </div>

    <form class="ask__form" @submit.prevent="submit">
      <textarea
        v-model="draft"
        class="ask__input"
        :maxlength="maxLength"
        rows="3"
        :placeholder="t('ask.placeholder')"
        :aria-label="t('ask.placeholder')"
        @keydown.enter.exact.prevent="submit"
      />
      <button type="submit" class="ask__submit" :disabled="!canSubmit">
        {{ t("ask.send") }}
      </button>
    </form>
  </section>
</template>

<style scoped>
.ask {
  max-width: 72rem;
  margin: 0 auto;
  padding: 0 1.5rem 3rem;
}

.ask__title {
  margin: 0 0 1rem;
  font-size: 1.25rem;
  letter-spacing: -0.01em;
}

.categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.category {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  font: inherit;
  font-size: 0.86rem;
  color: var(--color-text-soft);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.category:hover {
  border-color: var(--color-accent-border, var(--color-accent));
  color: var(--color-text);
}

.category--active {
  background: var(--color-accent);
  border-color: var(--color-accent);
  color: #fff;
}

.category--active .category__icon {
  color: #fff;
}

.category__icon {
  color: var(--color-accent);
  line-height: 1;
}

.examples {
  margin-top: 1.1rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--color-border);
  border-left: 3px solid var(--color-accent);
  border-radius: 0.75rem;
  background: var(--color-surface);
}

.examples__heading {
  margin: 0 0 0.6rem;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--color-muted);
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: baseline;
}

.examples__hint {
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
  font-size: 0.78rem;
}

.examples__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.example {
  width: 100%;
  text-align: left;
  font: inherit;
  font-size: 0.9rem;
  line-height: 1.5;
  padding: 0.55rem 0.7rem;
  border: 1px solid var(--color-border);
  border-radius: 0.55rem;
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease;
}

.example:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-soft);
}

.ask__form {
  margin-top: 1.25rem;
  display: flex;
  align-items: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.ask__input {
  flex: 1 1 22rem;
  min-width: 0;
  resize: vertical;
  min-height: 3.4rem;
  max-height: 12rem;
  padding: 0.75rem 0.9rem;
  border: 1px solid var(--color-border);
  border-radius: 0.75rem;
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  line-height: 1.55;
}

.ask__input:focus {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}

.ask__submit {
  flex: none;
  border: none;
  border-radius: 0.75rem;
  padding: 0.8rem 1.5rem;
  background: var(--color-accent);
  color: #fff;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.ask__submit:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
</style>
