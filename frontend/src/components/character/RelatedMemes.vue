<script setup lang="ts">
import type { Meme } from '@/types/meme'

defineProps<{
  memes: Meme[]
}>()
</script>

<template>
  <section id="related-memes" class="related-section">
    <div class="section-heading">
      <div>
        <p>RELATED MEMES</p>
        <h2>相关表情包</h2>
      </div>
      <RouterLink to="/memes">查看全部 <span>→</span></RouterLink>
    </div>

    <p v-if="memes.length === 0" class="empty-message">暂时还没有关联表情包。</p>

    <div v-else class="meme-grid">
      <RouterLink v-for="meme in memes" :key="meme.id" class="meme-card" to="/memes">
        <img :src="meme.image_url" :alt="meme.title" />
        <div>
          <h3>{{ meme.title }}</h3>
          <p>{{ meme.source_name || '小站收录' }}</p>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.related-section { margin-top: 62px; scroll-margin-top: 108px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 26px; }
.section-heading p { margin: 0 0 10px; color: #b88a12; font-size: 12px; font-weight: 900; letter-spacing: 0.13em; }
.section-heading h2 { margin: 0; color: #25231f; font-size: clamp(31px, 4vw, 43px); font-weight: 900; letter-spacing: -0.06em; line-height: 1; }
.section-heading a { color: #896d33; font-size: 14px; font-weight: 850; text-decoration: none; white-space: nowrap; }
.meme-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.meme-card { overflow: hidden; border: 1px solid #f0e3cf; border-radius: 25px; background: #fffaf0; color: inherit; text-decoration: none; box-shadow: 0 10px 24px rgba(80, 61, 32, 0.05); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.meme-card:hover { transform: translateY(-5px); box-shadow: 0 18px 32px rgba(80, 61, 32, 0.1); }
.meme-card img { display: block; width: 100%; aspect-ratio: 1; object-fit: cover; }
.meme-card div { padding: 14px 16px 16px; }
.meme-card h3 { margin: 0; color: #322e27; font-size: 16px; font-weight: 900; }
.meme-card p { margin: 6px 0 0; color: #907b55; font-size: 12px; font-weight: 750; }
.empty-message { margin: 0; border: 1px dashed #deceb4; border-radius: 22px; padding: 26px; color: #85745a; background: #fffaf0; }
@media (max-width: 900px) { .meme-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 560px) { .section-heading { align-items: flex-start; flex-direction: column; } .meme-grid { grid-template-columns: 1fr; } }
</style>
