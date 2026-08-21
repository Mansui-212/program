<script setup lang="ts">
import axios from 'axios'
import { onMounted, ref } from 'vue'

import {
  adjustAdminUserHaki,
  getAdminUserHakiRecords,
  getAdminUsers,
} from '@/api/modules/admin'
import { useAuthStore } from '@/stores/auth'

import type { AdminUser, HakiRecord } from '@/types/admin'
import { formatUid } from '@/utils/formatUid'

const authStore = useAuthStore()
const users = ref<AdminUser[]>([])
const keyword = ref('')
const loading = ref(true)
const savingUserId = ref<number | null>(null)
const recordsUserId = ref<number | null>(null)
const records = ref<HakiRecord[]>([])
const changes = ref<Record<number, number>>({})
const reasons = ref<Record<number, string>>({})
const error = ref('')
const success = ref('')

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

async function loadUsers() {
  loading.value = true
  error.value = ''

  try {
    const response = await getAdminUsers(keyword.value.trim() || undefined)
    users.value = response.data
  } catch (reason) {
    console.error('加载管理员用户列表失败', reason)
    error.value = getErrorMessage(reason, '用户列表暂时无法加载。')
  } finally {
    loading.value = false
  }
}

async function adjustHaki(user: AdminUser) {
  const changeValue = changes.value[user.id] || 0
  const reason = reasons.value[user.id]?.trim() || ''

  if (!changeValue) {
    error.value = '请输入非 0 的哈气值调整数量。'
    return
  }

  if (!reason) {
    error.value = '请填写调整原因。'
    return
  }

  error.value = ''
  success.value = ''
  savingUserId.value = user.id

  try {
    const response = await adjustAdminUserHaki(user.id, changeValue, reason)
    const updatedUser = response.data
    users.value = users.value.map((item) => (item.id === updatedUser.id ? updatedUser : item))

    if (authStore.user?.id === updatedUser.id) {
      authStore.setUser({ ...authStore.user, haki_value: updatedUser.haki_value })
    }

    changes.value[user.id] = 0
    reasons.value[user.id] = ''
    success.value = `已调整 ${updatedUser.username} 的哈气值。`

    if (recordsUserId.value === user.id) {
      await showRecords(user.id)
    }
  } catch (reason) {
    console.error('调整哈气值失败', reason)
    error.value = getErrorMessage(reason, '哈气值调整失败。')
  } finally {
    savingUserId.value = null
  }
}

async function showRecords(userId: number) {
  if (recordsUserId.value === userId) {
    recordsUserId.value = null
    records.value = []
    return
  }

  error.value = ''

  try {
    const response = await getAdminUserHakiRecords(userId)
    recordsUserId.value = userId
    records.value = response.data
  } catch (reason) {
    console.error('加载哈气值流水失败', reason)
    error.value = getErrorMessage(reason, '哈气值流水暂时无法加载。')
  }
}

onMounted(() => {
  void loadUsers()
})
</script>

<template>
  <main class="admin-page">
    <section class="page-heading">
      <div>
        <p class="section-kicker">USER MANAGEMENT</p>
        <h1>用户与哈气值</h1>
        <p>哈气值的每次手动调整都会写入流水，避免只改总数而无法追踪原因。</p>
      </div>
      <RouterLink to="/admin">← 返回管理中心</RouterLink>
    </section>

    <section class="search-row">
      <input v-model="keyword" type="search" placeholder="搜索用户名" @keyup.enter="loadUsers" />
      <button type="button" @click="loadUsers">搜索</button>
    </section>

    <p v-if="error" class="message error-message">{{ error }}</p>
    <p v-if="success" class="message success-message">{{ success }}</p>
    <p v-if="loading" class="message">正在加载用户...</p>

    <section v-else class="user-list">
      <article v-for="user in users" :key="user.id" class="user-card">
        <div class="user-summary">
          <img :src="user.avatar_url || '/static/images/avatars/maodie.jpg'" :alt="user.username" />
          <div>
            <div class="user-name-row">
              <RouterLink
                class="user-profile-link"
                :to="`/users/${formatUid(user.id)}`"
              >
                {{ user.username }}
              </RouterLink>
              <span :class="{ admin: user.role === 'admin' }">{{ user.role === 'admin' ? '管理员' : '用户' }}</span>
            </div>
            <p>UID {{ formatUid(user.id) }} · 当前哈气值 <strong>{{ user.haki_value }}</strong></p>
          </div>
        </div>

        <form class="haki-form" @submit.prevent="adjustHaki(user)">
          <label>
            调整值
            <input v-model.number="changes[user.id]" type="number" min="-10000" max="10000" placeholder="例如 +10 或 -10" />
          </label>
          <label>
            原因
            <input v-model="reasons[user.id]" type="text" maxlength="255" placeholder="例如：活动奖励" />
          </label>
          <button type="submit" :disabled="savingUserId === user.id">
            {{ savingUserId === user.id ? '保存中...' : '调整哈气值' }}
          </button>
        </form>

        <button type="button" class="record-button" @click="showRecords(user.id)">
          {{ recordsUserId === user.id ? '收起哈气值流水' : '查看哈气值流水' }}
        </button>

        <div v-if="recordsUserId === user.id" class="record-list">
          <p v-if="records.length === 0">还没有哈气值流水。</p>
          <div v-for="record in records" :key="record.id" class="record-item">
            <strong :class="{ minus: record.change_value < 0 }">
              {{ record.change_value > 0 ? '+' : '' }}{{ record.change_value }}
            </strong>
            <span>
              {{ record.reason }}
              <small v-if="record.target_type && record.target_id">
                · {{ record.target_type }} #{{ record.target_id }}
              </small>
            </span>
            <time>{{ new Date(record.created_at).toLocaleString() }}</time>
          </div>
        </div>
      </article>
    </section>
  </main>
