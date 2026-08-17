<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import CharacterResult from '@/components/search/CharacterResult.vue'
import MemeResult from '@/components/search/MemeResult.vue'
import MusicResult from '@/components/search/MusicResult.vue'
import SearchBox from '@/components/search/SearchBox.vue'
import { searchSite } from '@/api/modules/search'

import type { SearchResult } from '@/types/search'

type SearchSection = 'characters' | 'memes' | 'music'

const route = useRoute()
const router = useRouter()

const keyword = ref('')
const result = ref<SearchResult | null>(null)
const loading = ref(false)
const error = ref('')
let latestRequest = 0

const popularSearches = ['耄耋', '鼠鼠', 'doro', '曼波']

const hasResults = computed(() => {
  if (!result.value) return false

  return result.value.characters.length > 0 || result.value.memes.length > 0 || result.value.music.length > 0
})

const orderedSections = computed<SearchSection[]>(() => {
  if (!result.value) return []

  const sections: SearchSection[] = ['characters', 'memes', 'music']
  const primary = result.value.primary_type

  if (primary !== 'none') {
    sections.splice(sections.indexOf(primary), 1)
    sections.unshift(primary)
  }

  return sections.filter((section) => result.value?.[section].length)
})

function getRouteKeyword() {
  const value = route.query.q
  return typeof value === 'string' ? value.trim() : ''
}

async function loadSearch(query: string) {
  const normalized = query.trim()
  const requestId = ++latestRequest

  result.value = null
  error.value = ''

  if (!normalized) {
    loading.value = false
    return
  }

  loading.value = true

  try {
    const response = await searchSite(normalized)

    if (requestId === latestRequest) {
      result.value = response.data
    }
  } catch (err) {
    console.error('搜索失败', err)

    if (requestId === latestRequest) {
      error.value = '搜索暂时不可用，请稍后再试。'
    }
  } finally {
    if (requestId === latestRequest) {
      loading.value = false
    }
  }
}

async function submitSearch() {
  const normalized = keyword.value.trim()

  if (!normalized) {
    await router.push({ name: 'search' })
    return
  }

  if (getRouteKeyword() === normalized) {
    await loadSearch(normalized)
    return
  }

  await router.push({ name: 'search', query: { q: normalized } })
}

function searchPopular(item: string) {
  keyword.value = item
  void submitSearch()
}

watch(
  () => route.query.q,
  () => {
    const routeKeyword = getRouteKeyword()
    keyword.value = routeKeyword
    void loadSearch(routeKeyword)
  },
  { immediate: true },
)
</script>

<template>
  <main class="search-page">
    <section class="search-hero">
      <p class="section-kicker">HAKIMI SEARCH</p>
      <h1>搜索基米小站</h1>
      <p>先找角色百科档案，再延伸到表情包与音乐收藏。</p>

      <SearchBox v-model="keyword" @search="submitSearch" />

      <div class="popular-searches" aria-label="热门搜索">
        <span>热门：</span>
        <button v-for="item in popularSearches" :key="item" type="button" @click="searchPopular(item)">
          {{ item }}
        </button>
      </div>
    </section>

    <section v-if="loading" class="status-panel">
      正在检索哈基米档案...
    </section>

    <section v-else-if="error" class="status-panel error-panel">
      {{ error }}
    </section>

    <template v-else-if="result">
      <section class="result-intro">
        <p>SEARCH RESULT</p>
        <h2>🔍 搜索：{{ result.keyword }}</h2>
        <span v-if="hasResults">优先为你展示{{ result.primary_type === 'characters' ? '角色档案' : result.primary_type === 'memes' ? '表情包' : '音乐' }}相关内容</span>
      </section>

      <section v-if="!hasResults" class="empty-panel">
        <div class="empty-icon">⌕</div>
        <h2>没有找到这个哈基米</h2>
        <p>也许它还没有被收录。欢迎投稿补充，让更多人找到这份快乐。</p>
        <RouterLink to="/submit">我要投稿 →</RouterLink>
      </section>

      <div v-else class="results-stack">
        <template v-for="section in orderedSections" :key="section">
          <CharacterResult v-if="section === 'characters'" :characters="result.characters" />
          <MemeResult v-else-if="section === 'memes'" :memes="result.memes" />
          <MusicResult v-else :music="result.music" />
        </template>
      </div>
    </template>

    <section v-else class="explore-panel">
      <p class="section-kicker">START EXPLORING</p>
      <h2>从一个熟悉的哈基米开始</h2>
      <p>试试搜索角色名、表情包标题或歌曲名。</p>
    </section>
  </main>
