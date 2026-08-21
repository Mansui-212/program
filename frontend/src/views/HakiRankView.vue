<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getHakiRanking } from '@/api/modules/users'

import type { HakiRankingUser } from '@/types/user'

const users = ref<HakiRankingUser[]>([])
const loading = ref(true)
const error = ref('')

function medal(index: number) {
  return ['🥇', '🥈', '🥉'][index] || String(index + 1)
}

async function loadRanking() {
  loading.value = true
  error.value = ''

  try {
    const response = await getHakiRanking()
    users.value = response.data
  } catch (reason) {
    console.error('加载哈气排行榜失败', reason)
    error.value = '排行榜暂时无法加载。'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadRanking()
})
</script>

<template>
  <main class="rank-page">
    <section class="rank-hero">
      <p class="section-kicker">HAKI RANKING</p>
      <h1>哈气排行榜</h1>
      <p>每一次分享、收藏与创作，都会让基米居民的哈气更旺一点。</p>
    </section>

    <section class="rank-card">
      <p v-if="loading" class="page-status">正在统计哈气值...</p>
      <p v-else-if="error" class="page-status error-text">{{ error }}</p>
      <p v-else-if="users.length === 0" class="page-status">还没有居民进入排行榜。</p>

      <ol v-else class="rank-list">
        <li v-for="(user, index) in users" :key="user.id" class="rank-item">
          <span class="rank-number">{{ medal(index) }}</span>
          <img :src="user.avatar_url || '/static/images/avatars/maodie.jpg'" :alt="user.username" />
          <RouterLink :to="`/users/${user.uid}`" class="rank-user">
            <strong>{{ user.username }}</strong>
            <span>UID {{ user.uid }}</span>
          </RouterLink>
          <strong class="haki-value">{{ user.haki_value }} 哈气</strong>
        </li>
      </ol>
    </section>
  </main>
</template>

<style scoped>
.rank-page { width: min(960px, calc(100% - 48px)); margin: 0 auto; padding: 64px 0 120px; }
.rank-hero { padding: clamp(36px, 6vw, 68px); border-radius: 40px; background: linear-gradient(135deg, #fff2b2, #ffe3ec 58%, #e9e0ff); }
.section-kicker { margin: 0 0 12px; color: #ae8110; font-size: 13px; font-weight: 900; letter-spacing: .13em; }
.rank-hero h1 { margin: 0; color: #292722; font-size: clamp(42px, 7vw, 68px); letter-spacing: -.06em; }
.rank-hero p:not(.section-kicker) { margin: 20px 0 0; color: #786747; line-height: 1.7; }
.rank-card { margin-top: 28px; padding: 20px; border-radius: 32px; background: #fffaf0; box-shadow: 0 18px 40px rgba(79, 61, 32, .09); }
.page-status { margin: 0; padding: 28px; color: #7b6a4a; text-align: center; font-weight: 800; }
.error-text { color: #bd4747; }
.rank-list { display: grid; gap: 12px; padding: 0; margin: 0; list-style: none; }
.rank-item { display: grid; grid-template-columns: 48px 56px minmax(0, 1fr) auto; gap: 16px; align-items: center; padding: 16px; border-radius: 22px; background: #fffdf7; }
.rank-number { display: grid; place-items: center; min-width: 40px; color: #806219; font-weight: 900; font-size: 18px; }
.rank-item img { width: 56px; height: 56px; border: 3px solid #f6c534; border-radius: 50%; object-fit: cover; background: #fffaf0; }
.rank-user { display: grid; gap: 4px; min-width: 0; color: #292722; text-decoration: none; }
.rank-user:hover strong { color: #9a7512; text-decoration: underline; }
.rank-user span { color: #99845c; font-size: 13px; font-weight: 800; }
.haki-value { color: #856313; white-space: nowrap; }
@media (max-width: 560px) { .rank-page { width: min(100% - 32px, 960px); padding-top: 32px; } .rank-item { grid-template-columns: 40px 48px minmax(0, 1fr); gap: 10px; } .rank-item img { width: 48px; height: 48px; } .haki-value { grid-column: 2 / -1; } }
</style>
