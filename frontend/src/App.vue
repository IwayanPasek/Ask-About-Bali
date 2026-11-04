<script setup lang="ts">
import ConversationList from "./components/ConversationList.vue"
import HeroSection from "./components/HeroSection.vue"
import QuestionInput from "./components/QuestionInput.vue"
import SiteFooter from "./components/SiteFooter.vue"
import SiteHeader from "./components/SiteHeader.vue"
import { useAsk } from "./composables/useAsk"

const { entries, pending, ask, clear } = useAsk()
</script>

<template>
  <div class="page">
    <SiteHeader />
    <main id="top" class="page__main">
      <HeroSection />
      <QuestionInput @submit="ask" />
      <ConversationList :entries="entries" :pending="pending" @clear="clear" />
    </main>
    <SiteFooter />
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.page__main {
  flex: 1;
}
</style>
