<script setup lang="ts">
import type { MusicTrack } from '@/types/musicTrack'

defineProps<{
  music: MusicTrack[]
}>()
</script>

<template>
  <section class="result-section" aria-labelledby="music-results-title">
    <div class="section-heading">
      <div>
        <p>HAKIMI MUSIC</p>
        <h2 id="music-results-title">🎵 音乐</h2>
      </div>
      <RouterLink to="/music">去唱片机播放 →</RouterLink>
    </div>

    <div class="music-list">
      <RouterLink
        v-for="track in music"
        :key="track.id"
        class="track-card"
        :to="{ path: '/music', query: { track: track.slug } }"
      >
        <div class="track-cover">
          <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" />
          <span v-else>♪</span>
        </div>
        <div class="track-copy">
          <h3>{{ track.title }}</h3>
          <p>{{ track.description || track.author_name || '哈基米音乐档案' }}</p>
          <span>{{ track.author_name || '未知作者' }} · 播放 {{ track.play_count }}</span>
        </div>
        <span class="play-mark" aria-hidden="true">▶</span>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.result-section {
  padding: 30px;
  border-radius: 32px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.section-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.section-heading p {
  margin: 0 0 8px;
  color: #b88a12;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.section-heading h2 {
  margin: 0;
  color: #25231f;
  font-size: 28px;
}

.section-heading a {
  color: #9a7512;
  font-size: 14px;
  font-weight: 800;
  text-decoration: none;
}

.music-list {
  display: grid;
  gap: 14px;
}

.track-card {
  display: grid;
  grid-template-columns: 68px minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border: 1px solid #efe3cf;
  border-radius: 22px;
  background: #fffdf7;
  color: inherit;
  text-decoration: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.track-card:hover {
  border-color: #f6c534;
  box-shadow: 0 10px 24px rgba(246, 197, 52, 0.16);
}

.track-cover {
  display: grid;
  width: 68px;
  height: 68px;
  place-items: center;
  overflow: hidden;
  border-radius: 18px;
  background: linear-gradient(135deg, #fff6cf, #ffe3ec);
  color: #25231f;
  font-size: 26px;
  font-weight: 900;
}

.track-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.track-copy {
  min-width: 0;
}

.track-copy h3 {
  margin: 0;
  overflow: hidden;
  color: #25231f;
  font-size: 18px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-copy p {
  margin: 6px 0;
  overflow: hidden;
  color: #7b6a4a;
  font-size: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-copy span {
  color: #a58a55;
  font-size: 12px;
  font-weight: 800;
}

.play-mark {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 50%;
  background: #f6c534;
  color: #25231f;
  font-size: 14px;
}

@media (max-width: 620px) {
  .result-section {
    padding: 24px;
  }
}
</style>
