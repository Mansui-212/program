<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'

import { batchUploadAdminMemes } from '@/api/modules/admin'
import { getCharacters } from '@/api/modules/characters'

import type { BatchMemeUploadResult } from '@/types/admin'
import type { Character } from '@/types/character'

const characters = ref<Character[]>([])
const selectedFiles = ref<File[]>([])
const characterId = ref<number | null>(null)
const sourceName = ref('网络收集')
const loadingCharacters = ref(true)
const uploading = ref(false)
const error = ref('')
const result = ref<BatchMemeUploadResult | null>(null)

const selectedFileCount = computed(() => selectedFiles.value.length)
const hasZip = computed(() =>
  selectedFiles.value.some((file) => file.name.toLowerCase().endsWith('.zip')),
)

function getErrorMessage(reason: unknown, fallback: string) {
  if (axios.isAxiosError<{ detail?: string }>(reason)) {
    return reason.response?.data?.detail || fallback
  }

  return fallback
}

async function loadCharacters() {
  loadingCharacters.value = true

  try {
    const response = await getCharacters()
    characters.value = response.data
  } catch (reason) {
    console.error('加载角色列表失败', reason)
    error.value = '角色列表暂时无法加载。'
  } finally {
    loadingCharacters.value = false
  }
}

function chooseFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])

  if (!files.length) return

  selectedFiles.value = files
  result.value = null
  error.value = ''
  input.value = ''
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
  result.value = null
}

function clearFiles() {
  selectedFiles.value = []
  result.value = null
}

async function submitBatch() {
  if (!characterId.value) {
    error.value = '请选择这批表情包关联的角色。'
    return
  }

  if (!selectedFiles.value.length) {
    error.value = '请选择图片文件或 ZIP 压缩包。'
    return
  }

  uploading.value = true
  error.value = ''
  result.value = null

  try {
    const response = await batchUploadAdminMemes({
      files: selectedFiles.value,
      characterId: characterId.value,
      sourceName: sourceName.value,
    })
    result.value = response.data
    selectedFiles.value = []
  } catch (reason) {
    console.error('批量导入表情包失败', reason)
    error.value = getErrorMessage(reason, '批量导入失败，请稍后重试。')
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  void loadCharacters()
})
</script>

