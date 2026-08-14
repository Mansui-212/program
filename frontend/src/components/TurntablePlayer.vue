<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { MusicTrack } from '@/types/musicTrack'

const props = defineProps<{
  track: MusicTrack | null
  isPlaying: boolean
}>()

const emit = defineEmits<{
  (event: 'update:playing', value: boolean): void
  (event: 'next'): void
  (event: 'prev'): void
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const currentTime = ref(0)
const duration = ref(0)
const progressValue = ref(0)
const hasCover = computed(() => !!props.track?.cover_url)

function formatTime(seconds: number) {
  if (!Number.isFinite(seconds)) {
    return '00:00'
  }

  const minutes = Math.floor(seconds / 60)
  const restSeconds = Math.floor(seconds % 60)

  return `${String(minutes).padStart(2, '0')}:${String(restSeconds).padStart(2, '0')}`
}

function handleTimeUpdate() {
  const audio = audioRef.value

  if (!audio) return

  currentTime.value = audio.currentTime

  if (Number.isFinite(audio.duration) && audio.duration > 0) {
    progressValue.value = (audio.currentTime / audio.duration) * 100
  }
}

function handleLoadedMetadata() {
  const audio = audioRef.value

  if (!audio) return

  duration.value = Number.isFinite(audio.duration) ? audio.duration : 0
}

function handleProgressInput(event: Event) {
  const input = event.target as HTMLInputElement
  const value = Number(input.value)

  progressValue.value = value

  const audio = audioRef.value

  if (!audio || !duration.value) return

  audio.currentTime = (duration.value * value) / 100
  currentTime.value = audio.currentTime
}

function resetTrack() {
  currentTime.value = 0
  duration.value = props.track?.duration_seconds || 0
  progressValue.value = 0

  const audio = audioRef.value

  if (!audio || !props.track) return

  audio.load()
}

function togglePlay() {
  if (!props.track) return

  emit('update:playing', !props.isPlaying)
}

function handleEnded() {
  emit('next')
}

watch(
  () => props.track?.audio_url,
  () => {
    resetTrack()
  },
  {
    flush: 'post',
  },
)

watch(
  () => props.isPlaying,
  async (value) => {
    const audio = audioRef.value

    if (!audio || !props.track) return

    if (value) {
      try {
        if (audio.ended) {
          audio.currentTime = 0
        }

        await audio.play()
      } catch (error) {
        console.error('播放失败', error)
        emit('update:playing', false)
      }
    } else {
      audio.pause()
    }
  },
  {
    flush: 'post',
  },
)
</script>

<template>
  <section class="turntable-panel">
    <div class="turntable-shell">
      <div class="turntable-top">
        <div class="record-wrap">
          <div class="record" :class="{ spinning: isPlaying }">
            <div class="record-groove"></div>

            <img
              v-if="hasCover && track?.cover_url"
              class="record-label"
              :src="track.cover_url"
              :alt="track.title"
            />

            <div v-else class="record-label fallback-label">♪</div>

            <div class="record-center"></div>
          </div>
        </div>

        <div class="tonearm" :class="{ active: isPlaying }">
          <div class="tonearm-head"></div>
        </div>
      </div>

      <div class="player-meta">
        <p class="player-kicker">NOW PLAYING</p>
        <h2>{{ track?.title || '请选择一首哈基米音乐' }}</h2>
        <p class="player-subtitle">{{ track?.author_name || '等待播放' }}</p>

        <div class="progress-block">
          <div class="time-row">
            <span>{{ formatTime(currentTime) }}</span>
            <span>{{ formatTime(duration) }}</span>
          </div>

          <input
            class="progress-range"
            type="range"
            min="0"
            max="100"
            step="0.1"
            :value="progressValue"
            :disabled="!track || duration === 0"
            @input="handleProgressInput"
          />
        </div>

        <div class="player-actions">
          <button type="button" :disabled="!track" @click="$emit('prev')">上一首</button>
          <button type="button" class="primary" :disabled="!track" @click="togglePlay">
            {{ isPlaying ? '暂停' : '播放' }}
          </button>
          <button type="button" :disabled="!track" @click="$emit('next')">下一首</button>
        </div>

        <audio
          ref="audioRef"
          :src="track?.audio_url || ''"
          preload="auto"
          @ended="handleEnded"
          @durationchange="handleLoadedMetadata"
          @loadedmetadata="handleLoadedMetadata"
          @timeupdate="handleTimeUpdate"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.turntable-panel {
  position: sticky;
  top: 24px;
}

.turntable-shell {
  padding: 28px;
  border-radius: 36px;
  background: #fffaf0;
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.12);
}

