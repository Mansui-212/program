<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import SearchBox from '@/components/search/SearchBox.vue'
import UserLink from '@/components/common/UserLink.vue'
import { getFeaturedCharacters } from '@/api/modules/characters'
import { getLatestMemes } from '@/api/modules/memes'
import { getLatestMusicTracks } from '@/api/modules/musicTracks'
import type { Character } from '@/types/character'
import type { Meme } from '@/types/meme'
import type { MusicTrack } from '@/types/musicTrack'

const characters = ref<Character[]>([])
const charactersLoading = ref(true)
const charactersError = ref(false)
const latestMemes = ref<Meme[]>([])
const memesLoading = ref(true)
const memesError = ref(false)
const latestMusicTracks = ref<MusicTrack[]>([])
const musicLoading = ref(true)
const musicError = ref(false)
const homeSearchKeyword = ref('')
const router = useRouter()

const heroSlides = [
  { src: '/images/hero/hakimi1.jpg', position: 'center 42%' },
  { src: '/images/hero/hakimi2.jpg', position: 'center 38%' },
  { src: '/images/hero/hakimi3.jpg', position: 'center 45%' },
  { src: '/images/hero/hakimi4.jpg', position: 'center 38%' },
  { src: '/images/hero/hakimi5.jpg', position: 'center center' },
  { src: '/images/hero/hakimi6.jpg', position: 'center 42%' },
]

const currentHero = ref(0)
let heroTimer: ReturnType<typeof setInterval> | undefined

function nextHero() {
  currentHero.value = (currentHero.value + 1) % heroSlides.length
}

function prevHero() {
  currentHero.value = (currentHero.value - 1 + heroSlides.length) % heroSlides.length
}

function startHeroAutoplay() {
  if (heroTimer) {
    clearInterval(heroTimer)
  }

  heroTimer = setInterval(nextHero, 5000)
}

function showNextHero() {
  nextHero()
  startHeroAutoplay()
}

function showPrevHero() {
  prevHero()
  startHeroAutoplay()
}

function goHero(index: number) {
  currentHero.value = index
  startHeroAutoplay()
}

async function submitHomeSearch() {
  const keyword = homeSearchKeyword.value.trim()

  await router.push({
    name: 'search',
    query: keyword ? { q: keyword } : undefined,
  })
}

function searchPopular(keyword: string) {
  homeSearchKeyword.value = keyword
  void submitHomeSearch()
}

async function loadCharacters() {
  try {
    const response = await getFeaturedCharacters()
    characters.value = response.data
  } catch (error) {
    console.error(error)
    charactersError.value = true
  } finally {
    charactersLoading.value = false
  }
}

async function loadLatestMemes() {
  try {
    const response = await getLatestMemes(8)
    latestMemes.value = response.data
  } catch (error) {
    console.error('加载最新表情包失败', error)
    memesError.value = true
  } finally {
    memesLoading.value = false
  }
}

async function loadLatestMusicTracks() {
  try {
    const response = await getLatestMusicTracks(4)
    latestMusicTracks.value = response.data
  } catch (error) {
    console.error('加载音乐推荐失败', error)
    musicError.value = true
  } finally {
    musicLoading.value = false
  }
}

onMounted(() => {
  void loadCharacters()
  void loadLatestMemes()
  void loadLatestMusicTracks()
  startHeroAutoplay()
})

onUnmounted(() => {
  if (heroTimer) {
    clearInterval(heroTimer)
  }
})
</script>