<template>
  <main class="batch-page">
    <section class="page-heading">
      <div>
        <p class="section-kicker">MEME BULK IMPORT</p>
        <h1>表情包批量导入</h1>
        <p>把同一角色的图片或 ZIP 直接收录进表情包档案。系统会校验图片内容，并跳过重复素材。</p>
      </div>
      <RouterLink to="/admin">← 返回管理中心</RouterLink>
    </section>

    <section class="batch-layout">
      <form class="upload-card" @submit.prevent="submitBatch">
        <div class="card-heading">
          <div>
            <p>批量收录</p>
            <h2>选择素材与归档信息</h2>
          </div>
          <span>管理员专用</span>
        </div>

        <label class="field">
          <span>关联角色</span>
          <select v-model="characterId" :disabled="loadingCharacters || uploading" required>
            <option :value="null" disabled>
              {{ loadingCharacters ? '正在加载角色…' : '请选择角色' }}
            </option>
            <option v-for="character in characters" :key="character.id" :value="character.id">
              {{ character.name }}
            </option>
          </select>
        </label>

        <label class="field">
          <span>来源</span>
          <input
            v-model="sourceName"
            type="text"
            maxlength="120"
            :disabled="uploading"
            placeholder="例如：网络收集"
          />
        </label>

        <div class="field">
          <span>图片或 ZIP</span>
          <label class="file-drop">
            <input
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp,image/gif,.zip,application/zip"
              :disabled="uploading"
              @change="chooseFiles"
            />
            <b>选择文件</b>
            <small>支持 JPG、PNG、WebP、GIF，或一个 ZIP 压缩包</small>
          </label>
        </div>

        <div v-if="selectedFileCount" class="file-summary">
          <div>
            <strong>已选择 {{ selectedFileCount }} 个文件</strong>
            <span v-if="hasZip">包含 ZIP，服务端会逐张解压并检查</span>
            <span v-else>服务端会逐张检查格式和重复内容</span>
          </div>
          <button type="button" class="text-button" :disabled="uploading" @click="clearFiles">
            清空
          </button>
        </div>

        <ul v-if="selectedFileCount" class="file-list">
          <li
            v-for="(file, index) in selectedFiles"
            :key="`${file.name}-${file.lastModified}-${index}`"
          >
            <span>{{ file.name }}</span>
            <small>{{ (file.size / 1024 / 1024).toFixed(2) }} MB</small>
            <button type="button" :disabled="uploading" @click="removeFile(index)">移除</button>
          </li>
        </ul>

        <p class="limits">
          单张图片最多 10MB；ZIP 最多 100MB；单次最多处理 500 张、合计图片不超过 100MB。
        </p>

        <button class="primary-button" type="submit" :disabled="uploading || loadingCharacters">
          {{ uploading ? '正在导入…' : '开始导入表情包' }}
        </button>
      </form>

      <aside class="rule-card">
        <p class="section-kicker">IMPORT RULES</p>
        <h2>导入规则</h2>
        <ul>
          <li>文件名会自动作为表情包标题，可在内容管理中后续编辑。</li>
          <li>同一批次或表情包库中内容完全相同的图片会被跳过。</li>
          <li>导入后会立即公开；发现不相关内容可在内容管理中下架。</li>
          <li>本次导入按每张 2 哈气计算，单次最高增加 100 哈气。</li>
        </ul>
      </aside>
    </section>

    <p v-if="error" class="message error-message">{{ error }}</p>

    <section v-if="result" class="result-card">
      <div class="result-heading">
        <div>
          <p class="section-kicker">IMPORT COMPLETE</p>
          <h2>批量导入完成</h2>
        </div>
        <span class="haki-badge">+{{ result.haki_gained }} 哈气值</span>
      </div>

      <div class="result-stats">
        <article>
          <span>候选图片</span><strong>{{ result.total_candidates }}</strong>
        </article>
        <article class="success">
          <span>成功导入</span><strong>{{ result.imported }}</strong>
        </article>
        <article class="duplicate">
          <span>重复跳过</span><strong>{{ result.skipped_duplicates }}</strong>
        </article>
        <article class="invalid">
          <span>无效跳过</span><strong>{{ result.skipped_invalid }}</strong>
        </article>
      </div>

      <ul v-if="result.items.length" class="result-list">
        <li
          v-for="item in result.items"
          :key="`${item.status}-${item.filename}`"
          :class="item.status"
        >
          <span class="result-mark">{{
            item.status === 'imported' ? '✓' : item.status === 'duplicate' ? '—' : '!'
          }}</span>
          <div>
            <strong>{{ item.filename }}</strong>
            <small>{{ item.title || item.detail || '已处理' }}</small>
          </div>
          <em>{{
            item.status === 'imported' ? '已导入' : item.status === 'duplicate' ? '重复' : '已跳过'
          }}</em>
        </li>
      </ul>
    </section>
  </main>
</template>

<style scoped>
.batch-page {
  width: min(1160px, calc(100% - 48px));
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
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.1);
}
.section-kicker {
  margin: 0 0 11px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
}
.page-heading h1,
.result-card h2,
.upload-card h2,
.rule-card h2 {
  margin: 0;
  color: #25231f;
}
.page-heading h1 {
  font-size: clamp(38px, 5vw, 58px);
  letter-spacing: -0.06em;
}
.page-heading p:not(.section-kicker) {
  max-width: 650px;
  margin: 18px 0 0;
  color: #6f6047;
  line-height: 1.75;
}
.page-heading > a {
  align-self: flex-start;
  color: #8a6815;
  font-weight: 850;
  text-decoration: none;
}
.batch-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 26px;
  margin-top: 30px;
  align-items: start;
}
.upload-card,
.rule-card,
.result-card {
  border: 1px solid #eadfca;
  border-radius: 32px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}
