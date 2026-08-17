<script setup lang="ts">
import { onMounted } from 'vue'

import Footer from '@/components/common/Footer.vue'
import Header from '@/components/common/Header.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  void authStore.fetchMe()
})
</script>

<template>
  <div class="default-layout">
    <Header />

    <main class="layout-main">
      <slot />
    </main>

    <Footer />
  </div>
</template>

<style scoped>
.default-layout {
  min-width: 320px;
  min-height: 100vh;
  overflow: clip;
  background:
    radial-gradient(circle at 8% 8%, rgba(255, 224, 105, 0.18), transparent 21rem),
    #fffdf7;
}

.layout-main { min-height: calc(100vh - 188px); }
</style>
