<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref } from 'vue'

import {
  deleteAdminMeme,
  deleteAdminMusicTrack,
  getAdminSubmissions,
  updateAdminContentStatus,
  updateAdminContentFeatured,
} from '@/api/modules/admin'
import UserLink from '@/components/common/UserLink.vue'

import type { AdminSubmission } from '@/types/admin'

const submissions = ref<AdminSubmission[]>([])
const selectedType = ref<'all' | 'meme' | 'music'>('all')
const loading = ref(true)
const deletingId = ref<number | null>(null)
const featuringId = ref<number | null>(null)
const error = ref('')
const success = ref('')

function isContentActive(submission: AdminSubmission) {
  return !submission.content_deleted && submission.content_status === 'active'
}

function getContentStatusLabel(submission: AdminSubmission) {
  if (submission.content_deleted || submission.content_status === 'removed') {
    return '已下架'
  }

  if (submission.content_status === 'withdrawn') {
    return '用户撤回'
  }

  return submission.content_is_featured ? '已精选' : '已发布'
}

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

async function loadSubmissions() {
  loading.value = true
  error.value = ''

  try {
    const response = await getAdminSubmissions({
      submission_type: selectedType.value === 'all' ? undefined : selectedType.value,
    })
    submissions.value = response.data
  } catch (reason) {
    console.error('加载管理员内容列表失败', reason)
    error.value = getErrorMessage(reason, '内容列表暂时无法加载。')
  } finally {
    loading.value = false
  }
}

function changeType(type: 'all' | 'meme' | 'music') {
  selectedType.value = type
  void loadSubmissions()
}

async function removeContent(submission: AdminSubmission) {
  if (!submission.content_id || submission.content_deleted || submission.content_status === 'removed') return

  const confirmed = window.confirm(`确认下架“${submission.title}”吗？作品与历史会保留，之后可恢复发布。`)

  if (!confirmed) return

  error.value = ''
  success.value = ''
  deletingId.value = submission.id

  try {
    if (submission.submission_type === 'meme') {
      await deleteAdminMeme(submission.content_id)
    } else {
      await deleteAdminMusicTrack(submission.content_id)
    }

    submission.content_status = 'removed'
    submission.content_is_featured = false
    success.value = `已下架“${submission.title}”，作品与历史记录已保留。`
  } catch (reason) {
    console.error('下架内容失败', reason)
    error.value = getErrorMessage(reason, '下架失败，请稍后再试。')
  } finally {
    deletingId.value = null
  }
}

async function restoreContent(submission: AdminSubmission) {
  if (!submission.content_id || submission.content_deleted || isContentActive(submission)) return

  const confirmed = window.confirm(`确认恢复“${submission.title}”的公开展示吗？`)
  if (!confirmed) return

  error.value = ''
  success.value = ''
  deletingId.value = submission.id

  try {
    await updateAdminContentStatus(submission.submission_type, submission.content_id, 'active')
    submission.content_status = 'active'
    success.value = `已恢复“${submission.title}”的公开展示。`
  } catch (reason) {
    console.error('恢复内容失败', reason)
    error.value = getErrorMessage(reason, '恢复失败，请稍后再试。')
  } finally {
    deletingId.value = null
  }
}

async function toggleFeatured(submission: AdminSubmission) {
  if (!submission.content_id || !isContentActive(submission)) return

  const nextValue = !submission.content_is_featured
  const actionLabel = nextValue ? '精选' : '取消精选'

  if (!window.confirm(`确认${actionLabel}“${submission.title}”吗？首次精选会给创作者增加 50 哈气值。`)) {
    return
  }

  error.value = ''
  success.value = ''
  featuringId.value = submission.id

  try {
    await updateAdminContentFeatured(
      submission.submission_type,
      submission.content_id,
      nextValue,
    )
    submission.content_is_featured = nextValue
    success.value = nextValue
      ? `已精选“${submission.title}”。`
      : `已取消精选“${submission.title}”。`
  } catch (reason) {
    console.error('更新精选状态失败', reason)
    error.value = getErrorMessage(reason, '更新精选状态失败，请稍后再试。')
  } finally {
    featuringId.value = null
  }
}

onMounted(() => {
  void loadSubmissions()
})
</script>

