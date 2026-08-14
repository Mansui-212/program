<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getFeaturedCharacters } from '@/api/modules/characters'
import { getMemes } from '@/api/modules/memes'
import MemePreviewModal from '@/components/MemePreviewModal.vue'

import type { Character } from '@/types/character'
import type { Meme } from '@/types/meme'

const characters = ref<Character[]>([])
const memes = ref<Meme[]>([])

const loading = ref(true)
const selectedCharacterSlug = ref('')
const selectedOrder = ref<'latest' | 'featured' | 'popular'>('latest')
const keyword = ref('')
const selectedMeme = ref<Meme | null>(null)

async function loadCharacters() {
  const response = await getFeaturedCharacters()
  characters.value = response.data
}

async function loadMemes() {
  loading.value = true

  try {
    const response = await getMemes({
      limit: 50,
      character_slug: selectedCharacterSlug.value || undefined,
      keyword: keyword.value || undefined,
      order: selectedOrder.value,
    })

    memes.value = response.data
  } catch (error) {
    console.error('加载表情包失败', error)
  } finally {
    loading.value = false
  }
}

function selectCharacter(slug: string) {
  selectedCharacterSlug.value = slug
  loadMemes()
}

function changeOrder(order: 'latest' | 'featured' | 'popular') {
  selectedOrder.value = order
  loadMemes()
}

function searchMemes() {
  loadMemes()
}

function openMeme(meme: Meme) {
  selectedMeme.value = meme
}

function closeMeme() {
  selectedMeme.value = null
}

onMounted(async () => {
  await loadCharacters()
  await loadMemes()
})
</script>

<template>
  <main class="memes-page">
    <section class="memes-hero">
      <p class="section-kicker">MEME ARCHIVE</p>
      <h1>表情包档案</h1>
      <p>收录圆头耄耋、鼠鼠、Doro、曼波等哈基米相关表情包。</p>
    </section>

    <section class="memes-toolbar">
      <div class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索表情包名称，例如：圆头、鼠鼠、曼波"
          @keyup.enter="searchMemes"
        />

        <button type="button" @click="searchMemes">搜索</button>
      </div>

      <div class="filter-row">
        <button
          type="button"
          :class="{ active: selectedCharacterSlug === '' }"
          @click="selectCharacter('')"
        >
          全部
        </button>

        <button
          v-for="character in characters"
          :key="character.id"
          type="button"
          :class="{ active: selectedCharacterSlug === character.slug }"
          @click="selectCharacter(character.slug)"
        >
          {{ character.name }}
        </button>
      </div>

      <div class="filter-row">
        <button
          type="button"
          :class="{ active: selectedOrder === 'latest' }"
          @click="changeOrder('latest')"
        >
          最新
        </button>

        <button
          type="button"
          :class="{ active: selectedOrder === 'featured' }"
          @click="changeOrder('featured')"
        >
          推荐
        </button>

        <button
          type="button"
          :class="{ active: selectedOrder === 'popular' }"
          @click="changeOrder('popular')"
        >
          热度
        </button>
      </div>
    </section>

    <section class="memes-content">
      <p v-if="loading" class="loading-text">正在加载哈基米表情包...</p>

      <p v-else-if="memes.length === 0" class="empty-text">暂时没有找到对应表情包。</p>

      <div v-else class="meme-grid">
        <article v-for="meme in memes" :key="meme.id" class="meme-card" @click="openMeme(meme)">
          <img :src="meme.image_url" :alt="meme.title" />

          <div class="meme-card-body">
            <h3>{{ meme.title }}</h3>

            <p v-if="meme.description">{{ meme.description }}</p>

            <div class="meme-meta">
              <span>{{ meme.source_name || '未知来源' }}</span>
              <span>浏览 {{ meme.view_count }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <MemePreviewModal :meme="selectedMeme" @close="closeMeme" />
  </main>
</template>

<style scoped>
.memes-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 24px 120px;
}

.memes-hero {
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

.memes-hero h1 {
  margin: 0;
  color: #25231f;
  font-size: 64px;
  line-height: 1;
}

.memes-hero p {
  margin: 24px 0 0;
  color: #6f6047;
  font-size: 18px;
}

.memes-toolbar {
  margin-top: 36px;
  padding: 28px;
  border-radius: 32px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.search-box {
  display: flex;
  gap: 12px;
}

.search-box input {
  flex: 1;
  height: 48px;
  padding: 0 18px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #25231f;
  font-size: 15px;
}

.search-box button,
.filter-row button {
  height: 48px;
  padding: 0 22px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #594828;
  font-weight: 700;
  cursor: pointer;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 18px;
}

.search-box button:hover,
.filter-row button:hover,
.filter-row button.active {
  border-color: #f6c534;
  background: #f6c534;
  color: #25231f;
}

.memes-content {
  margin-top: 40px;
}

.loading-text,
.empty-text {
  color: #7b6a4a;
  font-size: 18px;
}

.meme-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 24px;
}

.meme-card {
  overflow: hidden;
  border-radius: 28px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.meme-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.12);
}

.meme-card img {
  display: block;
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  background: #f4ead7;
}

.meme-card-body {
  padding: 18px 20px 20px;
}

.meme-card-body h3 {
  margin: 0;
  color: #25231f;
  font-size: 18px;
}

.meme-card-body p {
  margin: 8px 0 0;
  color: #7b6a4a;
  font-size: 14px;
  line-height: 1.6;
}

.meme-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 16px;
  color: #a58a55;
  font-size: 13px;
  font-weight: 700;
}

@media (max-width: 1000px) {
  .meme-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .memes-page {
    padding: 48px 16px 80px;
  }

  .memes-hero {
    padding: 48px 32px;
  }

  .memes-hero h1 {
    font-size: 44px;
  }

  .search-box {
    flex-direction: column;
  }

  .meme-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .meme-grid {
    grid-template-columns: 1fr;
  }
}
</style>
