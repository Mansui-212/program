<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getPublicUser, getPublicUserSubmissions } from '@/api/modules/users'
import type { PublicSubmission, PublicUser } from '@/types/user'

const route = useRoute()
const defaultAvatar = '/static/images/avatars/maodie.jpg'

const user = ref<PublicUser | null>(null)
const submissions = ref<PublicSubmission[]>([])
const loading = ref(true)
const error = ref('')

const memeSubmissions = computed(() => (
  submissions.value.filter((submission) => submission.submission_type === 'meme')
))

const musicSubmissions = computed(() => (
  submissions.value.filter((submission) => submission.submission_type === 'music')
))

function formatDate(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(value))
}

async function loadUser(uid: string) {
  loading.value = true
  error.value = ''
  user.value = null
  submissions.value = []

  try {
    const [userResponse, submissionsResponse] = await Promise.all([
      getPublicUser(uid),
      getPublicUserSubmissions(uid),
    ])

    user.value = userResponse.data
    submissions.value = submissionsResponse.data
  } catch (requestError) {
    console.error('加载公开资料失败', requestError)
    error.value = '没有找到这位基米居民，或资料暂时无法加载。'
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.uid,
  (uid) => {
    if (typeof uid === 'string' && uid) {
      loadUser(uid)
      return
    }

    user.value = null
    error.value = 'UID 无效。'
    loading.value = false
  },
  { immediate: true },
)
</script>

<template>
  <main class="user-page">
    <p v-if="loading" class="page-status">正在加载居民资料...</p>

    <section v-else-if="error" class="page-status error-card">
      <p>{{ error }}</p>
      <RouterLink to="/">返回首页 →</RouterLink>
    </section>

    <template v-else-if="user">
      <section class="user-card">
        <img
          :src="user.avatar_url || defaultAvatar"
          :alt="`${user.username} 的头像`"
          class="avatar"
        />

        <div class="profile-copy">
          <p class="section-kicker">KIMI RESIDENT</p>
          <h1>{{ user.username }}</h1>
          <p class="uid">UID {{ user.uid }}</p>
          <p class="joined-date">于 {{ formatDate(user.created_at) }} 加入基米小站</p>
        </div>

        <div class="haki-value">
          <span>哈气值</span>
          <strong>{{ user.haki_value }}</strong>
        </div>
      </section>

      <section class="submission-area">
        <p class="section-kicker">CONTRIBUTIONS</p>
        <h2>TA 的投稿</h2>
        <p>已向基米小站提交 {{ user.submission_count }} 个作品。</p>

        <div class="contribution-summary">
          <div>
            <span class="summary-icon">🖼</span>
            <strong>表情包</strong>
            <small>{{ memeSubmissions.length }} 个</small>
          </div>
          <div>
            <span class="summary-icon">🎵</span>
            <strong>音乐</strong>
            <small>{{ musicSubmissions.length }} 首</small>
          </div>
        </div>

        <RouterLink
          :to="`/users/${user.uid}/submissions`"
          class="submission-button"
        >
          查看全部投稿 →
        </RouterLink>
      </section>
    </template>
  </main>
</template>

<style scoped>
.user-page {
  width: min(960px, calc(100% - 48px));
  margin: 0 auto;
  padding: 72px 0 120px;
}

.user-card,
.submission-area,
.page-status {
  border: 1px solid rgba(246, 197, 52, 0.3);
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 18px 44px rgba(79, 61, 32, 0.1);
}

.user-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 28px;
  padding: 44px;
  background:
    radial-gradient(circle at 88% 10%, rgba(255, 221, 230, 0.7), transparent 30%),
    radial-gradient(circle at 8% 92%, rgba(255, 237, 159, 0.52), transparent 28%),
    #fffaf0;
}

.avatar {
  width: 148px;
  height: 148px;
  border: 5px solid #f6c534;
  border-radius: 50%;
  background: #fffdf7;
  object-fit: cover;
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
  font-size: clamp(34px, 5vw, 54px);
}

h2 {
  font-size: 28px;
}

.uid,
.joined-date,
.submission-area > p:last-child,
.empty-copy {
  color: #7b6a4a;
}

.uid {
  margin: 12px 0 0;
  font-weight: 900;
}

.joined-date {
  margin: 8px 0 0;
}

.haki-value {
  display: grid;
  min-width: 118px;
  padding: 16px 20px;
  border-radius: 24px;
  background: rgba(255, 253, 247, 0.82);
  color: #8c6a20;
  text-align: center;
}

.haki-value span {
  font-size: 13px;
  font-weight: 800;
}

.haki-value strong {
  margin-top: 4px;
  color: #25231f;
  font-size: 34px;
}

.submission-area {
  margin-top: 28px;
  padding: 32px 36px;
}

.submission-area h2 {
  margin-top: 4px;
}

.submission-area > p:last-child {
  margin: 14px 0 0;
  line-height: 1.7;
}

.contribution-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.contribution-summary > div {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 11px;
  padding: 18px;
  border: 1px solid #eadfca;
  border-radius: 22px;
  background: #fffdf7;
  color: #594828;
}

.contribution-summary small {
  color: #8a7550;
  font-size: 13px;
  font-weight: 800;
}

.summary-icon {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 50%;
  background: #fff0be;
}

.submission-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  margin-top: 22px;
  padding: 0 22px;
  border-radius: 999px;
  background: #f6c534;
  color: #352b1b;
  font-weight: 900;
  text-decoration: none;
}

.contribution-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
  margin-top: 26px;
}

.contribution-group {
  min-width: 0;
}

.contribution-group h3 {
  margin: 0;
  color: #594828;
  font-size: 17px;
}

.meme-submission {
  display: grid;
  grid-template-columns: 72px minmax(0, 1fr);
  align-items: center;
  gap: 12px;
  margin-top: 14px;
  padding: 10px;
  border: 1px solid #eadfca;
  border-radius: 18px;
  color: #594828;
  font-weight: 800;
  text-decoration: none;
}

.meme-submission img {
  width: 72px;
  height: 72px;
  border-radius: 12px;
  object-fit: cover;
}

.music-submission {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  margin-top: 14px;
  padding: 12px;
  border: 1px solid #eadfca;
  border-radius: 18px;
}

.music-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: #f6c534;
  color: #25231f;
  font-size: 22px;
  font-weight: 900;
}

.music-submission strong {
  color: #594828;
}

.music-submission p {
  margin: 5px 0 0;
  color: #7b6a4a;
  font-size: 13px;
  line-height: 1.5;
}

.music-submission audio {
  grid-column: 1 / -1;
  width: 100%;
}

.empty-copy {
  margin: 12px 0 0;
  line-height: 1.7;
}

.page-status {
  padding: 44px;
  color: #7b6a4a;
  font-weight: 700;
  text-align: center;
}

.error-card a {
  color: #9a7512;
  font-weight: 900;
  text-decoration: none;
}

@media (max-width: 680px) {
  .user-page {
    width: min(100% - 32px, 960px);
    padding-top: 44px;
  }

  .user-card {
    grid-template-columns: 1fr;
    padding: 32px;
  }

  .avatar {
    width: 112px;
    height: 112px;
  }

  .haki-value {
    justify-self: start;
  }

  .contribution-columns {
    grid-template-columns: 1fr;
  }

  .contribution-summary {
    grid-template-columns: 1fr;
  }
}
</style>