<template>
  <div id="top">
      <section class="hero section-wrap" aria-labelledby="hero-title">
        <div class="hero-slides" aria-hidden="true">
          <div
            v-for="(slide, index) in heroSlides"
            :key="slide.src"
            class="hero-slide"
            :class="{ active: index === currentHero }"
            :style="{
              backgroundImage: `url(${slide.src})`,
              backgroundPosition: slide.position,
            }"
          ></div>
        </div>
        <div class="hero-mask" aria-hidden="true"></div>

        <div class="hero-copy">
          <p class="eyebrow">HAKIMI LITTLE STATION</p>
          <h1 id="hero-title">基米小站</h1>
          <p class="hero-slogan">正经做收录，抽象做内容</p>
          <p class="hero-description">
            给每个令人会心一笑的瞬间，留一盏温柔又明亮的小灯。
          </p>
          <div class="hero-search">
            <SearchBox v-model="homeSearchKeyword" @search="submitHomeSearch" />
            <div class="hero-popular-searches">
              <span>热门：</span>
              <button type="button" @click="searchPopular('耄耋')">耄耋</button>
              <button type="button" @click="searchPopular('鼠鼠')">鼠鼠</button>
              <button type="button" @click="searchPopular('doro')">doro</button>
              <button type="button" @click="searchPopular('曼波')">曼波</button>
            </div>
          </div>
          <div class="hero-actions">
            <RouterLink class="button button-primary" to="/characters">探索角色 <span>→</span></RouterLink>
            <RouterLink class="button button-secondary" to="/memes">随机来一张 <span>↗</span></RouterLink>
          </div>
        </div>

        <button
          type="button"
          class="hero-control hero-prev"
          aria-label="上一张首页图片"
          @click="showPrevHero"
        >
          ‹
        </button>
        <button
          type="button"
          class="hero-control hero-next"
          aria-label="下一张首页图片"
          @click="showNextHero"
        >
          ›
        </button>

        <div class="hero-dots" aria-label="首页图片切换">
          <button
            v-for="(_, index) in heroSlides"
            :key="index"
            type="button"
            :class="{ active: index === currentHero }"
            :aria-label="`切换到第 ${index + 1} 张首页图片`"
            :aria-current="index === currentHero ? 'true' : undefined"
            @click="goHero(index)"
          ></button>
        </div>
      </section>

      <section id="characters" class="section-wrap content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">CHARACTER ARCHIVE</p>
            <h2>首批角色</h2>
          </div>
         <RouterLink
  class="section-link"
  to="/characters"
>
  查看全部角色 <span>→</span>
