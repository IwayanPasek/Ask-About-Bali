<script setup lang="ts">
import { useI18n } from "../composables/useI18n"
import type { AskLocation } from "../types"

defineProps<{ locations: AskLocation[]; error?: string | null }>()

const { t } = useI18n()

/**
 * Classic Google Maps embed, which needs no API key on the client.
 * The key stays on the backend, where the Places API is called.
 */
function embedUrl(location: AskLocation): string {
  const { latitude, longitude } = location
  return `https://maps.google.com/maps?q=${latitude},${longitude}&z=15&hl=id&output=embed`
}
</script>

<template>
  <div v-if="locations.length || error" class="locations">
    <h3 class="locations__title">{{ t("locations.title") }}</h3>

    <p v-if="error" class="locations__error" role="alert">{{ error }}</p>

    <article v-for="location in locations" :key="location.place_id" class="location">
      <div class="location__map">
        <iframe
          class="location__iframe"
          :src="embedUrl(location)"
          :title="location.name"
          loading="lazy"
          referrerpolicy="no-referrer-when-downgrade"
          allowfullscreen
        ></iframe>
      </div>

      <div class="location__body">
        <p class="location__name">{{ location.name }}</p>
        <p v-if="location.address" class="location__address">{{ location.address }}</p>
        <p class="location__coords">
          {{ location.latitude.toFixed(5) }}, {{ location.longitude.toFixed(5) }}
        </p>
        <a
          class="location__link"
          :href="location.maps_url"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ t("locations.openInMaps") }}
        </a>
      </div>
    </article>
  </div>
</template>

<style scoped>
.locations {
  margin-top: 0.9rem;
}

.locations__title {
  margin: 0 0 0.55rem;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-muted);
}

.locations__error {
  margin: 0 0 0.55rem;
  padding: 0.55rem 0.7rem;
  border-radius: 0.5rem;
  background: var(--color-warning-soft, #fdf3e3);
  border: 1px solid var(--color-warning-border, #e8cf9e);
  color: var(--color-warning-text, #8a5a12);
  font-size: 0.83rem;
}

.location {
  display: grid;
  grid-template-columns: minmax(0, 14rem) minmax(0, 1fr);
  gap: 0.8rem;
  align-items: start;
  padding: 0.6rem;
  margin-bottom: 0.6rem;
  border: 1px solid var(--color-border);
  border-radius: 0.7rem;
  background: var(--color-bg);
}

.location__map {
  border-radius: 0.5rem;
  overflow: hidden;
  background: var(--color-surface-alt, #f2f0ea);
}

.location__iframe {
  display: block;
  width: 100%;
  height: 9rem;
  border: 0;
}

.location__body {
  min-width: 0;
}

.location__name {
  margin: 0;
  font-weight: 600;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.location__address {
  margin: 0.25rem 0 0;
  font-size: 0.82rem;
  line-height: 1.5;
  color: var(--color-muted);
  overflow-wrap: anywhere;
}

.location__coords {
  margin: 0.25rem 0 0;
  font-size: 0.72rem;
  color: var(--color-muted);
  font-variant-numeric: tabular-nums;
}

.location__link {
  display: inline-block;
  margin-top: 0.5rem;
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--color-accent);
  text-decoration: none;
}

.location__link:hover {
  text-decoration: underline;
}

@media (max-width: 620px) {
  .location {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
