<script setup lang="ts">
import type { Meme } from '@/types/meme'

defineProps<{
  memes: Meme[]
}>()
</script>

<template>
  <section class="result-section" aria-labelledby="meme-results-title">
    <div class="section-heading">
      <div>
        <p>MEME ARCHIVE</p>
        <h2 id="meme-results-title">😂 表情包</h2>
      </div>
      <RouterLink to="/memes">进入表情包档案 →</RouterLink>
    </div>

    <div class="meme-grid">
      <RouterLink
        v-for="meme in memes"
        :key="meme.id"
        class="meme-card"
        :to="{ path: '/memes', query: { keyword: meme.title } }"
      >
        <img :src="meme.image_url" :alt="meme.title" />
        <div>
          <h3>{{ meme.title }}</h3>
          <p>{{ meme.description || meme.source_name || '基米小站收录素材' }}</p>
        </div>
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

.meme-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
}

.meme-card {
  overflow: hidden;
  border: 1px solid #efe3cf;
  border-radius: 22px;
  background: #fffdf7;
  color: inherit;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.meme-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 14px 28px rgba(79, 61, 32, 0.1);
}

.meme-card img {
  display: block;
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background: #f4ead7;
}

.meme-card div {
  padding: 14px;
}

.meme-card h3 {
  margin: 0;
  color: #25231f;
  font-size: 16px;
}

.meme-card p {
  display: -webkit-box;
  margin: 7px 0 0;
  overflow: hidden;
  color: #7b6a4a;
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

@media (max-width: 920px) {
  .meme-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 620px) {
  .result-section {
    padding: 24px;
  }

  .meme-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
