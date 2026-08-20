<script setup lang="ts">
import { ref, watch } from 'vue'

import { getMemeDetail } from '@/api/modules/memes'
import UserLink from '@/components/common/UserLink.vue'

import type { Meme, MemeDetail } from '@/types/meme'

const props = defineProps<{
  meme: Meme | null
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const detail = ref<MemeDetail | null>(null)
const loading = ref(false)
const error = ref('')

async function loadDetail() {
  if (!props.meme) {
    detail.value = null
    return
  }

  loading.value = true
  error.value = ''

  try {
    const response = await getMemeDetail(props.meme.slug)
    detail.value = response.data
  } catch (err) {
    console.error(err)
    error.value = '加载表情包详情失败'
  } finally {
    loading.value = false
  }
}

function closeModal() {
  emit('close')
}

function openOriginalImage() {
  if (!detail.value?.image_url) return

  window.open(detail.value.image_url, '_blank')
}

watch(
  () => props.meme?.slug,
  () => {
    loadDetail()
  },
  {
    immediate: true,
  },
)
</script>

<template>
  <Teleport to="body">
    <div v-if="meme" class="modal-mask" @click.self="closeModal">
      <section class="modal-panel" aria-modal="true" role="dialog">
        <button type="button" class="modal-close" aria-label="关闭预览" @click="closeModal">×</button>

        <p v-if="loading" class="modal-status">正在加载详情...</p>

        <p v-else-if="error" class="modal-status">{{ error }}</p>

        <div v-else-if="detail" class="modal-content">
          <div class="preview-box">
            <img :src="detail.image_url" :alt="detail.title" />
          </div>

          <div class="detail-box">
            <p class="detail-kicker">MEME DETAIL</p>

            <h2>{{ detail.title }}</h2>

            <p v-if="detail.description" class="description">{{ detail.description }}</p>

            <div class="info-list">
              <div>
                <span>所属角色</span>
                <strong>{{ detail.character?.name || '未分类' }}</strong>
              </div>

              <div>
                <span>来源</span>
                <strong>{{ detail.source_name || '未知来源' }}</strong>
              </div>

              <div>
                <span>作者</span>
                <strong><UserLink :uid="detail.author_uid" :name="detail.author_name" /></strong>
              </div>

              <div>
                <span>浏览量</span>
                <strong>{{ detail.view_count }}</strong>
              </div>
            </div>

            <div class="action-row">
              <button type="button" @click="openOriginalImage">查看原图</button>

              <a :href="detail.image_url" :download="`${detail.slug}.png`">下载图片</a>
            </div>
          </div>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 32px;
  background: rgba(37, 35, 31, 0.48);
  backdrop-filter: blur(10px);
}

.modal-panel {
  position: relative;
  width: min(1080px, 100%);
  max-height: calc(100vh - 64px);
  overflow: auto;
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 32px 100px rgba(37, 35, 31, 0.28);
}

.modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 2;
  width: 44px;
  height: 44px;
  border: 0;
  border-radius: 999px;
  background: #25231f;
  color: #fffaf0;
  font-size: 28px;
  line-height: 1;
  cursor: pointer;
}

.modal-status {
  padding: 80px;
  color: #7b6a4a;
  font-size: 18px;
  text-align: center;
}

.modal-content {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 32px;
  padding: 40px;
}

.preview-box {
  display: grid;
  min-height: 520px;
  place-items: center;
  border-radius: 28px;
  background:
    radial-gradient(circle at 20% 20%, #fff6cf 0, transparent 32%),
    radial-gradient(circle at 80% 10%, #ffe3ec 0, transparent 34%),
    #fffdf7;
}

.preview-box img {
  display: block;
  max-width: 100%;
  max-height: 640px;
  object-fit: contain;
}

.detail-box {
  padding: 24px 8px 24px 0;
}

.detail-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.detail-box h2 {
  margin: 0;
  color: #25231f;
  font-size: 42px;
  line-height: 1.1;
}

.description {
  margin: 20px 0 0;
  color: #6f6047;
  font-size: 16px;
  line-height: 1.8;
}

.info-list {
  display: grid;
  gap: 14px;
  margin-top: 28px;
}

.info-list div {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 14px 0;
  border-bottom: 1px solid #eadfca;
}

.info-list span {
  color: #9d8656;
  font-size: 14px;
  font-weight: 700;
}

.info-list strong {
  color: #25231f;
  font-size: 15px;
  text-align: right;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 32px;
}

.action-row button,
.action-row a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 24px;
  border: 1px solid #f6c534;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 800;
  text-decoration: none;
  cursor: pointer;
}

.action-row a {
  background: #fffdf7;
}

@media (max-width: 860px) {
  .modal-content {
    grid-template-columns: 1fr;
  }

  .preview-box {
    min-height: 360px;
  }

  .detail-box {
    padding: 0;
  }

  .detail-box h2 {
    font-size: 32px;
  }
}
</style>
