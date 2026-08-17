<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { uploadMyAvatar } from '@/api/modules/users'
import { useAuthStore } from '@/stores/auth'
import { formatUid } from '@/utils/formatUid'

const router = useRouter()
const authStore = useAuthStore()

const defaultAvatar = '/static/images/avatars/maodie.jpg'
const allowedAvatarTypes = new Set([
  'image/jpeg',
  'image/png',
  'image/webp',
  'image/gif',
])
const maxAvatarSize = 2 * 1024 * 1024

const uploading = ref(false)
const error = ref('')
const success = ref('')

const avatarPreview = computed(() => authStore.user?.avatar_url || defaultAvatar)

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

async function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  error.value = ''
  success.value = ''

  if (!allowedAvatarTypes.has(file.type)) {
    error.value = '头像只支持 jpg、png、webp、gif 格式'
    input.value = ''
    return
  }

  if (file.size > maxAvatarSize) {
    error.value = '头像文件不能超过 2MB'
    input.value = ''
    return
  }

  uploading.value = true

  try {
    const response = await uploadMyAvatar(file)
    authStore.setUser(response.data)
    success.value = '头像更新成功'
  } catch (reason: unknown) {
    error.value = getErrorMessage(reason, '头像上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function goLogin() {
  router.push('/login')
}
</script>

<template>
  <main class="profile-page">
    <section v-if="authStore.user" class="profile-card">
      <div class="profile-header">
        <img class="profile-avatar" :src="avatarPreview" :alt="authStore.user.username" />

        <div>
          <p class="section-kicker">USER PROFILE</p>
          <h1>{{ authStore.user.username }}</h1>
          <p class="user-meta">
            UID {{ formatUid(authStore.user.id) }} · 哈气值 {{ authStore.user.haki_value }}
          </p>
        </div>
      </div>

      <div class="profile-block">
        <h2>自定义头像</h2>
        <p>支持 jpg、png、webp、gif，文件大小不超过 2MB。</p>

        <label class="upload-button" :class="{ disabled: uploading }">
          {{ uploading ? '上传中...' : '选择头像上传' }}
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp,image/gif"
            :disabled="uploading"
            @change="handleAvatarChange"
          />
        </label>

        <p v-if="success" class="success-text">{{ success }}</p>
        <p v-if="error" class="error-text">{{ error }}</p>
      </div>
    </section>

    <section v-else class="profile-card">
      <p class="section-kicker">NOT LOGIN</p>
      <h1>你还没有登录</h1>
      <p class="user-meta">登录后可以上传头像、投稿表情包和积累哈气值。</p>

      <button type="button" class="login-button" @click="goLogin">去登录</button>
    </section>
  </main>
</template>

<style scoped>
.profile-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 80px 24px 120px;
}

.profile-card {
  padding: 40px;
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.12);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 28px;
}

.profile-avatar {
  width: 120px;
  height: 120px;
  border: 4px solid #f6c534;
  border-radius: 50%;
  background: #fffdf7;
  object-fit: cover;
}

.section-kicker {
  margin: 0 0 10px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.profile-card h1 {
  margin: 0;
  color: #25231f;
  font-size: 42px;
}

.user-meta {
  margin: 12px 0 0;
  color: #7b6a4a;
  font-size: 16px;
  font-weight: 700;
}

.profile-block {
  margin-top: 36px;
  padding: 28px;
  border: 1px solid #eadfca;
  border-radius: 28px;
  background: #fffdf7;
}

.profile-block h2 {
  margin: 0;
  color: #25231f;
  font-size: 24px;
}

.profile-block p {
  margin: 10px 0 0;
  color: #7b6a4a;
  line-height: 1.7;
}

.upload-button,
.login-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  margin-top: 22px;
  padding: 0 24px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  cursor: pointer;
}

.upload-button.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-button input {
  display: none;
}

.success-text {
  color: #3b8f52 !important;
  font-weight: 800;
}

.error-text {
  color: #d64545 !important;
  font-weight: 800;
}

@media (max-width: 640px) {
  .profile-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-avatar {
    width: 96px;
    height: 96px;
  }

  .profile-card h1 {
    font-size: 34px;
  }
}
</style>