</RouterLink>
        </div>

        <div class="character-grid">
          <p v-if="charactersLoading" class="collection-message">正在加载角色档案...</p>
          <p v-else-if="charactersError" class="collection-message">角色档案暂时无法加载。</p>
          <article v-for="character in characters" v-else :key="character.id" class="character-card">
            <div class="character-portrait" :style="{ backgroundColor: character.theme_color || '#f6f0e2' }">
              <img v-if="character.avatar_url" class="avatar-image" :src="character.avatar_url" :alt="`${character.name}档案馆头像`" />
            </div>
            <div class="card-content">
              <h3>{{ character.name }}</h3>
              <p>{{ character.description || character.aliases || '角色档案正在整理中。' }}</p>
              <RouterLink
                class="archive-button"
                :to="{ name: 'character-detail', params: { slug: character.slug } }"
              >
                进入档案 <span>→</span>
              </RouterLink>
            </div>
          </article>
        </div>
      </section>

      <section id="memes" class="section-wrap content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">MEME CORNER</p>
            <h2>最新表情包</h2>
          </div>
          <RouterLink class="section-link" to="/memes">去表情包馆 <span>→</span></RouterLink>
        </div>

        <div class="meme-grid">
          <p v-if="memesLoading" class="collection-message">正在加载最新表情包...</p>
          <p v-else-if="memesError" class="collection-message">表情包暂时无法加载。</p>
          <article v-for="meme in latestMemes" v-else :key="meme.id" class="meme-card">
            <div class="meme-preview">
              <img class="meme-image" :src="meme.image_url" :alt="meme.title" />
            </div>
            <div class="meme-info">
              <span class="tag">{{ meme.source_name || '最新收录' }}</span>
              <h3>{{ meme.title }}</h3>
              <p v-if="meme.description">{{ meme.description }}</p>
              <div class="meme-actions">
                <span>{{ meme.file_type === 'gif' ? 'GIF 动图' : '图片' }}</span>
                <span v-if="meme.author_name">
                  收录：<UserLink :uid="meme.author_uid" :name="meme.author_name" />
                </span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section id="music" class="section-wrap content-section">
        <div class="section-heading">
          <div>
          <p class="eyebrow">LATEST HAKIMI MUSIC</p>
          <h2>最新哈基米音乐</h2>
          </div>
          <RouterLink class="section-link" to="/music">查看全部音乐 <span>→</span></RouterLink>
        </div>

        <div class="music-grid">
          <p v-if="musicLoading" class="collection-message">正在加载哈基米音乐...</p>
          <p v-else-if="musicError" class="collection-message">最新音乐暂时无法加载。</p>
          <article v-for="track in latestMusicTracks" v-else :key="track.id" class="music-card">
            <div class="music-cover">
              <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" />
              <span v-else>♪</span>
            </div>

            <div class="music-info">
              <h3>{{ track.title }}</h3>
              <p>{{ track.description || '这首哈基米音乐正在整理资料。' }}</p>
              <div class="music-meta">
                <span>制作：<UserLink :uid="track.author_uid" :name="track.author_name" /></span>
                <span>播放 {{ track.play_count }}</span>
              </div>
              <audio class="music-audio" :src="track.audio_url" controls preload="metadata" />
            </div>
          </article>
        </div>
      </section>

      <section id="chronicle" class="section-wrap content-section">
        <div class="chronicle-card">
          <div class="chronicle-copy">
            <p class="eyebrow">HAKIMI CHRONICLE</p>
            <h2>编年史</h2>
            <p>把流传过的梗、声音和画面，串成一条正在延伸的文化时间线。</p>
            <RouterLink class="button button-dark timeline-button" to="/chronicle">
              进入时间线 <span>→</span>
            </RouterLink>
          </div>
          <div class="timeline" aria-hidden="true">
            <span class="timeline-line"></span>
            <span class="timeline-dot dot-one"></span>
            <span class="timeline-dot dot-two"></span>
            <span class="timeline-dot dot-three"></span>
            <span class="timeline-label label-one">起点</span>
            <span class="timeline-label label-two">名场面</span>
            <span class="timeline-label label-three">今天</span>
          </div>
        </div>
      </section>

      <section id="contribute" class="section-wrap contribute-section">
        <div class="contribute-card">
          <div>
            <p class="eyebrow">CONTRIBUTE TO THE STATION</p>
            <h2>投稿与哈气值</h2>
            <p>上传作品，增加你的哈气值。好内容值得被更多人看见。</p>
          </div>
          <RouterLink to="/submit" class="button button-primary">我要投稿 <span>↗</span></RouterLink>
        </div>
      </section>
  </div>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(html) {
  scroll-behavior: smooth;
}

:global(body) {
  min-width: 320px;
  margin: 0;
  background: #fffdf7;
  color: #292723;
}

:global(button),
:global(a) {
  font: inherit;
}

:global(button) {
  cursor: pointer;
}

:global(#app) {
  display: block;
  width: 100%;
  max-width: none;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  font-weight: 400;
}

.site-shell {
  overflow: hidden;
  background:
    radial-gradient(circle at 10% 8%, rgba(255, 224, 105, 0.2), transparent 20rem),
    #fffdf7;
}

.topbar,
.section-wrap,
.footer {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
}

.topbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 32px;
  min-height: 82px;
}

.brand,
.main-nav a,
.text-action,
.section-link,
.button {
  text-decoration: none;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: #292723;
  font-size: 19px;
  font-weight: 800;
  letter-spacing: -0.04em;
  white-space: nowrap;
}

.brand-mark {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 12px;
  background: #ffd84d;
  box-shadow: 0 5px 0 #f2bd35;
  color: #4d3c14;
  font-size: 17px;
}

.main-nav {
  display: flex;
  justify-content: center;
  gap: clamp(16px, 3vw, 36px);
}

.main-nav a,
.text-action {
  color: #68645b;
  font-size: 14px;
  font-weight: 650;
  transition: color 0.2s ease;
}

.mobile-login {
  display: none;
}

.main-nav a:hover,
.text-action:hover,
.section-link:hover {
  color: #c38a12;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 18px;
  justify-self: end;
}

