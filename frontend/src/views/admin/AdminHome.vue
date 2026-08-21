<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getAdminOverview } from '@/api/modules/admin'

import type { AdminOverview } from '@/types/admin'

const overview = ref<AdminOverview | null>(null)
const error = ref('')

async function loadOverview() {
  error.value = ''

  try {
    const response = await getAdminOverview()
    overview.value = response.data
  } catch (reason) {
    console.error('加载管理中心概览失败', reason)
    error.value = '管理数据暂时无法加载。'
  }
}

onMounted(() => {
  void loadOverview()
})
</script>

<template>
  <main class="admin-page">
    <section class="admin-hero">
      <p class="section-kicker">HAKIMI ADMIN</p>
      <h1>基米管理中心</h1>
      <p>发布内容会立即进入档案库；在这里可以查看全站发布记录、下架不相关内容，并维护哈气值。</p>
    </section>

    <p v-if="error" class="status-message error-message">{{ error }}</p>

    <section class="stat-grid" aria-label="管理数据概览">
      <article class="stat-card yellow">
        <span>累计上传</span>
        <strong>{{ overview?.total_uploads ?? '—' }}</strong>
      </article>
      <article class="stat-card pink">
        <span>正式内容</span>
        <strong>{{ overview?.published_contents ?? '—' }}</strong>
      </article>
      <article class="stat-card green">
        <span>小站用户</span>
        <strong>{{ overview?.user_count ?? '—' }}</strong>
      </article>
      <article class="stat-card purple">
        <span>总哈气值</span>
        <strong>{{ overview?.total_haki_value ?? '—' }}</strong>
      </article>
    </section>

    <section class="admin-actions">
      <RouterLink to="/admin/submissions">
        <span>🗂</span>
        <div>
          <h2>内容管理</h2>
          <p>查看用户发布的图片与音乐，下架不相关内容。</p>
        </div>
        <b>→</b>
      </RouterLink>
      <RouterLink to="/admin/memes/batch">
        <span>▦</span>
        <div>
          <h2>表情包批量导入</h2>
          <p>上传图片或 ZIP，一次收录同一角色的表情包素材。</p>
        </div>
        <b>→</b>
      </RouterLink>
      <RouterLink to="/admin/users">
        <span>✦</span>
        <div>
          <h2>用户与哈气值</h2>
          <p>查看小站居民，调整哈气值并追踪每次变动。</p>
        </div>
        <b>→</b>
      </RouterLink>
      <RouterLink to="/admin/chronicle">
        <span>⌁</span>
        <div>
          <h2>编年史编辑台</h2>
          <p>添加或整理历史节点，公开时间轴会自动更新。</p>
        </div>
        <b>→</b>
      </RouterLink>
    </section>
  </main>
</template>

<style scoped>
.admin-page {
  width: min(1160px, calc(100% - 48px));
  margin: 0 auto;
  padding: 52px 0 120px;
}

.admin-hero {
  padding: clamp(34px, 6vw, 68px);
  border-radius: 40px;
  background: linear-gradient(135deg, #fff4c8, #ffe4ed 56%, #f3eaff);
  box-shadow: 0 24px 60px rgba(79, 61, 32, 0.1);
}

.section-kicker {
  margin: 0 0 12px;
  color: #b88a12;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.13em;
}

.admin-hero h1 {
  margin: 0;
  color: #25231f;
  font-size: clamp(42px, 6vw, 66px);
  letter-spacing: -0.06em;
}

.admin-hero > p:not(.section-kicker) {
  max-width: 640px;
  margin: 20px 0 0;
  color: #6f6047;
  line-height: 1.8;
}

.status-message {
  margin: 22px 0 0;
  color: #7b6a4a;
  font-weight: 800;
}

.error-message {
  color: #bd4747;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-top: 30px;
}

.stat-card {
  min-height: 156px;
  padding: 25px;
  border-radius: 28px;
  box-shadow: 0 16px 34px rgba(79, 61, 32, 0.08);
}

.stat-card span {
  display: block;
  color: #705c37;
  font-size: 14px;
  font-weight: 800;
}

.stat-card strong {
  display: block;
  margin-top: 20px;
  color: #25231f;
  font-size: 44px;
  line-height: 1;
}

.yellow {
  background: #fff0b8;
}
.pink {
  background: #ffdfe9;
}
.green {
  background: #dff3dd;
}
.purple {
  background: #e9e0ff;
}

.admin-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 22px;
  margin-top: 28px;
}

.admin-actions a {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 28px;
  border: 1px solid #eadfca;
  border-radius: 28px;
  background: #fffaf0;
  color: inherit;
  text-decoration: none;
  box-shadow: 0 16px 34px rgba(79, 61, 32, 0.08);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.admin-actions a:hover {
  transform: translateY(-4px);
  box-shadow: 0 22px 42px rgba(79, 61, 32, 0.12);
}

.admin-actions a > span {
  display: grid;
  width: 52px;
  height: 52px;
  place-items: center;
  border-radius: 18px;
  background: #fff0b8;
  font-size: 25px;
}

.admin-actions h2 {
  margin: 0;
  color: #25231f;
  font-size: 21px;
}

.admin-actions p {
  margin: 8px 0 0;
  color: #7b6a4a;
  font-size: 14px;
  line-height: 1.6;
}

.admin-actions b {
  color: #9a7512;
  font-size: 22px;
}

@media (max-width: 820px) {
  .stat-grid,
  .admin-actions {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .admin-page {
    width: min(100% - 32px, 1160px);
    padding-top: 30px;
  }

  .stat-grid,
  .admin-actions {
    grid-template-columns: 1fr;
  }
}
</style>
