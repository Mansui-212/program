<script setup lang="ts">
import { computed } from 'vue'

import { formatUid } from '@/utils/formatUid'

const props = defineProps<{
  uid: string | number | null | undefined
  name: string | null | undefined
}>()

const profilePath = computed(() => {
  const id = Number(props.uid)

  if (!Number.isSafeInteger(id) || id < 1) {
    return null
  }

  return `/users/${formatUid(id)}`
})
</script>

<template>
  <RouterLink
    v-if="profilePath && name"
    class="user-link"
    :to="profilePath"
    @click.stop
  >
    {{ name }}
  </RouterLink>
  <span v-else>{{ name || '未知作者' }}</span>
</template>

<style scoped>
.user-link {
  color: #9a7512;
  font: inherit;
  font-weight: 900;
  text-decoration: none;
}

.user-link:hover {
  color: #5d4515;
  text-decoration: underline;
}
</style>
