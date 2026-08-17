<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import TurntablePlayer from '@/components/TurntablePlayer.vue'
import { getFeaturedCharacters } from '@/api/modules/characters'
import { getMusicTracks } from '@/api/modules/musicTracks'

import type { Character } from '@/types/character'
import type { MusicTrack } from '@/types/musicTrack'

const characters = ref<Character[]>([])
const tracks = ref<MusicTrack[]>([])
const route = useRoute()
const loading = ref(true)

const selectedCharacterSlug = ref('')
const selectedOrder = ref<'latest' | 'featured' | 'popular'>('featured')
const keyword = ref('')

const currentTrack = ref<MusicTrack | null>(null)
const isPlaying = ref(false)

async function loadCharacters() {
  const response = await getFeaturedCharacters()
  characters.value = response.data
}

async function loadTracks() {
  loading.value = true

  try {
    const response = await getMusicTracks({
      limit: 50,
      character_slug: selectedCharacterSlug.value || undefined,
      keyword: keyword.value || undefined,
      order: selectedOrder.value,
    })

    tracks.value = response.data

    const currentTrackIsVisible = tracks.value.some(
      (track) => track.id === currentTrack.value?.id,
    )

    if ((!currentTrack.value || !currentTrackIsVisible) && tracks.value.length > 0) {
      const requestedSlug = typeof route.query.track === 'string' ? route.query.track : ''
      currentTrack.value = tracks.value.find((track) => track.slug === requestedSlug) || tracks.value[0] || null
      isPlaying.value = false
    }

    if (tracks.value.length === 0) {
      currentTrack.value = null
      isPlaying.value = false
    }
  } catch (error) {
    console.error('加载音乐失败', error)
    tracks.value = []
  } finally {
    loading.value = false
  }
}

async function selectTrack(track: MusicTrack) {
  const isSameTrack = currentTrack.value?.id === track.id

  currentTrack.value = track

  if (isSameTrack) {
    isPlaying.value = !isPlaying.value
    return
  }

  isPlaying.value = false
  await nextTick()
  isPlaying.value = true
}

function selectCharacter(slug: string) {
  selectedCharacterSlug.value = slug
  loadTracks()
}

function changeOrder(order: 'latest' | 'featured' | 'popular') {
  selectedOrder.value = order
  loadTracks()
}

function searchTracks() {
  loadTracks()
}

function handlePlayingChange(value: boolean) {
  isPlaying.value = value
}

async function playNextTrack() {
  if (tracks.value.length === 0) return

  if (!currentTrack.value) {
    currentTrack.value = tracks.value[0] ?? null
    isPlaying.value = false
    await nextTick()
    isPlaying.value = true
    return
  }

  const currentIndex = tracks.value.findIndex(
    (track) => track.id === currentTrack.value?.id,
  )
  const nextIndex = currentIndex === -1 ? 0 : (currentIndex + 1) % tracks.value.length

  currentTrack.value = tracks.value[nextIndex] ?? null
  isPlaying.value = false
  await nextTick()
  isPlaying.value = true
}

async function playPrevTrack() {
  if (tracks.value.length === 0) return

  if (!currentTrack.value) {
    currentTrack.value = tracks.value[0] ?? null
    isPlaying.value = false
    await nextTick()
    isPlaying.value = true
    return
  }

  const currentIndex = tracks.value.findIndex(
    (track) => track.id === currentTrack.value?.id,
  )
  const prevIndex = currentIndex === -1 ? 0 : (currentIndex - 1 + tracks.value.length) % tracks.value.length

  currentTrack.value = tracks.value[prevIndex] ?? null
  isPlaying.value = false
  await nextTick()
  isPlaying.value = true
}

onMounted(async () => {
  await loadCharacters()
  await loadTracks()
})
</script>