.upload-card {
  padding: 30px;
}
.card-heading,
.result-heading {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}
.card-heading p {
  margin: 0 0 7px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.1em;
}
.card-heading h2,
.rule-card h2,
.result-card h2 {
  font-size: 26px;
}
.card-heading > span {
  padding: 8px 12px;
  border-radius: 999px;
  background: #fff0b8;
  color: #765711;
  font-size: 12px;
  font-weight: 850;
  white-space: nowrap;
}
.field {
  display: grid;
  gap: 8px;
  margin-top: 23px;
  color: #594828;
  font-weight: 850;
}
.field select,
.field input:not([type='file']) {
  width: 100%;
  height: 48px;
  padding: 0 15px;
  border: 1px solid #eadfca;
  border-radius: 14px;
  background: #fffdf7;
  color: #25231f;
  font: inherit;
}
.file-drop {
  display: grid;
  min-height: 132px;
  place-items: center;
  align-content: center;
  gap: 8px;
  padding: 20px;
  border: 1px dashed #d2b66a;
  border-radius: 20px;
  background: #fffdf7;
  color: #765711;
  cursor: pointer;
  text-align: center;
}
.file-drop input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}
.file-drop b {
  display: inline-flex;
  min-height: 40px;
  align-items: center;
  padding: 0 18px;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
}
.file-drop small,
.limits {
  color: #8a7857;
  font-size: 13px;
  line-height: 1.55;
}
.file-summary {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  margin-top: 18px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #fff0b8;
}
.file-summary strong,
.file-summary span {
  display: block;
}
.file-summary strong {
  color: #4f401f;
  font-size: 14px;
}
.file-summary span {
  margin-top: 3px;
  color: #7b6430;
  font-size: 12px;
}
.text-button,
.file-list button {
  border: 0;
  background: transparent;
  color: #9a7512;
  font: inherit;
  font-size: 13px;
  font-weight: 850;
  cursor: pointer;
}
.file-list,
.result-list,
.rule-card ul {
  padding: 0;
  list-style: none;
}
.file-list {
  display: grid;
  max-height: 218px;
  gap: 8px;
  overflow: auto;
  margin: 12px 0 0;
}
.file-list li {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 13px;
  background: #fffdf7;
}
.file-list span {
  overflow: hidden;
  color: #594828;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-list small {
  color: #8a7857;
  font-size: 12px;
}
.limits {
  margin: 18px 0 0;
}
.primary-button {
  width: 100%;
  min-height: 50px;
  margin-top: 23px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font: inherit;
  font-weight: 900;
  cursor: pointer;
}
.primary-button:disabled,
.text-button:disabled,
.file-list button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.rule-card {
  padding: 30px;
}
.rule-card ul {
  display: grid;
  gap: 15px;
  margin: 22px 0 0;
}
.rule-card li {
  position: relative;
  padding-left: 20px;
  color: #705c37;
  font-size: 14px;
  line-height: 1.7;
}
.rule-card li::before {
  position: absolute;
  left: 0;
  content: '•';
  color: #e0ad20;
  font-weight: 900;
}
.message {
  margin: 22px 0 0;
  font-weight: 800;
}
.error-message {
  color: #b84444;
}
.result-card {
  margin-top: 26px;
  padding: 30px;
}
.haki-badge {
  padding: 10px 14px;
  border-radius: 999px;
  background: #dff3dd;
  color: #397448;
  font-size: 13px;
  font-weight: 900;
}
.result-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-top: 24px;
}
.result-stats article {
  padding: 18px;
  border-radius: 18px;
  background: #fffdf7;
}
.result-stats span {
  display: block;
  color: #8a7857;
  font-size: 13px;
  font-weight: 750;
}
.result-stats strong {
  display: block;
  margin-top: 8px;
  color: #25231f;
  font-size: 28px;
}
.result-stats .success {
  background: #dff3dd;
}
.result-stats .duplicate {
  background: #fff0b8;
}
.result-stats .invalid {
  background: #ffe1e8;
}
.result-list {
  display: grid;
  max-height: 440px;
  gap: 9px;
  overflow: auto;
  margin: 24px 0 0;
}
.result-list li {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  padding: 12px 14px;
  border-radius: 16px;
  background: #fffdf7;
}
.result-list li.imported {
  background: #f2faef;
}
.result-list li.duplicate {
  background: #fff9e5;
}
.result-list li.invalid {
  background: #fff1f3;
}
.result-mark {
  display: grid;
  width: 25px;
  height: 25px;
  place-items: center;
  border-radius: 50%;
  background: #dff3dd;
  color: #397448;
  font-weight: 900;
}
.duplicate .result-mark {
  background: #fff0b8;
  color: #806210;
}
.invalid .result-mark {
  background: #ffdce4;
  color: #a13c55;
}
.result-list strong,
.result-list small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.result-list strong {
  color: #4e4129;
  font-size: 14px;
}
.result-list small {
  margin-top: 3px;
  color: #857454;
  font-size: 12px;
}
.result-list em {
  color: #7b6430;
  font-size: 12px;
  font-style: normal;
  font-weight: 850;
}
@media (max-width: 860px) {
  .batch-layout {
    grid-template-columns: 1fr;
  }
  .result-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 620px) {
  .batch-page {
    width: min(100% - 32px, 1160px);
    padding-top: 30px;
  }
  .page-heading {
    display: grid;
  }
  .upload-card,
  .rule-card,
  .result-card {
    padding: 22px;
  }
  .file-summary {
    align-items: flex-start;
  }
  .result-stats {
    grid-template-columns: 1fr 1fr;
  }
  .file-list li {
    grid-template-columns: minmax(0, 1fr) auto;
  }
  .file-list button {
    grid-column: 1 / -1;
    justify-self: start;
  }
}
</style>
