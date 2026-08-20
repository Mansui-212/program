<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getChronicleEvents } from '@/api/modules/chronicle'

import type { ChronicleEvent } from '@/types/chronicle'

const events = ref<ChronicleEvent[]>([])
const currentYear = ref(new Date().getFullYear())
const loading = ref(true)
const error = ref('')

const years = computed(() => {
  return [...new Set(events.value.map((event) => event.year))].sort((a, b) => a - b)
})

const firstYear = computed(() => years.value[0] ?? new Date().getFullYear())
const lastYear = computed(() => years.value.at(-1) ?? firstYear.value)

const visibleEventGroups = computed(() => {
  return years.value
    .filter((year) => year <= currentYear.value)
    .map((year) => ({
      year,
      events: events.value.filter((event) => event.year === year),
    }))
})

function formatDate(date: string | null) {
  return date?.replaceAll('-', '.') || '年份待考'
}

function eventIcon(event: ChronicleEvent) {
  if (/曼波|音乐|哈基米/.test(event.title)) return '♪'
  if (/Doro|桃乐丝/.test(event.title)) return '✦'
  if (/鼠鼠|Swag/.test(event.title)) return '◉'
  return '🐱'
}

function selectYear(year: number) {
  currentYear.value = year
}

async function loadChronicle() {
  loading.value = true
  error.value = ''

  try {
    const response = await getChronicleEvents()
    events.value = response.data

    if (years.value.length > 0) {
      currentYear.value = lastYear.value
    }
  } catch (reason) {
    console.error('加载编年史失败', reason)
    error.value = '编年史暂时无法加载，请稍后再试。'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadChronicle()
})
</script>

<template>
  <main class="chronicle-page">
    <section class="chronicle-hero">
      <p class="section-kicker">HAKIMI CHRONICLE</p>
      <h1>哈基米编年史</h1>
      <p>
        从一段被听成“哈基米”的旋律开始，收录角色、音乐、表情包与二创文化不断交汇的时刻。
      </p>
      <span class="hero-stamp">持续收录中</span>
    </section>

    <section class="timeline-card" aria-label="编年史时间轴">
      <div class="timeline-heading">
        <div>
          <p class="eyebrow">TIMELINE CONTROL</p>
          <h2>拖动时间，回看已经发生的故事</h2>
        </div>
        <strong v-if="years.length">截至 {{ currentYear }} 年</strong>
      </div>

      <template v-if="!loading && years.length">
        <div class="timeline-years">
          <span class="origin-label">起源</span>
          <div class="timeline-line" aria-hidden="true"></div>
          <button
            v-for="year in years"
            :key="year"
            type="button"
            :class="{ active: year === currentYear, reached: year <= currentYear }"
            :aria-pressed="year === currentYear"
            @click="selectYear(year)"
          >
            <i></i>
            <span>{{ year }}</span>
          </button>
          <span class="now-label">现在</span>
        </div>

        <input
          v-model.number="currentYear"
          class="timeline-slider"
          type="range"
          :min="firstYear"
          :max="lastYear"
          step="1"
          aria-label="选择编年史年份"
        />
      </template>

      <p v-else-if="loading" class="timeline-status">正在翻找哈基米档案...</p>
      <p v-else class="timeline-status">第一条编年史正在整理中。</p>
    </section>

    <p v-if="error" class="status-message error-message">{{ error }}</p>

    <section v-if="!loading && visibleEventGroups.length" class="event-groups">
      <section v-for="group in visibleEventGroups" :key="group.year" class="year-group">
        <header class="year-heading">
          <span>{{ group.year }}</span>
          <div></div>
        </header>

        <div class="event-list">
          <article v-for="event in group.events" :key="event.id" class="event-card">
            <div class="event-rail" aria-hidden="true">
              <span>{{ eventIcon(event) }}</span>
            </div>

            <img v-if="event.image_url" :src="event.image_url" :alt="event.title" class="event-image" />

            <div class="event-copy">
              <p class="event-date">{{ formatDate(event.date) }}</p>
              <h3>{{ event.title }}</h3>
              <p>{{ event.content }}</p>
            </div>
          </article>
        </div>
      </section>
    </section>

    <section v-else-if="!loading && !error" class="empty-card">
      <span>🐱</span>
      <h2>第一页档案尚未写入</h2>
      <p>管理员添加事件后，时间轴会自动出现新的年份与节点。</p>
    </section>
  </main>
</template>

<style scoped>
.chronicle-page {
  width: min(1120px, calc(100% - 48px));
  margin: 0 auto;
  padding: 52px 0 120px;
}

.chronicle-hero {
  position: relative;
  overflow: hidden;
  padding: clamp(38px, 7vw, 76px);
  border-radius: 42px;
  background:
    radial-gradient(circle at 86% 18%, rgba(246, 211, 93, 0.18), transparent 15rem),
    radial-gradient(circle at 76% 120%, rgba(255, 168, 189, 0.18), transparent 20rem),
    #2c312d;
  color: #fffdf7;
  box-shadow: 0 30px 70px rgba(35, 40, 35, 0.22);
}

.section-kicker,
.eyebrow {
  margin: 0 0 13px;
  color: #f6d35d;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.14em;
}

.chronicle-hero h1 {
  max-width: 780px;
  margin: 0;
  font-size: clamp(46px, 7vw, 76px);
  letter-spacing: -0.075em;
  line-height: 1;
}

.chronicle-hero > p:not(.section-kicker) {
  max-width: 660px;
  margin: 23px 0 0;
  color: rgba(255, 253, 247, 0.76);
  font-size: 17px;
  line-height: 1.85;
}

