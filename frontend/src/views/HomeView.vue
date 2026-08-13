<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getHealth } from '@/api/modules/system'

const loading = ref(true)
const error = ref('')
const backendStatus = ref('')
const databaseStatus = ref('')

async function checkBackend() {
  try {
    const response = await getHealth()

    backendStatus.value = response.data.backend
    databaseStatus.value = response.data.database
  } catch (err) {
    console.error(err)
    error.value = '无法连接后端'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkBackend()
})
</script>

<template>
  <main>
    <h1>哈基米网站开发测试</h1>

    <p v-if="loading">正在连接后端...</p>

    <div v-else-if="error">
      {{ error }}
    </div>

    <div v-else>
      <p>后端状态：{{ backendStatus }}</p>
      <p>数据库状态：{{ databaseStatus }}</p>
    </div>
  </main>
</template>
