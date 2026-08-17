<script setup lang="ts">
import type { CharacterDetail } from '@/types/character'

defineProps<{
  character: CharacterDetail
}>()
</script>

<template>
  <section
    class="character-hero"
    :style="{ '--character-color': character.theme_color || '#fff0b8' }"
  >
    <div class="hero-avatar-wrap">
      <div class="hero-avatar-glow"></div>
      <img
        v-if="character.avatar_large_url || character.avatar_url"
        class="hero-avatar"
        :src="character.avatar_large_url || character.avatar_url || ''"
        :alt="`${character.name}大头像`"
      />
      <span v-else class="avatar-fallback">{{ character.name.slice(0, 1) }}</span>
    </div>

    <div class="hero-content">
      <p class="hero-kicker">HAKIMI CHARACTER FILE</p>
      <h1>{{ character.name }}</h1>
      <p class="hero-role">网络哈基米成员</p>
      <p class="hero-description">
        {{ character.description || '这份角色档案正在持续整理中。' }}
      </p>

      <div class="hero-meta">
        <span>网络昵称：{{ character.aliases || character.name }}</span>
        <span>档案编号：{{ String(character.id).padStart(3, '0') }}</span>
      </div>

      <div class="hero-actions">
        <a href="#related-memes">查看表情包 <span>↓</span></a>
        <a href="#related-music" class="secondary-action">播放音乐 <span>♪</span></a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.character-hero {
  position: relative;
  display: grid;
  grid-template-columns: minmax(230px, 0.7fr) minmax(0, 1.3fr);
  align-items: center;
  gap: clamp(28px, 5vw, 72px);
  overflow: hidden;
  padding: clamp(34px, 5vw, 64px);
  border: 1px solid rgba(255, 255, 255, 0.8);
  border-radius: 42px;
  background:
    radial-gradient(circle at 92% 12%, rgba(255, 255, 255, 0.58), transparent 24%),
    linear-gradient(135deg, var(--character-color), #fffaf0 68%);
  box-shadow: 0 22px 55px rgba(101, 79, 39, 0.11);
}

.character-hero::after {
  position: absolute;
  right: -5%;
  bottom: -26%;
  width: 260px;
  height: 260px;
  border: 22px solid rgba(255, 255, 255, 0.32);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.hero-avatar-wrap {
  position: relative;
  z-index: 1;
  display: grid;
  aspect-ratio: 1;
  place-items: center;
}

.hero-avatar-glow {
  position: absolute;
  inset: 8%;
  border-radius: 50%;
  background: var(--character-color);
  filter: blur(18px) saturate(1.15);
  opacity: 0.72;
}

.hero-avatar,
.avatar-fallback {
  position: relative;
  z-index: 1;
  width: min(100%, 280px);
  height: min(100%, 280px);
  border: 7px solid rgba(255, 253, 247, 0.88);
  border-radius: 50%;
  background: #fffdf7;
  box-shadow: 0 18px 35px rgba(92, 67, 29, 0.18);
  object-fit: contain;
}

.avatar-fallback {
  display: grid;
  place-items: center;
  color: #5e4b2e;
  font-size: 64px;
  font-weight: 900;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-kicker {
  margin: 0 0 12px;
  color: #97721b;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.hero-content h1 {
  margin: 0;
  color: #2b2924;
  font-size: clamp(42px, 6vw, 68px);
  font-weight: 900;
  letter-spacing: -0.08em;
  line-height: 0.98;
}

.hero-role {
  display: inline-flex;
  margin: 18px 0 0;
  border: 1px solid rgba(138, 108, 36, 0.18);
  border-radius: 999px;
  padding: 6px 12px;
  background: rgba(255, 253, 247, 0.58);
  color: #6d5730;
  font-size: 13px;
  font-weight: 800;
}

.hero-description {
  max-width: 580px;
  margin: 18px 0 0;
  color: #5d5548;
  font-size: 16px;
  line-height: 1.85;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 20px;
  color: #7e6e50;
  font-size: 13px;
  font-weight: 750;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 27px;
}

.hero-actions a {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 46px;
  border: 1px solid #f2c43b;
  border-radius: 999px;
  padding: 0 19px;
  background: #f6c534;
  color: #3e3116;
  font-size: 14px;
  font-weight: 900;
  text-decoration: none;
}

.hero-actions .secondary-action {
  border-color: rgba(128, 104, 62, 0.18);
  background: rgba(255, 253, 247, 0.72);
  color: #604d2d;
}

@media (max-width: 700px) {
  .character-hero {
    grid-template-columns: 1fr;
    gap: 28px;
    border-radius: 31px;
    text-align: center;
  }

  .hero-avatar-wrap {
    width: min(220px, 70vw);
    justify-self: center;
  }

  .hero-meta,
  .hero-actions {
    justify-content: center;
  }
}
</style>
