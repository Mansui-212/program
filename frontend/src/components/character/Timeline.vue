<script setup lang="ts">
import type { CharacterTimelineEvent } from '@/types/character'

defineOptions({
  name: 'CharacterTimeline',
})

defineProps<{
  events: CharacterTimelineEvent[]
}>()
</script>

<template>
  <section class="timeline-section">
    <div class="section-heading">
      <div>
        <p>HAKIMI CHRONICLE</p>
        <h2>哈基米编年史</h2>
      </div>
      <span>持续更新中</span>
    </div>

    <p v-if="events.length === 0" class="empty-message">这位角色的编年史正在整理中。</p>

    <ol v-else class="timeline-list">
      <li v-for="event in events" :key="`${event.date}-${event.title}`">
        <time>{{ event.date }}</time>
        <span class="timeline-dot"></span>
        <article>
          <h3>{{ event.title }}</h3>
          <p>{{ event.content }}</p>
        </article>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.timeline-section { margin-top: 52px; }
.section-heading { display: flex; align-items: end; justify-content: space-between; gap: 20px; margin-bottom: 26px; }
.section-heading p { margin: 0 0 10px; color: #b88a12; font-size: 12px; font-weight: 900; letter-spacing: 0.13em; }
.section-heading h2 { margin: 0; color: #25231f; font-size: clamp(31px, 4vw, 43px); font-weight: 900; letter-spacing: -0.06em; line-height: 1; }
.section-heading > span { border-radius: 999px; padding: 7px 11px; background: #fff0b2; color: #795c1c; font-size: 12px; font-weight: 800; white-space: nowrap; }
.timeline-list { position: relative; display: grid; gap: 0; margin: 0; padding: 0; list-style: none; }
.timeline-list::before { position: absolute; top: 25px; bottom: 25px; left: 100px; width: 2px; background: linear-gradient(#f6c534, #f3dfbe); content: ''; }
.timeline-list li { position: relative; display: grid; grid-template-columns: 78px 44px minmax(0, 1fr); gap: 0; align-items: start; min-height: 130px; }
time { padding-top: 16px; color: #987a45; font-size: 13px; font-weight: 900; }
.timeline-dot { position: relative; z-index: 1; justify-self: center; width: 16px; height: 16px; margin-top: 18px; border: 4px solid #fffaf0; border-radius: 50%; background: #f6c534; box-shadow: 0 0 0 1px #e8b92f; }
article { margin-bottom: 20px; border: 1px solid #f0e3cf; border-radius: 24px; padding: 20px 22px; background: #fffaf0; box-shadow: 0 10px 24px rgba(80, 61, 32, 0.05); }
article h3 { margin: 0; color: #342f27; font-size: 18px; font-weight: 900; }
article p { margin: 8px 0 0; color: #746551; font-size: 14px; line-height: 1.7; }
.empty-message { margin: 0; border: 1px dashed #deceb4; border-radius: 22px; padding: 26px; color: #85745a; background: #fffaf0; }
@media (max-width: 560px) { .section-heading { align-items: flex-start; flex-direction: column; } .timeline-list::before { left: 9px; } .timeline-list li { grid-template-columns: 25px minmax(0, 1fr); gap: 12px; } time { grid-column: 2; grid-row: 1; padding-top: 0; } .timeline-dot { grid-column: 1; grid-row: 1 / span 2; justify-self: start; margin-top: 3px; } article { grid-column: 2; grid-row: 2; } }
</style>