.turntable-top {
  position: relative;
  display: grid;
  min-height: 420px;
  place-items: center;
  overflow: hidden;
  border-radius: 28px;
  background:
    radial-gradient(circle at 20% 20%, #fff6cf 0, transparent 30%),
    radial-gradient(circle at 80% 10%, #ffe3ec 0, transparent 32%),
    #f7ead5;
}

.record-wrap {
  display: grid;
  place-items: center;
}

.record {
  position: relative;
  width: min(320px, 70vw);
  height: min(320px, 70vw);
  border-radius: 50%;
  background: radial-gradient(circle, #1f1e1b 0 24%, #111 24% 100%);
  box-shadow:
    inset 0 0 0 10px rgba(255, 255, 255, 0.03),
    inset 0 0 0 24px rgba(255, 255, 255, 0.02),
    0 20px 50px rgba(0, 0, 0, 0.24);
}

.record.spinning {
  animation: spin 4s linear infinite;
}

.record::after {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: linear-gradient(
    120deg,
    transparent 0%,
    rgba(255, 255, 255, 0.08) 38%,
    transparent 52%
  );
  content: '';
  pointer-events: none;
}

.record-groove {
  position: absolute;
  inset: 22px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 50%;
  box-shadow:
    inset 0 0 0 16px rgba(255, 255, 255, 0.02),
    inset 0 0 0 34px rgba(255, 255, 255, 0.02),
    inset 0 0 0 52px rgba(255, 255, 255, 0.02),
    inset 0 0 0 70px rgba(255, 255, 255, 0.02);
}

.record-label {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 136px;
  height: 136px;
  border: 6px solid #f8f0de;
  border-radius: 50%;
  object-fit: cover;
  transform: translate(-50%, -50%);
}

.fallback-label {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f6c534, #ffdede);
  color: #25231f;
  font-size: 48px;
  font-weight: 900;
}

.record-center {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f8f0de;
  box-shadow: 0 0 0 6px #26221b;
  transform: translate(-50%, -50%);
}

.tonearm {
  position: absolute;
  top: 58px;
  right: 62px;
  width: 150px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, #d5c4a0, #8b7452);
  transform: rotate(18deg);
  transform-origin: left center;
  transition: transform 0.35s ease;
}

.tonearm::before {
  position: absolute;
  top: -14px;
  left: -18px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #7a6040;
  box-shadow: inset 0 0 0 8px #d5c4a0;
  content: '';
}

.tonearm.active {
  transform: rotate(38deg) translateX(-12px);
}

.tonearm-head {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 26px;
  height: 24px;
  border-radius: 8px;
  background: #25231f;
}

.player-meta {
  margin-top: 24px;
}

.player-kicker {
  margin: 0 0 10px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.12em;
}

.player-meta h2 {
  margin: 0;
  color: #25231f;
  font-size: 30px;
  line-height: 1.2;
}

.player-subtitle {
  margin: 10px 0 0;
  color: #7b6a4a;
  font-size: 15px;
}

.progress-block {
  margin-top: 22px;
}

.time-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  color: #9d8656;
  font-size: 13px;
  font-weight: 800;
}

.progress-range {
  width: 100%;
  height: 8px;
  appearance: none;
  border-radius: 999px;
  background: #eadfca;
  cursor: pointer;
  outline: none;
}

.progress-range:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.progress-range::-webkit-slider-thumb {
  width: 18px;
  height: 18px;
  appearance: none;
  border: 4px solid #25231f;
  border-radius: 50%;
  background: #f6c534;
}

.progress-range::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border: 4px solid #25231f;
  border-radius: 50%;
  background: #f6c534;
}

.player-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.player-actions button {
  height: 46px;
  padding: 0 20px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  color: #594828;
  font-weight: 800;
  cursor: pointer;
}

.player-actions button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.player-actions .primary {
  border-color: #f6c534;
  background: #f6c534;
  color: #25231f;
}

.player-meta audio {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 500px) {
  .turntable-shell {
    padding: 18px;
  }

  .turntable-top {
    min-height: 330px;
  }

  .tonearm {
    top: 38px;
    right: 24px;
    width: 120px;
  }

  .record-label {
    width: 110px;
    height: 110px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .record.spinning {
    animation: none;
  }
}
</style>
