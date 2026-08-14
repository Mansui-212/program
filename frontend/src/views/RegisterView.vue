<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

async function submitRegister() {
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true

  try {
    await authStore.register({
      username: username.value,
      password: password.value,
    })

    await router.push('/')
  } catch (reason: unknown) {
    error.value = getErrorMessage(reason, '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <p class="section-kicker">REGISTER</p>
      <h1>加入基米小站</h1>
      <p class="auth-desc">注册后可以上传哈基米表情包和音乐，审核通过后增加哈气值。</p>

      <form @submit.prevent="submitRegister">
        <label>
          用户名
          <input v-model="username" type="text" autocomplete="username" required minlength="3" />
        </label>

        <label>
          密码
          <input
            v-model="password"
            type="password"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </label>

        <label>
          确认密码
          <input
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            required
            minlength="6"
          />
        </label>

        <p v-if="error" class="error-text">{{ error }}</p>

        <button type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册并登录' }}
        </button>
      </form>

      <RouterLink to="/login" class="auth-link">已有账号？去登录 →</RouterLink>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 80px 24px;
  background:
    radial-gradient(circle at 12% 12%, rgba(255, 224, 105, 0.26), transparent 22rem), #fffdf7;
}

.auth-card {
  width: min(480px, 100%);
  padding: 40px;
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.12);
}

.section-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.auth-card h1 {
  margin: 0;
  color: #25231f;
  font-size: 40px;
}

.auth-desc {
  margin: 14px 0 28px;
  color: #7b6a4a;
  line-height: 1.7;
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

input {
  height: 48px;
  padding: 0 16px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #25231f;
  font-size: 15px;
}

button {
  height: 50px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  margin: 0;
  color: #d64545;
  font-weight: 700;
}

.auth-link {
  display: inline-block;
  margin-top: 22px;
  color: #9a7512;
  font-weight: 800;
  text-decoration: none;
}

@media (max-width: 520px) {
  .auth-card {
    padding: 30px 24px;
    border-radius: 28px;
  }

  .auth-card h1 {
    font-size: 32px;
  }
}
</style>
