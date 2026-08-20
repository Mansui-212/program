<script setup lang="ts">
defineOptions({
  name: 'SiteFooter',
})
</script>

<template>
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <strong>基米小站</strong>
        <span>认真收录每一份快乐</span>
      </div>

      <nav aria-label="页脚导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/memes">表情包档案</RouterLink>
        <RouterLink to="/music">哈基米音乐</RouterLink>
        <RouterLink to="/chronicle">编年史</RouterLink>
        <RouterLink to="/submit">投稿</RouterLink>
      </nav>

      <span class="copyright">© 2026 HAKIMI LITTLE STATION</span>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  width: min(1180px, calc(100% - 48px));
  margin: 0 auto;
  border-top: 1px solid #eee4d2;
  padding: 28px 0 42px;
}

.footer-inner { display: flex; align-items: center; justify-content: space-between; gap: 22px; }
.footer-brand { display: grid; gap: 4px; }
.footer-brand strong { color: #4b402d; font-size: 15px; font-weight: 900; }
.footer-brand span, .copyright { color: #9d917e; font-size: 12px; font-weight: 650; }
nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 16px; }
nav a { color: #77684d; font-size: 13px; font-weight: 750; text-decoration: none; }
nav a:hover { color: #af7e10; }

@media (max-width: 760px) {
  .site-footer { width: calc(100% - 32px); padding: 24px 0 34px; }
  .footer-inner { align-items: flex-start; flex-direction: column; }
  nav { justify-content: flex-start; }
}
</style>