<template>
  <main class="music-page">
    <section class="music-hero">
      <p class="section-kicker">HAKIMI MUSIC</p>
      <h1>哈基米音乐档案</h1>
      <p>用唱片机的方式播放你的哈基米改编音乐、曼波神曲与抽象音频收藏。</p>
    </section>

    <section class="music-toolbar">
      <div class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索歌曲名，例如：曼波、圆头、鼠鼠"
          @keyup.enter="searchTracks"
        />

        <button type="button" @click="searchTracks">搜索</button>
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
          :class="{ active: selectedOrder === 'featured' }"
          @click="changeOrder('featured')"
        >
          推荐
        </button>

        <button
          type="button"
          :class="{ active: selectedOrder === 'latest' }"
          @click="changeOrder('latest')"
        >
          最新
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

    <section class="music-layout">
      <TurntablePlayer
        :track="currentTrack"
        :is-playing="isPlaying"
        @update:playing="handlePlayingChange"
        @next="playNextTrack"
        @prev="playPrevTrack"
      />

      <section class="playlist-panel">
        <p v-if="loading" class="loading-text">正在加载哈基米音乐...</p>

        <p v-else-if="tracks.length === 0" class="empty-text">暂时没有找到对应音乐。</p>

        <div v-else class="playlist">
          <article
            v-for="track in tracks"
            :key="track.id"
            class="track-card"
            :class="{ active: currentTrack?.id === track.id }"
            role="button"
            tabindex="0"
            @click="selectTrack(track)"
            @keydown.enter="selectTrack(track)"
            @keydown.space.prevent="selectTrack(track)"
          >
            <div class="track-cover">
              <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" />
              <span v-else>♪</span>
            </div>

            <div class="track-info">
              <h3>
                {{ track.title }}
                <span v-if="currentTrack?.id === track.id && isPlaying" class="playing-badge">
                  播放中
                </span>
              </h3>
              <p>{{ track.author_name || '未知作者' }}</p>
              <div class="track-meta">
                <span>{{ track.source_name || '未知来源' }}</span>
                <span>播放 {{ track.play_count }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.music-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 80px 24px 120px;
}

.music-hero {
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

.music-hero h1 {
  margin: 0;
  color: #25231f;
  font-size: 64px;
  line-height: 1;
}

.music-hero p {
  margin: 24px 0 0;
  color: #6f6047;
  font-size: 18px;
}

.music-toolbar {
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

.music-layout {
  display: grid;
  grid-template-columns: minmax(340px, 460px) minmax(0, 1fr);
  align-items: start;
  gap: 28px;
  margin-top: 40px;
}

.playlist-panel {
  padding: 24px;
  border-radius: 32px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.playlist {
  display: grid;
  gap: 16px;
}

.track-card {
  display: grid;
  grid-template-columns: 88px minmax(0, 1fr);
  gap: 16px;
  padding: 14px;
  border: 1px solid #efe3cf;
  border-radius: 24px;
  background: #fffdf7;
  cursor: pointer;
  outline: none;
  transition: 0.2s ease;
}

.track-card:hover,
.track-card:focus-visible,
.track-card.active {
  border-color: #f6c534;
  background: #fff8da;
  box-shadow: 0 10px 30px rgba(246, 197, 52, 0.16);
}

.track-cover {
  display: grid;
  width: 88px;
  height: 88px;
  place-items: center;
  overflow: hidden;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff6cf, #ffe3ec);
  color: #25231f;
  font-size: 32px;
  font-weight: 900;
}

.track-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.track-info h3 {
  margin: 0;
  color: #25231f;
  font-size: 18px;
}

.playing-badge {
  display: inline-flex;
  align-items: center;
  height: 22px;
  margin-left: 8px;
  padding: 0 8px;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-size: 12px;
  font-weight: 900;
  vertical-align: middle;
}

.track-info p {
  margin: 6px 0 0;
  color: #7b6a4a;
  font-size: 14px;
}

.track-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
  color: #a58a55;
  font-size: 13px;
  font-weight: 700;
}

.loading-text,
.empty-text {
  color: #7b6a4a;
  font-size: 18px;
}

@media (max-width: 980px) {
  .music-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .music-page {
    padding: 48px 16px 80px;
  }

  .music-hero {
    padding: 48px 32px;
  }

  .music-hero h1 {
    font-size: 44px;
  }

  .search-box {
    flex-direction: column;
  }
}
</style>