<template>
  <main class="admin-page">
    <section class="page-heading">
      <div>
        <p class="section-kicker">CONTENT MODERATION</p>
        <h1>发布内容管理</h1>
        <p>所有用户发布会直接进入内容库；管理员可在此下架无关或不合规的图片与音乐。</p>
      </div>
      <RouterLink to="/admin">← 返回管理中心</RouterLink>
    </section>

    <section class="toolbar">
      <div class="filter-row">
        <button type="button" :class="{ active: selectedType === 'all' }" @click="changeType('all')">全部</button>
        <button type="button" :class="{ active: selectedType === 'meme' }" @click="changeType('meme')">表情包</button>
        <button type="button" :class="{ active: selectedType === 'music' }" @click="changeType('music')">音乐</button>
      </div>
      <button type="button" class="refresh-button" @click="loadSubmissions">刷新</button>
    </section>

    <p v-if="error" class="message error-message">{{ error }}</p>
    <p v-if="success" class="message success-message">{{ success }}</p>
    <p v-if="loading" class="message">正在加载全站发布内容...</p>

    <section v-else-if="submissions.length === 0" class="empty-panel">
      还没有用户发布内容。
    </section>

    <section v-else class="submission-grid">
      <article v-for="submission in submissions" :key="submission.id" class="submission-card">
        <div class="preview-box">
          <img
            v-if="submission.submission_type === 'meme' && !submission.content_deleted"
            :src="submission.file_url"
            :alt="submission.title"
          />
          <div
            v-else-if="submission.submission_type === 'meme'"
            class="removed-preview"
          >
            已下架
          </div>
          <div v-else class="music-preview">♪</div>
        </div>

        <div class="submission-copy">
          <div class="card-topline">
            <span>{{ submission.submission_type === 'meme' ? '表情包' : '音乐' }}</span>
            <span :class="{ removed: submission.content_deleted || submission.content_status === 'removed', withdrawn: submission.content_status === 'withdrawn', featured: submission.content_is_featured && submission.content_status === 'active' }">
              {{ getContentStatusLabel(submission) }}
            </span>
          </div>
          <h2>{{ submission.title }}</h2>
          <p>{{ submission.description || '发布者没有留下简介。' }}</p>
          <div class="submission-meta">
            <span>
              投稿人：<UserLink :uid="submission.author_uid" :name="submission.user.username" />
              · UID {{ submission.author_uid }}
            </span>
            <span>哈气值 {{ submission.user.haki_value }}</span>
          </div>

          <div v-if="submission.submission_type === 'music'" class="music-source-meta">
            <span>
              来源：{{
                submission.source_type === 'video_upload'
                  ? '上传视频自动提取'
                  : submission.source_type === 'douyin'
                    ? '抖音链接收录'
                    : '上传 MP3'
              }}
            </span>
            <span v-if="submission.source_author">视频作者：{{ submission.source_author }}</span>
            <a
              v-if="submission.source_url"
              :href="submission.source_url"
              target="_blank"
              rel="noreferrer"
            >
              打开原链接 ↗
            </a>
          </div>

          <audio
            v-if="submission.submission_type === 'music' && !submission.content_deleted"
            class="preview-audio"
            :src="submission.file_url"
            controls
            preload="metadata"
          />

          <div class="card-actions">
            <a
              v-if="!submission.content_deleted"
              :href="submission.file_url"
              target="_blank"
              rel="noreferrer"
            >
              查看原文件
            </a>
            <span v-else class="removed-file-note">原文件已移除</span>
            <button
              v-if="submission.content_id && isContentActive(submission)"
              type="button"
              class="feature-button"
              :disabled="featuringId === submission.id"
              @click="toggleFeatured(submission)"
            >
              {{ featuringId === submission.id ? '保存中...' : (submission.content_is_featured ? '取消精选' : '设为精选') }}
            </button>
            <button
              v-if="submission.content_id && !submission.content_deleted && submission.content_status !== 'removed'"
              type="button"
              class="remove-button"
              :disabled="deletingId === submission.id"
              @click="removeContent(submission)"
            >
              {{ deletingId === submission.id ? '下架中...' : '下架内容' }}
            </button>
            <button
              v-if="submission.content_id && !submission.content_deleted && !isContentActive(submission)"
              type="button"
              class="restore-button"
              :disabled="deletingId === submission.id"
              @click="restoreContent(submission)"
            >
              {{ deletingId === submission.id ? '恢复中...' : '恢复发布' }}
            </button>
            <span v-else-if="!submission.content_deleted" class="legacy-note">历史记录无关联内容</span>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.admin-page {
  width: min(1200px, calc(100% - 48px));
  margin: 0 auto;
  padding: 52px 0 120px;
}

.page-heading {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: clamp(32px, 5vw, 58px);
  border-radius: 40px;
  background: linear-gradient(135deg, #fff6cf, #ffe3ec);
}

.section-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
}