.user-entry {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-profile-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 13px 6px 6px;
  border-radius: 999px;
  background: #fff4ca;
  color: #594828;
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
  white-space: nowrap;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border: 2px solid #f6c534;
  border-radius: 50%;
  background: #fffdf7;
  object-fit: cover;
}

.user-entry a,
.user-entry button {
  border: 1px solid #e8dfc9;
  border-radius: 10px;
  padding: 9px 16px;
  background: #fffdf7;
  color: #403d36;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.hero {
  position: relative;
  min-height: 490px;
  margin-top: 14px;
  padding: 58px clamp(28px, 6vw, 72px);
  border: 1px solid #f0e4ca;
  border-radius: 34px;
  overflow: hidden;
}

.hero-slides,
.hero-mask {
  position: absolute;
  inset: 0;
}

.hero-slide {
  position: absolute;
  inset: 0;
  background-repeat: no-repeat;
  background-size: cover;
  opacity: 0;
  transform: scale(1.03);
  transition: opacity 0.7s ease, transform 5s ease;
}

.hero-slide.active {
  opacity: 1;
  transform: scale(1);
}

.hero-mask {
  background:
    linear-gradient(90deg, rgba(255, 250, 237, 0.96) 0%, rgba(255, 250, 237, 0.86) 40%, rgba(255, 250, 237, 0.26) 100%),
    linear-gradient(0deg, rgba(70, 53, 30, 0.14), transparent 42%);
}

.hero-copy {
  position: relative;
  z-index: 1;
  min-width: 0;
  max-width: 560px;
}

.eyebrow {
  margin: 0 0 12px;
  color: #ba8a1c;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.13em;
}

.hero h1,
.section-heading h2,
.chronicle-copy h2,
.contribute-card h2 {
  margin: 0;
  color: #292723;
  font-weight: 850;
  letter-spacing: -0.07em;
}

.hero h1 {
  font-size: clamp(54px, 7vw, 88px);
  line-height: 0.98;
}

.hero-slogan {
  margin: 22px 0 0;
  color: #3d3931;
  font-size: clamp(20px, 2.2vw, 27px);
  font-weight: 750;
  letter-spacing: -0.05em;
}

.hero-description {
  max-width: 390px;
  margin: 15px 0 0;
  color: #6f695e;
  font-size: 15px;
  line-height: 1.8;
  overflow-wrap: anywhere;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 30px;
}

.hero-search {
  max-width: 490px;
  margin-top: 22px;
}

.hero-search :deep(.search-box) {
  box-shadow: 0 12px 26px rgba(76, 58, 29, 0.08);
}

.hero-popular-searches {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 7px;
  margin-top: 10px;
  color: #8d816f;
  font-size: 12px;
  font-weight: 750;
}

.hero-popular-searches button {
  padding: 4px 8px;
  border: 1px solid rgba(215, 169, 79, 0.35);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  color: #66583e;
  font: inherit;
  cursor: pointer;
}

.hero-popular-searches button:hover {
  border-color: #f6c83f;
  background: #fff0b8;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 46px;
  border: 0;
  border-radius: 14px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 800;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.button:hover,
.archive-button:hover,
.play-button:hover {
  transform: translateY(-2px);
}

.button-primary {
  background: #f6c83f;
  box-shadow: 0 8px 0 #e9b42a;
  color: #443719;
}

.button-secondary {
  border: 1px solid rgba(215, 169, 79, 0.35);
  background: rgba(255, 255, 255, 0.72);
  color: #554930;
}

.hero-control {
  position: relative;
  position: absolute;
  z-index: 2;
  top: 50%;
  display: grid;
  width: 46px;
  height: 46px;
  place-items: center;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.72);
  background: rgba(255, 253, 247, 0.78);
  box-shadow: 0 8px 22px rgba(82, 60, 29, 0.16);
  color: #493f2d;
  font-size: 34px;
  line-height: 1;
  backdrop-filter: blur(8px);
  transform: translateY(-50%);
  transition: background 0.2s ease, transform 0.2s ease;
}

