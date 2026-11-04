<script setup lang="ts">
import { useI18n } from "../composables/useI18n"

const { t } = useI18n()
const year = new Date().getFullYear()
</script>

<template>
  <footer class="footer">
    <div class="footer__inner">
      <p class="footer__brand">{{ t("footer.product") }}</p>
      <p class="footer__disclaimer">{{ t("footer.disclaimer") }}</p>
      <p class="footer__copyright">{{ t("footer.copyright", { year }) }}</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: auto;
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.footer__inner {
  max-width: 72rem;
  margin: 0 auto;
  padding: 2rem 1.5rem 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.footer__brand {
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.footer__disclaimer {
  margin: 0;
  max-width: 70ch;
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--color-muted);
}

.footer__copyright {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-muted);
}
</style>
