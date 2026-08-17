<script setup lang="ts">
import type { CharacterDetail } from '@/types/character'

defineProps<{
  characters: CharacterDetail[]
}>()
</script>

<template>
  <section class="result-section" aria-labelledby="character-results-title">
    <div class="section-heading">
      <div>
        <p>CHARACTER ARCHIVE</p>
        <h2 id="character-results-title">🐱 角色</h2>
      </div>
      <span>{{ characters.length }} 位相关角色</span>
    </div>

    <div class="character-results">
      <RouterLink
        v-for="character in characters"
        :key="character.id"
        class="character-card"
        :to="{ name: 'character-detail', params: { slug: character.slug } }"
        :style="{ '--character-color': character.theme_color || '#fff0b8' }"
      >
        <img
          v-if="character.avatar_large_url || character.avatar_url"
          :src="character.avatar_large_url || character.avatar_url || ''"
          :alt="character.name"
        />
        <div class="character-copy">
          <span class="archive-tag">哈基米百科档案</span>
          <h3>{{ character.name }}</h3>
          <p>{{ character.description || '角色档案正在补充中。' }}</p>

          <div v-if="character.timeline?.length" class="timeline-preview">
            <span v-for="event in character.timeline.slice(0, 2)" :key="`${character.id}-${event.date}-${event.title}`">
              <b>{{ event.date }}</b>{{ event.title }}
            </span>
          </div>

          <strong>查看完整档案 →</strong>
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

.section-heading > span {
  color: #9d8656;
  font-size: 14px;
  font-weight: 800;
}

.character-results {
  display: grid;
  gap: 16px;
}

.character-card {
  display: grid;
  grid-template-columns: 148px minmax(0, 1fr);
  gap: 24px;
  overflow: hidden;
  padding: 18px;
  border: 1px solid color-mix(in srgb, var(--character-color) 72%, #eadfca);
  border-radius: 26px;
  background: linear-gradient(135deg, var(--character-color), #fffdf7 68%);
  color: inherit;
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.character-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 14px 28px rgba(79, 61, 32, 0.1);
}

.character-card img {
  width: 148px;
  height: 148px;
  border: 4px solid rgba(255, 253, 247, 0.82);
  border-radius: 22px;
  object-fit: cover;
  background: #fffdf7;
}

.character-copy {
  min-width: 0;
}

.archive-tag {
  color: #9a7512;
  font-size: 12px;
  font-weight: 900;
}

.character-copy h3 {
  margin: 7px 0 0;
  color: #25231f;
  font-size: 24px;
}

.character-copy > p {
  margin: 10px 0 0;
  color: #6f6047;
  font-size: 15px;
  line-height: 1.7;
}

.timeline-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 14px;
}

.timeline-preview span {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.82);
  color: #725c33;
  font-size: 12px;
  font-weight: 800;
}

.timeline-preview b {
  margin-right: 5px;
  color: #b88a12;
}

.character-copy strong {
  display: inline-block;
  margin-top: 16px;
  color: #604714;
  font-size: 14px;
}

@media (max-width: 620px) {
  .result-section {
    padding: 24px;
  }

  .character-card {
    grid-template-columns: 92px minmax(0, 1fr);
    gap: 16px;
  }

  .character-card img {
    width: 92px;
    height: 92px;
  }

  .character-copy h3 {
    font-size: 20px;
  }
}
</style>
