<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import CharacterCard from '@/components/character/CharacterCard.vue'

import { getCharacters } from '@/api/modules/characters'

import type { Character } from '@/types/character'


const characters = ref<Character[]>([])

const loading = ref(true)

const error = ref('')


const characterCount = computed(() => {
  return characters.value.length
})


async function loadCharacters() {
  loading.value = true
  error.value = ''

  try {
    const response = await getCharacters()

    characters.value = response.data
  } catch (err) {
    console.error('加载全部角色失败：', err)

    error.value = '角色档案加载失败，请稍后再试。'
  } finally {
    loading.value = false
  }
}


onMounted(() => {
  loadCharacters()
})
</script>


<template>
  <main class="characters-page">

    <!-- 顶部标题 -->

    <section class="characters-hero">

      <div>
        <p class="section-kicker">
          CHARACTER ARCHIVE
        </p>

        <h1>
          全部角色
        </h1>

        <p class="hero-description">
          收录基米小站中的哈基米家族成员、衍生角色与相关形象。
        </p>
      </div>


      <div class="archive-count">
        <span class="count-number">
          {{ characterCount }}
        </span>

        <span class="count-text">
          个角色档案
        </span>
      </div>

    </section>


    <!-- 加载状态 -->

    <section
      v-if="loading"
      class="state-card"
    >
      <div class="loading-dot"></div>

      <p>
        正在翻找哈基米档案……
      </p>
    </section>


    <!-- 错误状态 -->

    <section
      v-else-if="error"
      class="state-card"
    >
      <h2>
        加载失败
      </h2>

      <p>
        {{ error }}
      </p>

      <button
        type="button"
        @click="loadCharacters"
      >
        重新加载
      </button>
    </section>


    <!-- 空状态 -->

    <section
      v-else-if="characters.length === 0"
      class="state-card"
    >
      <h2>
        暂时没有角色档案
      </h2>

      <p>
        新的哈基米成员正在赶来的路上。
      </p>
    </section>


    <!-- 角色列表 -->

    <section
      v-else
      class="characters-section"
    >
      <div class="section-title-row">

        <div>
          <p class="section-kicker">
            ARCHIVE LIST
          </p>

          <h2>
            角色档案
          </h2>
        </div>

      </div>


      <div class="characters-grid">

        <CharacterCard
          v-for="character in characters"
          :key="character.id"
          :character="character"
        />

      </div>

    </section>

  </main>
</template>


<style scoped>
.characters-page {
  width: min(1500px, calc(100% - 48px));

  margin: 0 auto;

  padding:
    72px
    0
    120px;
}


/* =========================
   Hero
========================= */

.characters-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;

  gap: 40px;

  padding: 64px;

  border: 1px solid rgba(116, 91, 46, 0.1);
  border-radius: 40px;

  background:
    linear-gradient(
      135deg,
      #fff4c9 0%,
      #fff8df 45%,
      #ffe4ec 100%
    );

  box-shadow:
    0 24px 60px rgba(79, 61, 32, 0.06);
}


.section-kicker {
  margin: 0 0 14px;

  color: #b88713;

  font-size: 14px;
  font-weight: 900;

  letter-spacing: 0.12em;
}


.characters-hero h1 {
  margin: 0;

  color: #292722;

  font-size: clamp(50px, 7vw, 82px);

  line-height: 1;
}


.hero-description {
  max-width: 650px;

  margin: 24px 0 0;

  color: #706657;

  font-size: 17px;
  line-height: 1.8;
}


.archive-count {
  display: flex;
  flex-direction: column;

  min-width: 150px;

  padding: 26px 28px;

  border: 1px solid rgba(116, 91, 46, 0.1);
  border-radius: 28px;

  background:
    rgba(255, 255, 255, 0.55);

  backdrop-filter: blur(12px);
}


.count-number {
  color: #292722;

  font-size: 48px;
  font-weight: 900;

  line-height: 1;
}


.count-text {
  margin-top: 8px;

  color: #887551;

  font-size: 14px;
  font-weight: 800;
}


/* =========================
   List
========================= */

.characters-section {
  margin-top: 80px;
}


.section-title-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;

  margin-bottom: 32px;
}


.section-title-row h2 {
  margin: 0;

  color: #292722;

  font-size: 44px;
}


.characters-grid {
  display: grid;

  grid-template-columns:
    repeat(4, minmax(0, 1fr));

  gap: 26px;
}


/* =========================
   State
========================= */

.state-card {
  display: grid;
  place-items: center;

  min-height: 300px;

  margin-top: 60px;
  padding: 50px;

  border: 1px solid #eadfca;
  border-radius: 36px;

  background: #fffdf8;

  text-align: center;
}


.state-card h2 {
  margin: 0;

  color: #292722;

  font-size: 30px;
}


.state-card p {
  margin: 14px 0 0;

  color: #776c5c;
}


.state-card button {
  height: 46px;

  margin-top: 22px;
  padding: 0 24px;

  border: 0;
  border-radius: 999px;

  background: #f6c534;

  color: #292722;

  font-weight: 900;

  cursor: pointer;
}


.loading-dot {
  width: 18px;
  height: 18px;

  border-radius: 50%;

  background: #f6c534;

  animation:
    loadingPulse
    1s
    ease-in-out
    infinite alternate;
}


@keyframes loadingPulse {
  from {
    transform: scale(0.8);
    opacity: 0.45;
  }

  to {
    transform: scale(1.25);
    opacity: 1;
  }
}


/* =========================
   Responsive
========================= */

@media (max-width: 1150px) {

  .characters-grid {
    grid-template-columns:
      repeat(3, minmax(0, 1fr));
  }

}


@media (max-width: 850px) {

  .characters-hero {
    align-items: stretch;
    flex-direction: column;

    padding: 44px 36px;
  }


  .archive-count {
    width: fit-content;
  }


  .characters-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

}


@media (max-width: 560px) {

  .characters-page {
    width: min(100% - 28px, 1500px);

    padding-top: 40px;
  }


  .characters-hero {
    padding: 36px 26px;

    border-radius: 30px;
  }


  .characters-grid {
    grid-template-columns: 1fr;
  }


  .section-title-row h2 {
    font-size: 36px;
  }

}
</style>