.page-heading h1 {
  margin: 0;
  color: #25231f;
  font-size: clamp(38px, 5vw, 58px);
  letter-spacing: -0.06em;
}

.page-heading p:not(.section-kicker) {
  max-width: 650px;
  margin: 18px 0 0;
  color: #6f6047;
  line-height: 1.75;
}

.page-heading a {
  align-self: start;
  color: #795c1b;
  font-size: 14px;
  font-weight: 900;
  text-decoration: none;
  white-space: nowrap;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-top: 28px;
  padding: 18px;
  border-radius: 24px;
  background: #fffaf0;
  box-shadow: 0 14px 30px rgba(79, 61, 32, 0.07);
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-row button,
.refresh-button,
.feature-button,
.remove-button {
  height: 42px;
  padding: 0 16px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #594828;
  font-weight: 800;
  cursor: pointer;
}

.filter-row button.active,
.refresh-button {
  border-color: #f6c534;
  background: #f6c534;
  color: #25231f;
}

.message,
.empty-panel {
  margin: 24px 0 0;
  padding: 20px 24px;
  border-radius: 22px;
  background: #fffaf0;
  color: #7b6a4a;
  font-weight: 700;
}

.error-message { color: #bd4747; }
.success-message { color: #3b8f52; }

.submission-grid {
  display: grid;
  gap: 20px;
  margin-top: 24px;
}

.submission-card {
  display: grid;
  grid-template-columns: 230px minmax(0, 1fr);
  overflow: hidden;
  border-radius: 28px;
  background: #fffaf0;
  box-shadow: 0 16px 34px rgba(79, 61, 32, 0.08);
}

.preview-box {
  min-height: 220px;
  background: #f4ead7;
}

.preview-box img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.music-preview {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 220px;
  place-items: center;
  background: radial-gradient(circle, #ffe3ec 0 26%, #25231f 27% 57%, #151412 58%);
  color: #fffaf0;
  font-size: 48px;
}

.removed-preview {
  display: grid;
  width: 100%;
  height: 100%;
  min-height: 220px;
  place-items: center;
  background: repeating-linear-gradient(
    -45deg,
    #f6eee1,
    #f6eee1 12px,
    #eee0cc 12px,
    #eee0cc 24px
  );
  color: #9d8656;
  font-size: 16px;
  font-weight: 900;
}

.submission-copy {
  padding: 26px;
}

.card-topline,
.submission-meta,
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.card-topline {
  justify-content: space-between;
  color: #9a7512;
  font-size: 13px;
  font-weight: 900;
}

.card-topline .removed {
  color: #bd4747;
}

.card-topline .withdrawn {
  color: #897558;
}

.card-topline .featured {
  color: #8c6511;
}

.submission-copy h2 {
  margin: 10px 0 0;
  color: #25231f;
  font-size: 24px;
}

.submission-copy > p {
  margin: 10px 0 0;
  color: #6f6047;
  line-height: 1.65;
}

.submission-meta {
  margin-top: 16px;
  color: #9d8656;
  font-size: 13px;
  font-weight: 800;
}

.music-source-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 12px;
  color: #806f50;
  font-size: 13px;
  font-weight: 750;
}

.music-source-meta a {
  color: #9a7512;
  font-weight: 900;
  text-decoration: none;
}

.preview-audio {
  width: 100%;
  margin-top: 16px;
}

.card-actions {
  align-items: center;
  margin-top: 18px;
}

.card-actions a {
  color: #9a7512;
  font-size: 14px;
  font-weight: 900;
  text-decoration: none;
}

.remove-button {
  border-color: #f1b7b7;
  background: #fff4f4;
  color: #af3e3e;
}

.feature-button {
  border-color: #f0c350;
  background: #fff2be;
  color: #715517;
}

.restore-button {
  height: 42px;
  padding: 0 16px;
  border: 1px solid #a9d4af;
  border-radius: 999px;
  background: #ecf9eb;
  color: #397448;
  font-weight: 800;
  cursor: pointer;
}

.remove-button:disabled,
.feature-button:disabled,
.restore-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.legacy-note {
  color: #9d8656;
  font-size: 13px;
}

.removed-file-note {
  color: #9d8656;
  font-size: 14px;
  font-weight: 800;
}

@media (max-width: 700px) {
  .admin-page {
    width: min(100% - 32px, 1200px);
    padding-top: 30px;
  }

  .page-heading,
  .toolbar {
    display: grid;
  }

  .submission-card {
    grid-template-columns: 1fr;
  }

  .preview-box,
  .music-preview,
  .removed-preview {
    min-height: 200px;
  }
}
</style>
