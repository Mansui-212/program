<script setup lang="ts">
import type { MusicTrack } from '@/types/musicTrack'

defineProps<{
  tracks: MusicTrack[]
}>()
</script>

<template>
  <section id="related-music" class="related-section">
    <div class="section-heading">
      <div>
        <p>RELATED MUSIC</p>
        <h2>相关音乐</h2>
      </div>
      <RouterLink to="/music">打开唱片机 <span>→</span></RouterLink>
    </div>

    <p v-if="tracks.length === 0" class="empty-message">暂时还没有关联音乐。</p>

    <div v-else class="music-list">
      <RouterLink v-for="track in tracks" :key="track.id" class="track-card" to="/music">
        <div class="track-cover">
          <img v-if="track.cover_url" :src="track.cover_url" :alt="track.title" />
          <span v-else>♪</span>
        </div>
        <div>
          <p>{{ track.author_name || '未知作者' }}</p>
          <h3>{{ track.title }}</h3>
          <small>播放 {{ track.play_count }} · 去唱片机播放</small>
        </div>
        <span class="play-mark">▶</span>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.related-section { margin-top: 62px; padding-bottom: 12px; scroll-margin-top: 108px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 26px; }
.section-heading p { margin: 0 0 10px; color: #b88a12; font-size: 12px; font-weight: 900; letter-spacing: 0.13em; }
.section-heading h2 { margin: 0; color: #25231f; font-size: clamp(31px, 4vw, 43px); font-weight: 900; letter-spacing: -0.06em; line-height: 1; }
.section-heading a { color: #896d33; font-size: 14px; font-weight: 850; text-decoration: none; white-space: nowrap; }
.music-list { display: grid; gap: 14px; }
.track-card { display: grid; grid-template-columns: 64px minmax(0, 1fr) auto; align-items: center; gap: 16px; border: 1px solid #f0e3cf; border-radius: 24px; padding: 12px; background: #fffaf0; color: inherit; text-decoration: none; box-shadow: 0 10px 24px rgba(80, 61, 32, 0.05); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.track-card:hover { transform: translateX(5px); box-shadow: 0 16px 30px rgba(80, 61, 32, 0.09); }
.track-cover { display: grid; width: 64px; height: 64px; place-items: center; overflow: hidden; border-radius: 17px; background: linear-gradient(135deg, #fff0b8, #ffdce8); color: #4e4128; font-size: 26px; font-weight: 900; }
.track-cover img { width: 100%; height: 100%; object-fit: cover; }
.track-card p { margin: 0 0 3px; color: #957a4e; font-size: 12px; font-weight: 800; }
.track-card h3 { margin: 0; color: #302d27; font-size: 18px; font-weight: 900; }
.track-card small { display: block; margin-top: 4px; color: #88775c; font-size: 12px; font-weight: 700; }
.play-mark { display: grid; width: 34px; height: 34px; place-items: center; border-radius: 50%; background: #f6c534; color: #4c3b17; font-size: 11px; }
.empty-message { margin: 0; border: 1px dashed #deceb4; border-radius: 22px; padding: 26px; color: #85745a; background: #fffaf0; }
@media (max-width: 560px) { .section-heading { align-items: flex-start; flex-direction: column; } .track-card { grid-template-columns: 56px minmax(0, 1fr); } .track-cover { width: 56px; height: 56px; } .play-mark { display: none; } }
</style>