.hero-control:hover {
  background: #fffdf7;
  transform: translateY(-50%) scale(1.06);
}

.hero-prev { left: 24px; }
.hero-next { right: 24px; }

.hero-dots {
  position: absolute;
  z-index: 2;
  bottom: 24px;
  left: 50%;
  display: flex;
  gap: 9px;
  transform: translateX(-50%);
}

.hero-dots button {
  width: 10px;
  height: 10px;
  border: 0;
  border-radius: 999px;
  padding: 0;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 1px 4px rgba(65, 46, 20, 0.18);
  transition: width 0.2s ease, background 0.2s ease;
}

.hero-dots button.active {
  width: 28px;
  background: #f6c83f;
}

.content-section {
  padding-top: 108px;
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 28px;
}

.section-heading h2,
.chronicle-copy h2,
.contribute-card h2 {
  font-size: clamp(32px, 4vw, 44px);
  line-height: 1;
}

.section-link {
  color: #836e43;
  font-size: 14px;
  font-weight: 750;
  white-space: nowrap;
}

.section-link span,
.archive-button span {
  margin-left: 4px;
}

.character-grid,
.meme-grid,
.album-grid {
  display: grid;
  gap: 18px;
}

.character-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.character-card,
.meme-card,
.album-card {
  overflow: hidden;
  border: 1px solid #f0eadf;
  border-radius: 24px;
  background: #fffefa;
  box-shadow: 0 10px 26px rgba(70, 59, 37, 0.06);
}

.character-portrait {
  display: grid;
  min-height: 164px;
  place-items: center;
  background: #f6f0e2;
}

.avatar-image {
  width: 100%;
  height: 100%;
  padding: 12px;
  object-fit: contain;
  mix-blend-mode: multiply;
}

.collection-message {
  grid-column: 1 / -1;
  margin: 0;
  border: 1px dashed #dfd4bd;
  border-radius: 20px;
  padding: 28px;
  background: #fffefa;
  color: #857b6a;
  font-size: 14px;
}

.card-content {
  padding: 22px;
}

.card-content h3,
.meme-info h3,
.album-copy h3 {
  margin: 0;
  color: #38342d;
  font-size: 20px;
  letter-spacing: -0.05em;
}

.card-content p {
  min-height: 48px;
  margin: 10px 0 18px;
  color: #787166;
  font-size: 13px;
  line-height: 1.7;
}

.archive-button,
.play-button {
  border: 0;
  padding: 0;
  background: transparent;
  color: #5f543d;
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
  transition: transform 0.2s ease;
}

.maodie {
  --soft: #e7e2ff;
  --light: #f5f2ff;
  --deep: #65579f;
}

.shushu {
  --soft: #dcefd8;
  --light: #f3faeb;
  --deep: #557c4c;
}

.doro {
  --soft: #ffd5dc;
  --light: #fff0ed;
  --deep: #a65c6b;
}

.manbo {
  --soft: #ffe7ac;
  --light: #fff7da;
  --deep: #a26f16;
}

.meme-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.meme-preview {
  background: #f5efdf;
  min-height: 190px;
  overflow: hidden;
}

.meme-image {
  display: block;
  width: 100%;
  min-height: 190px;
  aspect-ratio: 1 / 0.84;
  object-fit: cover;
}

.meme-info {
  padding: 16px 17px;
}

.tag {
  display: inline-block;
  margin-bottom: 8px;
  border-radius: 99px;
  padding: 4px 9px;
  background: #f6f0e4;
  color: #89775d;
  font-size: 11px;
  font-weight: 750;
}

.meme-info h3 {
  font-size: 17px;
}

.meme-info p {
  display: -webkit-box;
  overflow: hidden;
  margin: 8px 0 0;
  color: #787166;
  font-size: 13px;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.meme-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.meme-actions span {
  color: #888076;
  font-size: 11px;
  font-weight: 700;
}

.meme-actions span + span::before {
  margin-right: 8px;
  color: #d5ccbc;
  content: '·';
}

.music-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.music-card {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr);
  gap: 20px;
  padding: 18px;
  border: 1px solid #f0eadf;
  border-radius: 28px;
  background: #fffefa;
  box-shadow: 0 10px 26px rgba(70, 59, 37, 0.06);
}