.hero-stamp {
  display: inline-flex;
  margin-top: 30px;
  border: 1px solid rgba(246, 211, 93, 0.55);
  border-radius: 999px;
  padding: 9px 14px;
  background: rgba(246, 211, 93, 0.12);
  color: #f6d35d;
  font-size: 13px;
  font-weight: 850;
}

.timeline-card {
  margin-top: 28px;
  padding: clamp(24px, 4vw, 38px);
  border: 1px solid #eee1ca;
  border-radius: 34px;
  background: #fffaf0;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.timeline-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
}

.timeline-heading .eyebrow { color: #b88a12; }

.timeline-heading h2 {
  margin: 0;
  color: #29261f;
  font-size: clamp(21px, 3vw, 30px);
  letter-spacing: -0.045em;
}

.timeline-heading strong {
  color: #8c6b21;
  font-size: 15px;
  white-space: nowrap;
}

.timeline-years {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  min-height: 72px;
  margin-top: 34px;
  padding: 0 8px;
}

.timeline-line {
  position: absolute;
  top: 13px;
  right: 52px;
  left: 52px;
  height: 3px;
  border-radius: 99px;
  background: #eadfca;
}

.origin-label,
.now-label {
  z-index: 1;
  color: #9c8760;
  font-size: 12px;
  font-weight: 850;
  line-height: 28px;
}

.timeline-years button {
  z-index: 1;
  display: grid;
  gap: 8px;
  min-width: 46px;
  border: 0;
  padding: 0;
  background: transparent;
  color: #9c8760;
  font: inherit;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
}

.timeline-years button i {
  display: block;
  width: 28px;
  height: 28px;
  margin: 0 auto;
  border: 7px solid #fffaf0;
  border-radius: 50%;
  background: #d5c6aa;
  box-shadow: 0 0 0 2px #d5c6aa;
  transition: transform 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.timeline-years button.reached { color: #71571f; }
.timeline-years button.reached i { background: #f1c22f; box-shadow: 0 0 0 2px #f1c22f; }
.timeline-years button.active i { transform: scale(1.18); background: #ef8fa8; box-shadow: 0 0 0 3px #ef8fa8; }

.timeline-slider {
  width: 100%;
  height: 7px;
  margin-top: 9px;
  appearance: none;
  border-radius: 999px;
  background: linear-gradient(90deg, #f1c22f, #ef8fa8);
  cursor: pointer;
}

.timeline-slider::-webkit-slider-thumb {
  width: 20px;
  height: 20px;
  appearance: none;
  border: 4px solid #fffaf0;
  border-radius: 50%;
  background: #2c312d;
  box-shadow: 0 0 0 2px #2c312d;
}

.timeline-slider::-moz-range-thumb {
  width: 14px;
  height: 14px;
  border: 4px solid #fffaf0;
  border-radius: 50%;
  background: #2c312d;
  box-shadow: 0 0 0 2px #2c312d;
}

.timeline-status,
.status-message {
  margin: 28px 0 0;
  color: #7b6a4a;
  font-weight: 750;
}

.error-message { color: #bf4c4c; }

.event-groups { margin-top: 46px; }

.year-group + .year-group { margin-top: 46px; }

.year-heading {
  display: flex;
  align-items: center;
  gap: 17px;
  margin-bottom: 20px;
}

.year-heading span {
  color: #2f2c24;
  font-size: 34px;
  font-weight: 950;
  letter-spacing: -0.065em;
}

.year-heading div { height: 1px; flex: 1; background: #e9ddca; }

.event-list {
  display: grid;
  gap: 17px;
}

.event-card {
  display: grid;
  grid-template-columns: auto auto minmax(0, 1fr);
  gap: 20px;
  padding: 23px;
  border: 1px solid #eee1ca;
  border-radius: 28px;
  background: rgba(255, 250, 240, 0.85);
  box-shadow: 0 14px 32px rgba(79, 61, 32, 0.06);
}

.event-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.event-rail::after {
  width: 2px;
  min-height: 44px;
  flex: 1;
  margin-top: 10px;
  border-radius: 99px;
  background: #eadfca;
  content: '';
}

.event-rail span {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 15px;
  background: #fff0b8;
  color: #493819;
  font-size: 20px;
}

.event-image {
  width: 150px;
  height: 126px;
  border-radius: 19px;
  object-fit: cover;
}

.event-copy { padding: 3px 0 2px; }

.event-date {
  margin: 0;
  color: #a38754;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.04em;
}

.event-copy h3 {
  margin: 6px 0 0;
  color: #29261f;
  font-size: 21px;
  letter-spacing: -0.045em;
}

.event-copy > p:last-child {
  margin: 10px 0 0;
  color: #716348;
  font-size: 15px;
  line-height: 1.8;
}

.empty-card {
  margin-top: 34px;
  padding: 54px 30px;
  border: 1px dashed #dfc77d;
  border-radius: 30px;
  background: #fffaf0;
  text-align: center;
}

.empty-card span { font-size: 42px; }
.empty-card h2 { margin: 16px 0 0; color: #2c312d; font-size: 25px; }
.empty-card p { margin: 10px 0 0; color: #7b6a4a; line-height: 1.7; }

@media (max-width: 700px) {
  .chronicle-page { width: calc(100% - 32px); padding-top: 30px; }
  .timeline-heading { align-items: flex-start; flex-direction: column; }
  .timeline-years { gap: 5px; padding: 0; overflow-x: auto; }
  .timeline-line { right: 38px; left: 38px; }
  .event-card { grid-template-columns: auto minmax(0, 1fr); gap: 14px; padding: 18px; }
  .event-image { grid-column: 2; width: 100%; height: 180px; }
  .event-copy { grid-column: 2; }
}
</style>
