<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { getFeaturedCharacters } from '@/api/modules/characters'
import { getLatestMemes } from '@/api/modules/memes'
import type { Character } from '@/types/character'
import type { Meme } from '@/types/meme'

const characters = ref<Character[]>([])
const charactersLoading = ref(true)
const charactersError = ref(false)
const latestMemes = ref<Meme[]>([])
const memesLoading = ref(true)
const memesError = ref(false)
const route = useRoute()

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

onMounted(() => {
  if (route.path === '/') {
    loadCharacters()
    loadLatestMemes()
  }
})

const albums = [
  { title: '午后慢慢转', character: '耄耋 · 轻松循环', tone: 'maodie', icon: '☀' },
  { title: '鼠鼠的口袋歌', character: '鼠鼠 · 轻快收藏', tone: 'shushu', icon: '✿' },
  { title: '曼波不下班', character: '曼波 · 随时摇摆', tone: 'manbo', icon: '♪' },
]
</script>

<template>
  <RouterView v-if="route.path !== '/'" />

  <div v-else class="site-shell">
    <header class="topbar">
      <a class="brand" href="#top" aria-label="基米小站首页">
        <span class="brand-mark">基</span>
        <span>基米小站</span>
      </a>

      <nav class="main-nav" aria-label="主导航">
        <a href="#characters">角色馆</a>
        <RouterLink to="/memes">表情包</RouterLink>
        <a href="#music">音乐馆</a>
        <a href="#chronicle">编年史</a>
        <button class="mobile-login" type="button">登录</button>
      </nav>

      <div class="nav-actions">
        <a class="text-action" href="#contribute">投稿</a>
        <button class="login-button" type="button">登录</button>
      </div>
    </header>

    <main id="top">
      <section class="hero section-wrap" aria-labelledby="hero-title">
        <div class="hero-copy">
          <p class="eyebrow">HAKIMI LITTLE STATION</p>
          <h1 id="hero-title">基米小站</h1>
          <p class="hero-slogan">正经做收录，抽象做内容</p>
          <p class="hero-description">
            给每个令人会心一笑的瞬间，留一盏温柔又明亮的小灯。
          </p>
          <div class="hero-actions">
            <a class="button button-primary" href="#characters">探索角色 <span>→</span></a>
            <button class="button button-secondary" type="button">随机来一张 <span>↗</span></button>
          </div>
        </div>

        <div class="hero-art" aria-label="基米小站视觉占位">
          <span class="sun-orb">☼</span>
          <span class="bubble bubble-one">哈</span>
          <span class="bubble bubble-two">咪</span>
          <div class="hero-card hero-card-main">
            <span class="hero-card-label">今日收录</span>
            <strong>把快乐<br />放大一点</strong>
            <span class="hero-card-arrow">↗</span>
          </div>
          <div class="hero-card hero-card-small">温柔 · 有趣 · 正在发生</div>
        </div>
      </section>

      <section id="characters" class="section-wrap content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">CHARACTER ARCHIVE</p>
            <h2>首批角色</h2>
          </div>
          <a class="section-link" href="#characters">查看全部角色 <span>→</span></a>
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
              <button type="button" class="archive-button">进入档案 <span>→</span></button>
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
                <span v-if="meme.author_name">收录：{{ meme.author_name }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>

      <section id="music" class="section-wrap content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">LISTEN TO HAKIMI</p>
            <h2>音乐推荐</h2>
          </div>
          <a class="section-link" href="#music">更多歌单 <span>→</span></a>
        </div>

        <div class="album-grid">
          <article v-for="album in albums" :key="album.title" class="album-card">
            <div class="record-wrap">
              <div class="record" :class="album.tone">
                <span>{{ album.icon }}</span>
              </div>
              <div class="record-hole"></div>
            </div>
            <div class="album-copy">
              <p>{{ album.character }}</p>
              <h3>{{ album.title }}</h3>
              <button type="button" class="play-button"><span>▶</span> 播放试听</button>
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
            <a class="button button-dark" href="#chronicle">进入时间线 <span>→</span></a>
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
          <button type="button" class="button button-primary">我要投稿 <span>↗</span></button>
        </div>
      </section>
    </main>

    <footer class="footer">
      <span>基米小站 · 认真收录每一份快乐</span>
      <span>© 2026 HAKIMI LITTLE STATION</span>
    </footer>
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

.login-button {
  border: 1px solid #e8dfc9;
  border-radius: 10px;
  padding: 9px 16px;
  background: #fffdf7;
  color: #403d36;
  font-size: 14px;
  font-weight: 700;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(350px, 0.98fr);
  align-items: center;
  min-height: 490px;
  margin-top: 14px;
  padding: 58px clamp(28px, 6vw, 72px);
  border: 1px solid #f0e4ca;
  border-radius: 34px;
  background: linear-gradient(120deg, #fff6cc 0%, #fff9e8 52%, #ffe9ec 100%);
  overflow: hidden;
}

.hero-copy {
  min-width: 0;
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

.hero-art {
  position: relative;
  min-height: 330px;
}

.sun-orb {
  position: absolute;
  top: 8px;
  right: 6%;
  display: grid;
  width: 92px;
  height: 92px;
  place-items: center;
  border-radius: 50%;
  background: #ffd85a;
  color: #9a6c11;
  font-size: 48px;
  transform: rotate(-15deg);
}

.bubble {
  position: absolute;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #825e64;
  font-weight: 800;
}

.bubble-one {
  top: 42px;
  left: 8%;
  width: 55px;
  height: 55px;
  background: #ffc9d1;
  transform: rotate(-13deg);
}

.bubble-two {
  right: 4%;
  bottom: 22px;
  width: 43px;
  height: 43px;
  background: #dcebd9;
  color: #4e784c;
  transform: rotate(15deg);
}

.hero-card {
  position: absolute;
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 25px;
  box-shadow: 0 18px 40px rgba(148, 112, 50, 0.16);
}

.hero-card-main {
  top: 88px;
  right: 13%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: min(270px, 70%);
  min-height: 210px;
  padding: 26px;
  background: linear-gradient(145deg, #fff 0%, #fff9e9 100%);
  transform: rotate(5deg);
}

.hero-card-label {
  color: #ab8b55;
  font-size: 12px;
  font-weight: 700;
}

.hero-card-main strong {
  color: #3e3a31;
  font-size: 28px;
  line-height: 1.25;
  letter-spacing: -0.06em;
}

.hero-card-arrow {
  align-self: flex-end;
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border-radius: 10px;
  background: #ffdb54;
}

.hero-card-small {
  bottom: 18px;
  left: 10%;
  padding: 13px 17px;
  background: #f5d8e7;
  color: #75505d;
  font-size: 12px;
  font-weight: 750;
  transform: rotate(-5deg);
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
  .topbar {
    grid-template-columns: auto 1fr;
    gap: 16px;
  }

  .main-nav {
    justify-content: flex-end;
  }

  .nav-actions {
    grid-column: 1 / -1;
    justify-content: flex-end;
  }

  .hero {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .hero-art {
    max-width: 510px;
    width: 100%;
    margin: 0 auto;
  }

  .character-grid,
  .meme-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .album-grid {
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
    min-height: 0;
    margin-top: 5px;
    padding: 40px 24px 20px;
    border-radius: 25px;
  }

  .hero h1 {
    font-size: 58px;
  }

  .hero-description {
    max-width: 280px;
  }

  .hero-art {
    min-height: 282px;
  }

  .hero-card-main {
    top: 58px;
    right: 10%;
    min-height: 178px;
    padding: 21px;
  }

  .hero-card-main strong {
    font-size: 24px;
  }

  .sun-orb {
    width: 72px;
    height: 72px;
    font-size: 37px;
  }

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
</style>