</template>

<style scoped>
.admin-page {
  width: min(1100px, calc(100% - 48px));
  margin: 0 auto;
  padding: 52px 0 120px;
}

.page-heading {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: clamp(32px, 5vw, 58px);
  border-radius: 40px;
  background: linear-gradient(135deg, #e9e0ff, #ffe3ec 58%, #fff6cf);
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
  max-width: 590px;
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

.search-row {
  display: flex;
  gap: 10px;
  margin-top: 28px;
  padding: 10px;
  border-radius: 999px;
  background: #fffaf0;
  box-shadow: 0 14px 30px rgba(79, 61, 32, 0.07);
}

.search-row input {
  min-width: 0;
  height: 44px;
  flex: 1;
  padding: 0 16px;
  border: 0;
  outline: 0;
  background: transparent;
  color: #25231f;
  font: inherit;
}

.search-row button,
.haki-form button,
.record-button {
  height: 44px;
  padding: 0 16px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  cursor: pointer;
}

.message {
  margin: 24px 0 0;
  padding: 18px 22px;
  border-radius: 20px;
  background: #fffaf0;
  color: #7b6a4a;
  font-weight: 800;
}

.error-message { color: #bd4747; }
.success-message { color: #3b8f52; }

.user-list {
  display: grid;
  gap: 20px;
  margin-top: 24px;
}

.user-card {
  padding: 26px;
  border-radius: 28px;
  background: #fffaf0;
  box-shadow: 0 16px 34px rgba(79, 61, 32, 0.08);
}

.user-summary {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-summary > img {
  width: 64px;
  height: 64px;
  border: 3px solid #f6c534;
  border-radius: 50%;
  object-fit: cover;
  background: #fffdf7;
}

.user-name-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.user-profile-link {
  color: #25231f;
  font-size: 23px;
  font-weight: 900;
  text-decoration: none;
}

.user-profile-link:hover {
  color: #9a7512;
  text-decoration: underline;
}

.user-name-row h2 {
  margin: 0;
  color: #25231f;
  font-size: 23px;
}

.user-name-row span {
  padding: 4px 8px;
  border-radius: 999px;
  background: #ece6dc;
  color: #6f6047;
  font-size: 12px;
  font-weight: 900;
}

.user-name-row span.admin {
  background: #fff0b8;
  color: #795c1b;
}

.user-summary p {
  margin: 7px 0 0;
  color: #7b6a4a;
  font-size: 14px;
}

.user-summary strong {
  color: #9a7512;
}

.haki-form {
  display: grid;
  grid-template-columns: 160px minmax(0, 1fr) auto;
  align-items: end;
  gap: 12px;
  margin-top: 22px;
}

.haki-form label {
  display: grid;
  gap: 7px;
  color: #594828;
  font-size: 13px;
  font-weight: 800;
}

.haki-form input {
  width: 100%;
  height: 44px;
  padding: 0 13px;
  border: 1px solid #eadfca;
  border-radius: 14px;
  background: #fffdf7;
  color: #25231f;
  font: inherit;
}

.haki-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.record-button {
  margin-top: 15px;
  background: #fffdf7;
  box-shadow: inset 0 0 0 1px #eadfca;
  color: #725c33;
}

.record-list {
  display: grid;
  gap: 10px;
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #eadfca;
  border-radius: 18px;
  background: #fffdf7;
}

.record-list > p {
  margin: 0;
  color: #7b6a4a;
  font-size: 14px;
}

.record-item {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  color: #725c33;
  font-size: 13px;
}

.record-item strong {
  color: #3b8f52;
}

.record-item strong.minus {
  color: #bd4747;
}

.record-item time {
  color: #9d8656;
  font-size: 12px;
  white-space: nowrap;
}

@media (max-width: 680px) {
  .admin-page {
    width: min(100% - 32px, 1100px);
    padding-top: 30px;
  }

  .page-heading,
  .haki-form {
    display: grid;
    grid-template-columns: 1fr;
  }

  .record-item {
    grid-template-columns: 48px minmax(0, 1fr);
  }

  .record-item time {
    grid-column: 2;
  }
}
</style>