.music-cover {
  display: grid;
  width: 120px;
  height: 120px;
  place-items: center;
  overflow: hidden;
  border-radius: 24px;
  background: linear-gradient(135deg, #fff6cf, #ffe3ec);
  color: #25231f;
  font-size: 42px;
  font-weight: 900;
}

.music-cover img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.music-info h3 {
  margin: 0;
  color: #38342d;
  font-size: 20px;
}

.music-info p {
  margin: 8px 0 0;
  color: #787166;
  font-size: 13px;
  line-height: 1.6;
}

.music-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 12px;
  color: #a58a55;
  font-size: 12px;
  font-weight: 700;
}

.music-audio {
  width: 100%;
  height: 34px;
  margin-top: 12px;
}

.album-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.album-card {
  display: flex;
  align-items: center;
  gap: 22px;
  min-height: 188px;
  padding: 24px;
}

.record-wrap {
  position: relative;
  flex: 0 0 118px;
  width: 118px;
  height: 118px;
}

.record {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  border: 7px solid rgba(255, 255, 255, 0.75);
  border-radius: 50%;
  background: repeating-radial-gradient(circle, var(--deep) 0 2px, var(--soft) 3px 7px);
  box-shadow: inset 0 0 0 12px rgba(255, 255, 255, 0.18);
}

.record span {
  color: #fffdf7;
  font-size: 28px;
  text-shadow: 0 1px 2px rgba(55, 49, 37, 0.2);
}

.record-hole {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 14px;
  height: 14px;
  border: 3px solid #fffefa;
  border-radius: 50%;
  background: #5a5146;
  transform: translate(-50%, -50%);
}

.album-copy {
  min-width: 0;
}

.album-copy p {
  margin: 0 0 7px;
  color: #958a7a;
  font-size: 12px;
  font-weight: 700;
}

.album-copy h3 {
  font-size: 20px;
}

.play-button {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 18px;
  color: #b17d17;
}

.play-button span {
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border-radius: 50%;
  background: #ffe48e;
  color: #79530d;
  font-size: 8px;
}

.chronicle-card {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(320px, 1.15fr);
  align-items: center;
  gap: 34px;
  overflow: hidden;
  min-height: 325px;
  border-radius: 30px;
  padding: 48px clamp(28px, 5vw, 64px);
  background: #2e332e;
}

.chronicle-copy .eyebrow {
  color: #edcf78;
}

.chronicle-copy h2 {
  color: #fffbed;
}

.chronicle-copy > p:not(.eyebrow) {
  max-width: 370px;
  margin: 17px 0 25px;
  color: #d8d7c9;
  font-size: 14px;
  line-height: 1.8;
}

.button-dark {
  background: #fff3b8;
  color: #4c442c;
  box-shadow: none;
}

.timeline {
  position: relative;
  min-height: 164px;
}

