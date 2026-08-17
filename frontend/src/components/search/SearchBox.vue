<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'search'): void
}>()

const keyword = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value),
})

function submitSearch() {
  emit('search')
}
</script>

<template>
  <form class="search-box" role="search" @submit.prevent="submitSearch">
    <label class="sr-only" for="site-search-input">搜索基米小站</label>
    <input
      id="site-search-input"
      v-model="keyword"
      type="search"
      placeholder="搜索角色、表情包或音乐，例如：耄耋、曼波音乐"
      autocomplete="off"
    />
    <button type="submit">搜索 <span aria-hidden="true">⌕</span></button>
  </form>
</template>

<style scoped>
.search-box {
  display: flex;
  gap: 12px;
  padding: 9px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: #fffdf7;
  box-shadow: 0 10px 28px rgba(91, 72, 39, 0.07);
}

.search-box input {
  min-width: 0;
  height: 48px;
  flex: 1;
  padding: 0 16px;
  border: 0;
  outline: 0;
  background: transparent;
  color: #25231f;
  font: inherit;
}

.search-box input::placeholder {
  color: #a59475;
}

.search-box button {
  height: 48px;
  padding: 0 22px;
  border: 0;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  cursor: pointer;
}

.search-box button span {
  margin-left: 4px;
  font-size: 20px;
  line-height: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 560px) {
  .search-box {
    flex-direction: column;
    border-radius: 24px;
  }

  .search-box input {
    width: 100%;
  }
}
</style>