</template>

<style scoped>
.search-page {
  width: min(1200px, calc(100% - 48px));
  margin: 0 auto;
  padding: 52px 0 120px;
}

.search-hero {
  padding: clamp(32px, 6vw, 68px);
  border-radius: 40px;
  background:
    radial-gradient(circle at 88% 14%, rgba(255, 226, 235, 0.9) 0, transparent 28%),
    radial-gradient(circle at 8% 100%, rgba(255, 239, 178, 0.9) 0, transparent 30%),
    #fffaf0;
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.1);
}

.section-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
}

.search-hero h1 {
  margin: 0;
  color: #25231f;
  font-size: clamp(42px, 6vw, 68px);
  line-height: 1;
  letter-spacing: -0.06em;
}

.search-hero > p:not(.section-kicker) {
  margin: 20px 0 28px;
  color: #6f6047;
  font-size: 17px;
}

.popular-searches {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
  color: #8a7550;
  font-size: 14px;
  font-weight: 800;
}

.popular-searches button {
  padding: 7px 12px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  background: rgba(255, 253, 247, 0.78);
  color: #725c33;
  font: inherit;
  cursor: pointer;
}

.popular-searches button:hover {
  border-color: #f6c534;
  background: #fff4c5;
}

.status-panel,
.empty-panel,
.explore-panel {
  margin-top: 30px;
  padding: 42px;
  border-radius: 32px;
  background: #fffaf0;
  color: #7b6a4a;
  box-shadow: 0 18px 40px rgba(79, 61, 32, 0.08);
}

.error-panel {
  color: #b54646;
}

.result-intro {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
  margin: 38px 0 20px;
}

.result-intro p {
  margin: 0 0 9px;
  color: #b88a12;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.13em;
}

.result-intro h2 {
  margin: 0;
  color: #25231f;
  font-size: 30px;
}

.result-intro > span {
  color: #8a7550;
  font-size: 14px;
  font-weight: 700;
  text-align: right;
}

.results-stack {
  display: grid;
  gap: 24px;
}

.empty-panel {
  display: grid;
  justify-items: center;
  text-align: center;
}

.empty-icon {
  display: grid;
  width: 62px;
  height: 62px;
  place-items: center;
  border-radius: 50%;
  background: #fff0b8;
  color: #725c33;
  font-size: 34px;
}

.empty-panel h2,
.explore-panel h2 {
  margin: 18px 0 0;
  color: #25231f;
  font-size: 28px;
}

.empty-panel p,
.explore-panel p:not(.section-kicker) {
  max-width: 540px;
  margin: 12px 0 0;
  line-height: 1.7;
}

.empty-panel a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  margin-top: 22px;
  padding: 0 22px;
  border-radius: 999px;
  background: #f6c534;
  color: #25231f;
  font-weight: 900;
  text-decoration: none;
}

.explore-panel {
  margin-top: 30px;
}

@media (max-width: 620px) {
  .search-page {
    width: min(100% - 32px, 1200px);
    padding-top: 30px;
  }

  .result-intro {
    display: block;
  }

  .result-intro > span {
    display: block;
    margin-top: 12px;
    text-align: left;
  }

  .status-panel,
  .empty-panel,
  .explore-panel {
    padding: 30px 24px;
  }
}
</style>
