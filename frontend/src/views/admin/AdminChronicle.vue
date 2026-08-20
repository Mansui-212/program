<script setup lang="ts">
import { onMounted, ref } from 'vue'

import {
  createAdminChronicleEvent,
  deleteAdminChronicleEvent,
  getAdminChronicleEvents,
  updateAdminChronicleEvent,
} from '@/api/modules/admin'

import type { ChronicleEvent, ChronicleEventPayload } from '@/types/chronicle'

const events = ref<ChronicleEvent[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')
const editingId = ref<number | null>(null)

const form = ref<ChronicleEventPayload>({
  year: new Date().getFullYear(),
  date: '',
  title: '',
  content: '',
  image_url: '',
  sort_order: 0,
})

function resetForm() {
  editingId.value = null
  form.value = {
    year: new Date().getFullYear(),
    date: '',
    title: '',
    content: '',
    image_url: '',
    sort_order: 0,
  }
}

async function loadEvents() {
  loading.value = true
  error.value = ''

  try {
    const response = await getAdminChronicleEvents()
    events.value = response.data
  } catch (reason) {
    console.error('加载编年史管理数据失败', reason)
    error.value = '无法加载编年史事件。'
  } finally {
    loading.value = false
  }
}

function editEvent(event: ChronicleEvent) {
  editingId.value = event.id
  form.value = {
    year: event.year,
    date: event.date || '',
    title: event.title,
    content: event.content,
    image_url: event.image_url || '',
    sort_order: event.sort_order,
  }
  success.value = ''
  error.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function saveEvent() {
  saving.value = true
  error.value = ''
  success.value = ''

  const payload: ChronicleEventPayload = {
    ...form.value,
    date: form.value.date || null,
    image_url: form.value.image_url || null,
  }

  try {
    if (editingId.value) {
      await updateAdminChronicleEvent(editingId.value, payload)
      success.value = '编年史事件已更新。'
    } else {
      await createAdminChronicleEvent(payload)
      success.value = '新的编年史事件已写入。'
    }

    resetForm()
    await loadEvents()
  } catch (reason) {
    console.error('保存编年史事件失败', reason)
    error.value = '保存失败，请检查填写内容后重试。'
  } finally {
    saving.value = false
  }
}

async function removeEvent(event: ChronicleEvent) {
  if (!window.confirm(`确认删除「${event.title}」吗？`)) return

  error.value = ''
  success.value = ''

  try {
    await deleteAdminChronicleEvent(event.id)

    if (editingId.value === event.id) {
      resetForm()
    }

    success.value = '事件已删除。'
    await loadEvents()
  } catch (reason) {
    console.error('删除编年史事件失败', reason)
    error.value = '删除失败，请稍后再试。'
  }
}

onMounted(() => {
  void loadEvents()
})
</script>

<template>
  <main class="admin-page">
    <section class="admin-hero">
      <p class="section-kicker">CHRONICLE ADMIN</p>
      <h1>编年史编辑台</h1>
      <p>新增、调整或删除事件后，公开时间轴会自动按年份更新，不需要再改前端页面。</p>
    </section>

    <section class="admin-layout">
      <form class="editor-card" @submit.prevent="saveEvent">
        <div class="card-heading">
          <div>
            <p class="eyebrow">{{ editingId ? 'EDIT EVENT' : 'NEW EVENT' }}</p>
            <h2>{{ editingId ? '编辑事件' : '写入新事件' }}</h2>
          </div>
          <button v-if="editingId" type="button" class="plain-button" @click="resetForm">取消编辑</button>
        </div>

        <div class="field-row">
          <label>
            年份
            <input v-model.number="form.year" type="number" min="2000" max="2100" required />
          </label>
          <label>
            日期
            <input v-model="form.date" type="text" placeholder="例如：2024-09-11" />
          </label>
          <label>
            排序
            <input v-model.number="form.sort_order" type="number" />
          </label>
        </div>

        <label>
          标题
          <input v-model.trim="form.title" type="text" maxlength="200" required />
        </label>

        <label>
          内容
          <textarea v-model.trim="form.content" rows="7" required></textarea>
        </label>

        <label>
          配图地址（可选）
          <input v-model.trim="form.image_url" type="text" placeholder="/static/images/..." />
        </label>

        <p v-if="error" class="message error-message">{{ error }}</p>
        <p v-if="success" class="message success-message">{{ success }}</p>

        <button class="primary-button" type="submit" :disabled="saving">
          {{ saving ? '保存中...' : editingId ? '保存修改' : '写入编年史' }}
        </button>
      </form>

      <section class="events-card">
        <div class="card-heading">
          <div>
            <p class="eyebrow">ARCHIVE</p>
            <h2>已有事件</h2>
          </div>
          <span>{{ events.length }} 条</span>
        </div>

        <p v-if="loading" class="message">正在读取档案...</p>
        <p v-else-if="events.length === 0" class="message">暂无事件。</p>

        <div v-else class="event-items">
          <article v-for="event in events" :key="event.id">
            <div>
              <span>{{ event.date || event.year }}</span>
              <h3>{{ event.title }}</h3>
              <p>{{ event.content }}</p>
            </div>
            <div class="item-actions">
              <button type="button" @click="editEvent(event)">编辑</button>
              <button type="button" class="danger-button" @click="removeEvent(event)">删除</button>
            </div>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.admin-page { width: min(1160px, calc(100% - 48px)); margin: 0 auto; padding: 52px 0 120px; }
.admin-hero { padding: clamp(34px, 6vw, 68px); border-radius: 40px; background: linear-gradient(135deg, #fff4c8, #ffe4ed 56%, #f3eaff); box-shadow: 0 24px 60px rgba(79, 61, 32, 0.1); }
.section-kicker, .eyebrow { margin: 0 0 12px; color: #b88a12; font-size: 13px; font-weight: 900; letter-spacing: 0.13em; }
.admin-hero h1 { margin: 0; color: #25231f; font-size: clamp(42px, 6vw, 66px); letter-spacing: -0.06em; }
.admin-hero > p:not(.section-kicker) { max-width: 650px; margin: 20px 0 0; color: #6f6047; line-height: 1.8; }
.admin-layout { display: grid; grid-template-columns: minmax(0, 0.95fr) minmax(380px, 1.05fr); gap: 26px; margin-top: 30px; align-items: start; }
.editor-card, .events-card { padding: 30px; border: 1px solid #eadfca; border-radius: 30px; background: #fffaf0; box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08); }
.card-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; margin-bottom: 25px; }
.card-heading h2 { margin: 0; color: #25231f; font-size: 26px; letter-spacing: -0.045em; }
.card-heading > span { color: #9b7b39; font-size: 13px; font-weight: 850; }
form { display: grid; gap: 17px; }
label { display: grid; gap: 8px; color: #594828; font-size: 14px; font-weight: 850; }
.field-row { display: grid; grid-template-columns: 1fr 1.4fr 0.8fr; gap: 12px; }
input, textarea { width: 100%; box-sizing: border-box; border: 1px solid #eadfca; border-radius: 16px; padding: 12px 14px; background: #fffdf7; color: #25231f; font: inherit; }
textarea { line-height: 1.7; resize: vertical; }
.primary-button, .plain-button, .item-actions button { min-height: 42px; border: 1px solid #eadfca; border-radius: 999px; padding: 0 16px; background: #fffdf7; color: #594828; font: inherit; font-size: 13px; font-weight: 850; cursor: pointer; }
.primary-button { border-color: #f6c534; background: #f6c534; color: #31270f; }
.primary-button:disabled { opacity: 0.6; cursor: not-allowed; }
.message { margin: 0; color: #7b6a4a; line-height: 1.6; }
.error-message { color: #bd4747; font-weight: 800; }
.success-message { color: #3b8752; font-weight: 800; }
.event-items { display: grid; gap: 13px; }
.event-items article { display: flex; justify-content: space-between; gap: 18px; padding: 17px; border: 1px solid #eee1ca; border-radius: 21px; background: #fffdf7; }
.event-items span { color: #a38754; font-size: 12px; font-weight: 900; }
.event-items h3 { margin: 5px 0 0; color: #302c24; font-size: 17px; }
.event-items p { display: -webkit-box; overflow: hidden; margin: 7px 0 0; color: #7b6a4a; font-size: 13px; line-height: 1.65; -webkit-box-orient: vertical; -webkit-line-clamp: 2; }
.item-actions { display: flex; height: fit-content; gap: 7px; }
.item-actions button { min-height: 34px; padding: 0 10px; }
.item-actions .danger-button { border-color: #f2cdcd; color: #b54c4c; }
@media (max-width: 900px) { .admin-layout { grid-template-columns: 1fr; } }
@media (max-width: 600px) { .admin-page { width: calc(100% - 32px); padding-top: 30px; } .editor-card, .events-card { padding: 22px; } .field-row { grid-template-columns: 1fr; } .event-items article { flex-direction: column; } }
</style>