.timeline-line {
  position: absolute;
  top: 82px;
  right: 4%;
  left: 3%;
  height: 2px;
  background: linear-gradient(90deg, #f1d976, #eaa3aa 48%, #acd49b);
}

.timeline-dot {
  position: absolute;
  top: 68px;
  width: 30px;
  height: 30px;
  border: 6px solid #2e332e;
  border-radius: 50%;
}

.dot-one { left: 4%; background: #f1d976; }
.dot-two { left: 46%; background: #eaa3aa; }
.dot-three { right: 4%; background: #acd49b; }

.timeline-label {
  position: absolute;
  color: #f4eedb;
  font-size: 12px;
  font-weight: 700;
}

.label-one { top: 33px; left: 2%; }
.label-two { right: 42%; bottom: 24px; }
.label-three { top: 33px; right: 2%; }

.contribute-section {
  padding-top: 108px;
  padding-bottom: 100px;
}

.contribute-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  border: 1px solid #f2dccc;
  border-radius: 28px;
  padding: 38px clamp(25px, 5vw, 58px);
  background: linear-gradient(110deg, #ffe6dc 0%, #fff5d8 100%);
}

.contribute-card > div > p:not(.eyebrow) {
  margin: 14px 0 0;
  color: #74675f;
  font-size: 14px;
}

.footer {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  border-top: 1px solid #eee6d8;
  padding: 26px 0 38px;
  color: #9a9388;
  font-size: 12px;
}

@media (max-width: 900px) {
  .character-grid,
  .meme-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .album-grid {
    grid-template-columns: 1fr;
  }

  .music-grid {
    grid-template-columns: 1fr;
  }

  .chronicle-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 900px) {
  .topbar,
  .section-wrap,
  .footer {
    width: calc(100vw - 32px);
    max-width: 1180px;
  }

  .topbar {
    position: relative;
    display: block;
    padding: 18px 0;
  }

  .main-nav {
    justify-content: flex-start;
    overflow-x: auto;
    gap: 18px;
    margin-top: 21px;
    padding: 4px 0 1px;
  }

  .main-nav a {
    white-space: nowrap;
  }

  .nav-actions {
    display: none;
  }

  .text-action {
    display: none;
  }

  .mobile-login {
    display: inline-flex;
    align-items: center;
    flex: 0 0 auto;
    border: 0;
    padding: 0;
    background: transparent;
    color: #5d594f;
    font-size: 14px;
    font-weight: 750;
    white-space: nowrap;
  }

  .hero {
    min-height: 500px;
    margin-top: 5px;
    padding: 54px 52px 72px;
    border-radius: 25px;
  }

  .hero h1 {
    font-size: 58px;
  }

  .hero-description {
    max-width: 280px;
  }

  .hero-control {
    width: 38px;
    height: 38px;
    font-size: 29px;
  }

  .hero-prev { left: 10px; }
  .hero-next { right: 10px; }

  .hero-dots { bottom: 16px; }

  .content-section,
  .contribute-section {
    padding-top: 72px;
  }

  .contribute-section {
    padding-bottom: 72px;
  }

  .section-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 22px;
  }

  .character-grid,
  .meme-grid {
    grid-template-columns: 1fr;
  }

  .character-card {
    display: grid;
    grid-template-columns: 112px 1fr;
  }

  .character-portrait {
    min-height: 100%;
  }

  .avatar-image {
    padding: 8px;
  }

  .card-content p {
    min-height: 0;
  }

  .meme-card {
    display: grid;
    grid-template-columns: 126px 1fr;
  }

  .meme-preview {
    min-height: 100%;
  }

  .meme-image {
    min-height: 100%;
    height: 100%;
    aspect-ratio: auto;
  }

  .music-card {
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 14px;
    padding: 14px;
  }

  .music-cover {
    width: 96px;
    height: 96px;
    border-radius: 20px;
  }

  .chronicle-card {
    min-height: 0;
    padding: 36px 25px;
  }

  .timeline {
    min-height: 130px;
  }

  .timeline-line { top: 63px; }
  .timeline-dot { top: 49px; }
  .label-two { bottom: 7px; }

  .contribute-card {
    align-items: flex-start;
    flex-direction: column;
    padding: 31px 25px;
  }

  .footer {
    align-items: flex-start;
    flex-direction: column;
    padding-bottom: 26px;
  }
}

@media (max-width: 560px) {
  .hero {
    min-height: 530px;
    padding: 48px 26px 70px;
  }

  .hero h1 {
    font-size: 52px;
  }

  .hero-slogan {
    font-size: 20px;
  }

  .hero-actions {
    gap: 9px;
  }

  .hero-actions .button {
    flex: 1;
    padding: 0 13px;
  }

  .hero-control {
    top: auto;
    bottom: 13px;
    width: 32px;
    height: 32px;
    font-size: 25px;
    transform: none;
  }

  .hero-control:hover {
    transform: scale(1.04);
  }

  .hero-prev { left: 20px; }
  .hero-next { right: 20px; }

  .hero-dots {
    bottom: 25px;
    gap: 7px;
  }
}
</style>
