<script setup lang="ts">
import { useI18n } from "../composables/useI18n"
import type { AskImage } from "../types"

defineProps<{ images: AskImage[] }>()

const { t } = useI18n()
</script>

<template>
  <div v-if="images.length" class="image-grid">
    <figure v-for="(image, index) in images" :key="`${image.image_url}-${index}`" class="image-card">
      <a :href="image.source_url || image.image_url" target="_blank" rel="noopener noreferrer">
        <img
          class="image-card__img"
          :src="image.thumbnail_url || image.image_url"
          :alt="image.title || t('images.alt')"
          loading="lazy"
          referrerpolicy="no-referrer"
        />
      </a>
      <figcaption class="image-card__caption">
        <a
          class="image-card__source"
          :href="image.source_url || image.image_url"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ image.source_name || t("images.unknownSource") }}
        </a>
      </figcaption>
    </figure>
  </div>
</template>

<style scoped>
.image-grid {
  margin-top: 0.85rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 10.5rem), 1fr));
  gap: 0.6rem;
}

.image-card {
  margin: 0;
  border: 1px solid var(--color-border);
  border-radius: 0.6rem;
  overflow: hidden;
  background: var(--color-bg);
}

.image-card__img {
  display: block;
  width: 100%;
  height: 7rem;
  object-fit: cover;
  background: var(--color-surface-alt, #f2f0ea);
}

.image-card__caption {
  padding: 0.4rem 0.5rem;
  font-size: 0.72rem;
  line-height: 1.4;
  color: var(--color-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.image-card__source {
  color: inherit;
  text-decoration: none;
}

.image-card__source:hover {
  color: var(--color-accent);
  text-decoration: underline;
}
</style>
