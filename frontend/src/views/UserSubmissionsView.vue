<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getPublicUser, getUserSubmissions } from '@/api/modules/users'
import type { PublicSubmission, PublicUser } from '@/types/user'

const route = useRoute()

const user = ref<PublicUser | null>(null)
const submissions = ref<PublicSubmission[]>([])
const loading = ref(true)
const error = ref('')

const memes = computed(() => (
  submissions.value.filter((submission) => submission.submission_type === 'meme')
))

const music = computed(() => (
  submissions.value.filter((submission) => submission.submission_type === 'music')
))

function formatDate(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(value))
}

async function loadSubmissions(uid: string) {
  loading.value = true
  error.value = ''
  user.value = null
  submissions.value = []

  try {
    const [userResponse, submissionsResponse] = await Promise.all([
      getPublicUser(uid),
      getUserSubmissions(uid),
    ])

    user.value = userResponse.data
    submissions.value = submissionsResponse.data
  } catch (requestError) {
    console.error('加载公开投稿失败', requestError)
    error.value = '没有找到这位基米居民，或公开投稿暂时无法加载。'
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.uid,
  (uid) => {
    if (typeof uid === 'string' && uid) {
      loadSubmissions(uid)
      return
    }

    error.value = 'UID 无效。'
    loading.value = false
  },
  { immediate: true },
)
</script>

<template>
  <main class="submission-page">
    <p v-if="loading" class="page-status">正在整理 TA 的公开投稿...</p>

    <section v-else-if="error" class="page-status error-card">
      <p>{{ error }}</p>
      <RouterLink to="/">返回首页 →</RouterLink>
    </section>

    <template v-else-if="user">
      <section class="page-hero">
        <div>
          <p class="section-kicker">PUBLIC CONTRIBUTIONS</p>
          <h1>{{ user.username }} 的投稿</h1>
          <p>UID {{ user.uid }} · 仅展示仍在基米小站公开收录的作品。</p>
        </div>

        <RouterLink :to="`/users/${user.uid}`" class="back-link">返回 TA 的主页 →</RouterLink>
      </section>

      <section class="submission-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">MEME ARCHIVE</p>
            <h2>🖼 表情包</h2>
          </div>
          <span>{{ memes.length }} 个</span>
        </div>

        <p v-if="memes.length === 0" class="empty-copy">TA 暂未公开发布表情包。</p>

        <div v-else class="meme-grid">
          <a
            v-for="item in memes"
            :key="item.id"
            class="meme-card"
            :href="item.file_url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img :src="item.file_url" :alt="item.title" />
            <div>
              <strong>{{ item.title }}</strong>
              <small>{{ formatDate(item.created_at) }}</small>
            </div>
          </a>
        </div>
      </section>

      <section class="submission-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">HAKIMI MUSIC</p>
            <h2>🎵 音乐</h2>
          </div>
          <span>{{ music.length }} 首</span>
        </div>

        <p v-if="music.length === 0" class="empty-copy">TA 暂未公开发布音乐。</p>

        <div v-else class="music-grid">
          <article v-for="item in music" :key="item.id" class="music-card">
            <img v-if="item.cover_url" :src="item.cover_url" :alt="item.title" />
            <span v-else class="music-placeholder">♪</span>
            <div class="music-copy">
              <strong>{{ item.title }}</strong>
              <p>{{ item.description || '哈基米音乐投稿' }}</p>
              <small>{{ formatDate(item.created_at) }}</small>
              <audio :src="item.file_url" controls preload="metadata" />
            </div>
          </article>
        </div>
      </section>
    </template>
  </main>
</template>

<style scoped>
.submission-page {
  width: min(1160px, calc(100% - 48px));
  margin: 0 auto;
  padding: 72px 0 120px;
}

.page-hero,
.submission-section,
.page-status {
  border: 1px solid rgba(246, 197, 52, 0.3);
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 18px 44px rgba(79, 61, 32, 0.1);
}

.page-hero {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 24px;
  padding: 46px;
  background:
    radial-gradient(circle at 90% 16%, rgba(255, 221, 230, 0.7), transparent 30%),
    radial-gradient(circle at 10% 92%, rgba(255, 237, 159, 0.56), transparent 28%),
    #fffaf0;
}

.section-kicker {
  margin: 0 0 10px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
}

h1,
h2 {
  margin: 0;
  color: #25231f;
}

h1 {
  font-size: clamp(38px, 5vw, 60px);
}

h2 {
  font-size: 27px;
}

.page-hero p:not(.section-kicker) {
  margin: 14px 0 0;
  color: #7b6a4a;
  line-height: 1.7;
}

.back-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0 20px;
  border: 1px solid #f6c534;
  border-radius: 999px;
  background: #f6c534;
  color: #352b1b;
  font-weight: 900;
  text-decoration: none;
}

.submission-section {
  margin-top: 28px;
  padding: 32px;
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
}

.section-heading span {
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff0be;
  color: #75581b;
  font-size: 13px;
  font-weight: 900;
}

.meme-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 18px;
  margin-top: 24px;
}

.meme-card {
  overflow: hidden;
  border: 1px solid #eadfca;
  border-radius: 22px;
  background: #fffdf7;
  color: #594828;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.meme-card:hover {
  box-shadow: 0 12px 28px rgba(79, 61, 32, 0.12);
  transform: translateY(-3px);
}

.meme-card img {
  display: block;
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.meme-card div {
  display: grid;
  gap: 5px;
  padding: 13px;
}

.meme-card strong,
.music-copy strong {
  color: #3f3320;
  font-size: 15px;
}

small,
.music-copy p,
.empty-copy {
  color: #806e4d;
}

.music-grid {
  display: grid;
  gap: 14px;
  margin-top: 24px;
}

.music-card {
  display: grid;
  grid-template-columns: 100px minmax(0, 1fr);
  gap: 18px;
  padding: 14px;
  border: 1px solid #eadfca;
  border-radius: 24px;
  background: #fffdf7;
}

.music-card > img,
.music-placeholder {
  width: 100px;
  height: 100px;
  border-radius: 18px;
  object-fit: cover;
}

.music-placeholder {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #ffe898, #ffdce6);
  color: #4f3b21;
  font-size: 38px;
  font-weight: 900;
}

.music-copy {
  min-width: 0;
}

.music-copy p {
  margin: 6px 0;
  font-size: 13px;
  line-height: 1.55;
}

.music-copy audio {
  display: block;
  width: 100%;
  margin-top: 10px;
}

.empty-copy {
  margin: 18px 0 0;
  line-height: 1.7;
}

.page-status {
  padding: 48px;
  color: #7b6a4a;
  font-weight: 800;
  text-align: center;
}

.error-card a {
  color: #9a7512;
  font-weight: 900;
  text-decoration: none;
}

@media (max-width: 680px) {
  .submission-page {
    width: min(100% - 32px, 1160px);
    padding-top: 44px;
  }

  .page-hero {
    align-items: start;
    flex-direction: column;
    padding: 32px;
  }

  .submission-section {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .music-card {
    grid-template-columns: 1fr;
  }
}
</style>
