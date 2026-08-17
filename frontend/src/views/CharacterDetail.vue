<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import CharacterHero from '@/components/character/CharacterHero.vue'
import RelatedMemes from '@/components/character/RelatedMemes.vue'
import RelatedMusic from '@/components/character/RelatedMusic.vue'
import Timeline from '@/components/character/Timeline.vue'
import {
  getCharacterDetail,
  getCharacterMemes,
  getCharacterMusic,
} from '@/api/modules/characters'
import type { CharacterDetail } from '@/types/character'
import type { Meme } from '@/types/meme'
import type { MusicTrack } from '@/types/musicTrack'

const route = useRoute()
const character = ref<CharacterDetail | null>(null)
const memes = ref<Meme[]>([])
const musicTracks = ref<MusicTrack[]>([])
const loading = ref(true)
const error = ref('')

async function loadCharacter(slug: string) {
  loading.value = true
  error.value = ''
  character.value = null
  memes.value = []
  musicTracks.value = []

  try {
    const detailResponse = await getCharacterDetail(slug)
    character.value = detailResponse.data

    const [memesResponse, musicResponse] = await Promise.all([
      getCharacterMemes(character.value.id),
      getCharacterMusic(character.value.id),
    ])

    memes.value = memesResponse.data
    musicTracks.value = musicResponse.data
  } catch (reason) {
    console.error('加载角色详情失败', reason)
    error.value = '角色档案暂时无法加载，请稍后再试。'
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.slug,
  (value) => {
    const slug = Array.isArray(value) ? value[0] : value

    if (slug) {
      void loadCharacter(slug)
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="character-detail-page">
    <p v-if="loading" class="state-card">正在打开角色档案...</p>

    <section v-else-if="error" class="state-card error-card">
      <h1>档案未找到</h1>
      <p>{{ error }}</p>
      <RouterLink to="/">返回角色档案</RouterLink>
    </section>

    <template v-else-if="character">
      <CharacterHero :character="character" />

      <section class="origin-section">
        <div class="origin-card">
          <p>ORIGIN STORY</p>
          <h2>起源故事</h2>
          <div class="origin-content">
            <span>✦</span>
            <p>{{ character.origin_story || '这位角色的起源故事正在整理中。' }}</p>
          </div>
        </div>

        <aside class="archive-note">
          <p>ARCHIVE NOTE</p>
          <strong>基米小站角色百科</strong>
          <span>所有时间线为小站整理记录，会随新素材持续补充。</span>
        </aside>
      </section>

      <Timeline :events="character.timeline || []" />
      <RelatedMemes :memes="memes" />
      <RelatedMusic :tracks="musicTracks" />
    </template>
  </div>
</template>

<style scoped>
.character-detail-page { width: min(1180px, calc(100% - 48px)); margin: 0 auto; padding: 54px 0 110px; }
.state-card { margin: 70px 0; border: 1px dashed #dfceb0; border-radius: 30px; padding: 52px; background: #fffaf0; color: #756247; font-size: 17px; text-align: center; }
.error-card h1 { margin: 0; color: #342e26; font-size: 32px; font-weight: 900; }
.error-card p { margin: 12px 0 22px; }
.error-card a { color: #8c691b; font-weight: 900; text-decoration: none; }
.origin-section { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 24px; margin-top: 34px; }
.origin-card, .archive-note { border: 1px solid #f0e2ca; border-radius: 30px; padding: 31px 34px; background: #fffaf0; box-shadow: 0 14px 30px rgba(76, 58, 28, 0.05); }
.origin-card > p, .archive-note > p { margin: 0 0 11px; color: #b88a12; font-size: 12px; font-weight: 900; letter-spacing: 0.13em; }
.origin-card h2 { margin: 0; color: #2f2c27; font-size: 29px; font-weight: 900; letter-spacing: -0.05em; }
.origin-content { display: grid; grid-template-columns: 34px minmax(0, 1fr); gap: 12px; margin-top: 19px; color: #71614b; line-height: 1.85; }
.origin-content span { display: grid; width: 30px; height: 30px; place-items: center; border-radius: 10px; background: #fff0b2; color: #896414; font-size: 13px; }
.origin-content p { margin: 0; font-size: 15px; }
.archive-note { display: grid; align-content: start; background: linear-gradient(145deg, #fff0b8, #ffe9ed); }
.archive-note strong { color: #4c3d29; font-size: 19px; font-weight: 900; line-height: 1.25; }
.archive-note span { margin-top: 13px; color: #756044; font-size: 13px; font-weight: 700; line-height: 1.7; }
@media (max-width: 760px) { .character-detail-page { width: calc(100% - 32px); padding-top: 35px; } .origin-section { grid-template-columns: 1fr; } .origin-card, .archive-note { border-radius: 25px; padding: 27px; } }
</style>
