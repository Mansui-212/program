<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'

import { getFeaturedCharacters } from '@/api/modules/characters'
import { createSubmission, getMySubmissions } from '@/api/modules/submissions'
import { useAuthStore } from '@/stores/auth'

import type { Character } from '@/types/character'
import type { Submission } from '@/types/submission'

const authStore = useAuthStore()

const characters = ref<Character[]>([])
const mySubmissions = ref<Submission[]>([])

const submissionType = ref<'meme' | 'music'>('meme')
const title = ref('')
const description = ref('')
const characterIds = ref<number[]>([])
const sourceName = ref('')
const sourceUrl = ref('')
const authorName = ref('')
const selectedFile = ref<File | null>(null)
const fileInputKey = ref(0)

const loading = ref(false)
const error = ref('')
const success = ref('')

const memeTypes = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif'])
const musicTypes = new Set(['audio/mpeg', 'audio/mp3'])

const fileAccept = computed(() =>
  submissionType.value === 'meme'
    ? 'image/jpeg,image/png,image/webp,image/gif'
    : 'audio/mpeg,audio/mp3',
)

const fileHint = computed(() =>
  submissionType.value === 'meme'
    ? '支持 jpg、png、webp、gif，最大 10MB。'
    : '支持 MP3，最大 30MB。',
)

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

function getPublishLabel(submission: Submission) {
  return submission.content_deleted ? '已下架' : '已发布'
}

async function loadCharacters() {
  try {
    const response = await getFeaturedCharacters()
    characters.value = response.data
  } catch (reason) {
    console.error('加载角色列表失败', reason)
  }
}

async function loadMySubmissions() {
  if (!authStore.isLoggedIn) return

  try {
    const response = await getMySubmissions()
    mySubmissions.value = response.data
  } catch (reason) {
    console.error('加载我的投稿失败', reason)
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null

  selectedFile.value = null

  if (!file) return

  const allowedTypes = submissionType.value === 'meme' ? memeTypes : musicTypes
  const maxSize = submissionType.value === 'meme' ? 10 * 1024 * 1024 : 30 * 1024 * 1024

  if (!allowedTypes.has(file.type)) {
    error.value = submissionType.value === 'meme'
      ? '表情包只支持 jpg、png、webp、gif'
      : '音乐投稿暂时只支持 MP3'
    input.value = ''
    return
  }

  if (file.size > maxSize) {
    error.value = submissionType.value === 'meme'
      ? '表情包文件不能超过 10MB'
      : '音乐文件不能超过 30MB'
    input.value = ''
    return
  }

  error.value = ''
  selectedFile.value = file
}

async function submitForm() {
  if (!authStore.isLoggedIn) return

  const cleanedTitle = title.value.trim()

  if (!cleanedTitle) {
    error.value = '请填写投稿标题'
    return
  }

  if (!selectedFile.value) {
    error.value = '请选择投稿文件'
    return
  }

  error.value = ''
  success.value = ''
  loading.value = true

  try {
    await createSubmission({
      submission_type: submissionType.value,
      title: cleanedTitle,
      description: description.value,
      character_ids: characterIds.value,
      source_name: sourceName.value,
      source_url: sourceUrl.value,
      author_name: authorName.value,
      file: selectedFile.value,
    })

    success.value = '发布成功，已进入内容库并获得 10 哈气值'
    title.value = ''
    description.value = ''
    characterIds.value = []
    sourceName.value = ''
    sourceUrl.value = ''
    authorName.value = ''
    selectedFile.value = null
    fileInputKey.value += 1

    await authStore.fetchMe()
    await loadMySubmissions()
  } catch (reason: unknown) {
    error.value = getErrorMessage(reason, '投稿失败')
  } finally {
    loading.value = false
  }
}

watch(submissionType, () => {
  selectedFile.value = null
  error.value = ''
  fileInputKey.value += 1
})

watch(
  () => authStore.isLoggedIn,
  (isLoggedIn) => {
    if (isLoggedIn) {
      void loadMySubmissions()
    } else {
      mySubmissions.value = []
    }
  },
  { immediate: true },
)

onMounted(() => {
  void loadCharacters()
})
</script>

<template>
  <main class="submit-page">
    <section class="submit-hero">
      <p class="section-kicker">SUBMIT</p>
      <h1>投稿到基米小站</h1>
      <p>上传你的哈基米表情包或音乐，发布后会立即进入小站档案，并获得 10 哈气值。</p>
    </section>

    <section v-if="!authStore.isLoggedIn" class="submit-card">
      <h2>请先登录</h2>
      <p>登录后才能投稿并积累哈气值。</p>

      <RouterLink to="/login" class="primary-link">去登录</RouterLink>
    </section>

    <section v-else class="submit-layout">
      <form class="submit-card" @submit.prevent="submitForm">
        <h2>发布内容</h2>

        <label>
          投稿类型
          <select v-model="submissionType">
            <option value="meme">表情包 / 图片 / GIF</option>
            <option value="music">音乐 / MP3</option>
          </select>
        </label>

        <label>
          标题
          <input v-model="title" type="text" :maxlength="submissionType === 'meme' ? 120 : 160" required />
        </label>

        <fieldset class="character-selector">
          <legend>关联角色 <span>可多选</span></legend>
          <p>选择这份内容所属或相关的角色；不选也可以直接发布。</p>
          <div class="character-options">
            <label v-for="character in characters" :key="character.id" class="character-option">
              <input v-model="characterIds" type="checkbox" :value="character.id" />
              <span>{{ character.name }}</span>
            </label>
          </div>
        </fieldset>

        <label>
          简介
          <textarea v-model="description" rows="4" />
        </label>

        <label>
          来源名称
          <input v-model="sourceName" type="text" placeholder="例如：B站、微博、手动收录" />
        </label>

        <label>
          来源链接
          <input v-model="sourceUrl" type="url" placeholder="可选" />
        </label>

        <label>
          作者
          <input v-model="authorName" type="text" placeholder="不填则默认使用你的用户名" />
        </label>

        <label>
          文件
          <input
            :key="fileInputKey"
            type="file"
            :accept="fileAccept"
            required
            @change="handleFileChange"
          />
          <small>{{ fileHint }}</small>
          <small v-if="selectedFile">已选择：{{ selectedFile.name }}</small>
        </label>

        <p v-if="error" class="error-text">{{ error }}</p>
        <p v-if="success" class="success-text">{{ success }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? '发布中...' : '立即发布' }}
        </button>
      </form>

      <section class="submit-card">
        <h2>我的发布</h2>

        <p v-if="mySubmissions.length === 0" class="empty-text">暂无投稿。</p>

        <div v-else class="submission-list">
          <article v-for="submission in mySubmissions" :key="submission.id" class="submission-item">
            <div>
              <h3>{{ submission.title }}</h3>
              <p>
                {{ submission.submission_type === 'meme' ? '表情包' : '音乐' }}
                · {{ getPublishLabel(submission) }}
              </p>
            </div>

            <a :href="submission.file_url" target="_blank" rel="noreferrer">查看内容</a>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.submit-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px 120px;
}

