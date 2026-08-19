<script setup lang="ts">
import type { Character } from '@/types/character'


defineProps<{
  character: Character
}>()
</script>


<template>
  <RouterLink
    :to="`/character/${character.slug}`"
    class="character-card"
  >
    <div
      class="character-image"
      :style="{
        backgroundColor: character.theme_color || '#fff4cf',
      }"
    >
      <img
        v-if="character.avatar_url"
        :src="character.avatar_url"
        :alt="character.name"
      />

      <div
        v-else
        class="character-placeholder"
      >
        ?
      </div>
    </div>


    <div class="character-content">
      <h2>
        {{ character.name }}
      </h2>


      <p v-if="character.description">
        {{ character.description }}
      </p>

      <p v-else class="empty-description">
        该角色档案正在补充中。
      </p>


      <span class="enter-link">
        进入档案
        <span>→</span>
      </span>
    </div>
  </RouterLink>
</template>


<style scoped>
.character-card {
  display: flex;
  flex-direction: column;

  overflow: hidden;

  min-width: 0;

  border: 1px solid rgba(116, 91, 46, 0.12);
  border-radius: 30px;

  background: #fffdf8;

  color: inherit;
  text-decoration: none;

  box-shadow:
    0 20px 50px rgba(79, 61, 32, 0.07);

  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}


.character-card:hover {
  transform: translateY(-6px);

  border-color: rgba(246, 197, 52, 0.55);

  box-shadow:
    0 28px 70px rgba(79, 61, 32, 0.12);
}


.character-image {
  display: grid;
  place-items: center;

  width: 100%;
  aspect-ratio: 1 / 1;

  overflow: hidden;
}


.character-image img {
  display: block;

  width: 100%;
  height: 100%;

  object-fit: contain;
}


.character-placeholder {
  display: grid;
  place-items: center;

  width: 100%;
  height: 100%;

  color: #8c774b;

  font-size: 64px;
  font-weight: 900;
}


.character-content {
  display: flex;
  flex: 1;
  flex-direction: column;

  padding: 26px 28px 28px;
}


.character-content h2 {
  margin: 0;

  color: #292722;

  font-size: 27px;
  line-height: 1.25;
}


.character-content p {
  margin: 18px 0 0;

  color: #766d5f;

  font-size: 15px;
  line-height: 1.9;
}


.empty-description {
  opacity: 0.7;
}


.enter-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  margin-top: auto;
  padding-top: 28px;

  color: #65502a;

  font-size: 15px;
  font-weight: 900;
}


.character-card:hover .enter-link span {
  transform: translateX(4px);
}


.enter-link span {
  transition: transform 0.2s ease;
}
</style>