.submit-hero {
  padding: 64px 72px;
  border-radius: 40px;
  background: linear-gradient(135deg, #fff6cf 0%, #ffe3ec 100%);
}

.section-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.submit-hero h1 {
  margin: 0;
  color: #25231f;
  font-size: 60px;
  line-height: 1;
}

.submit-hero p {
  margin: 24px 0 0;
  color: #6f6047;
  font-size: 18px;
}

.submit-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 420px;
  align-items: start;
  gap: 28px;
  margin-top: 36px;
}

.submit-card {
  margin-top: 36px;
  padding: 32px;
  border-radius: 32px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.submit-layout .submit-card {
  margin-top: 0;
}

.submit-card h2 {
  margin: 0 0 24px;
  color: #25231f;
  font-size: 28px;
}

form {
  display: grid;
  gap: 18px;
}

label {
  display: grid;
  gap: 8px;
  color: #594828;
  font-weight: 800;
}

.character-selector {
  margin: 0;
  padding: 0;
  border: 0;
}

.character-selector legend {
  color: #594828;
  font-weight: 800;
}

.character-selector legend span {
  margin-left: 6px;
  color: #a58a55;
  font-size: 12px;
  font-weight: 700;
}

.character-selector > p {
  margin: 8px 0 12px;
  color: #8a7655;
  font-size: 13px;
  line-height: 1.5;
}

.character-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.character-option {
  display: inline-flex;
  grid-template-columns: none;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  padding: 0 14px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #725c33;
  cursor: pointer;
}

.character-option:has(input:checked) {
  border-color: #f6c534;
  background: #fff0b8;
  color: #594828;
}

.character-option input {
  width: 16px;
  height: 16px;
  accent-color: #d6a818;
}

input,
select,
textarea {
  width: 100%;
  border: 1px solid #eadfca;
  border-radius: 18px;
  background: #fffdf7;
  color: #25231f;
  font-size: 15px;
}

input,
select {
  height: 48px;
  padding: 0 16px;
}

input[type='file'] {
  height: auto;
  padding: 12px 16px;
}

textarea {
  padding: 14px 16px;
  resize: vertical;
}

small {
  color: #8a7655;
  font-size: 13px;
  font-weight: 600;
}

button,
.primary-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 50px;
  padding: 0 24px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  text-decoration: none;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  margin: 0;
  color: #d64545;
  font-weight: 800;
}

.success-text {
  margin: 0;
  color: #3b8f52;
  font-weight: 800;
}

.empty-text {
  color: #7b6a4a;
}

.submission-list {
  display: grid;
  gap: 14px;
}

.submission-item {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border: 1px solid #eadfca;
  border-radius: 22px;
  background: #fffdf7;
}

.submission-item h3 {
  margin: 0;
  color: #25231f;
  font-size: 17px;
}

.submission-item p {
  margin: 6px 0 0;
  color: #7b6a4a;
  font-size: 14px;
  font-weight: 700;
}

.submission-item a {
  color: #9a7512;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .submit-layout {
    grid-template-columns: 1fr;
  }

  .submit-hero {
    padding: 48px 32px;
  }

  .submit-hero h1 {
    font-size: 42px;
  }
}
</style>
