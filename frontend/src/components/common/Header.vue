<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import stationLogo from '../../../../logo.jpg'
import { useAuthStore } from '@/stores/auth'
import { formatUid } from '@/utils/formatUid'

defineOptions({
  name: 'SiteHeader',
})

const route = useRoute()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)
const defaultAvatar = '/static/images/avatars/maodie.jpg'

function closeMenu() {
  mobileMenuOpen.value = false
}

function logout() {
  authStore.logout()
  closeMenu()
}

watch(
  () => route.fullPath,
  () => closeMenu(),
)
</script>

<template>
  <header class="site-header">
    <div class="header-bar">
      <RouterLink class="station-brand" to="/" aria-label="基米小站首页" @click="closeMenu">
        <span class="brand-avatar" aria-hidden="true">
          <img :src="stationLogo" alt="" />
        </span>
        <span class="brand-copy">
          <strong>基米小站</strong>
          <small>正经做收录，抽象做内容</small>
        </span>
      </RouterLink>

      <nav class="desktop-nav" aria-label="主导航">
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/characters">角色档案</RouterLink>
        <RouterLink to="/memes">表情包</RouterLink>
        <RouterLink to="/music">音乐</RouterLink>
        <RouterLink to="/chronicle">编年史</RouterLink>
        <RouterLink to="/haki">哈气榜</RouterLink>
        <RouterLink to="/search">搜索</RouterLink>
      </nav>

      <div class="header-actions">
        <RouterLink class="submit-link" to="/submit">投稿</RouterLink>

        <template v-if="authStore.isLoggedIn && authStore.user">
          <RouterLink v-if="authStore.user.role === 'admin'" class="admin-link" to="/admin">管理后台</RouterLink>
          <RouterLink
            class="profile-link"
            to="/profile"
            aria-label="进入个人中心"
          >
            <img
              class="user-avatar"
              :src="authStore.user.avatar_url || defaultAvatar"
              :alt="authStore.user.username"
            />
            <span>
              <strong>{{ authStore.user.username }}</strong>
              <small>UID {{ formatUid(authStore.user.id) }} · 哈气值 {{ authStore.user.haki_value }}</small>
            </span>
          </RouterLink>
          <button type="button" class="logout-button" @click="logout">退出</button>
        </template>

        <template v-else>
          <RouterLink class="login-link" to="/login">登录</RouterLink>
          <RouterLink class="register-link" to="/register">注册</RouterLink>
        </template>
      </div>

      <button
        type="button"
        class="menu-toggle"
        :class="{ active: mobileMenuOpen }"
        :aria-expanded="mobileMenuOpen"
        aria-controls="mobile-navigation"
        :aria-label="mobileMenuOpen ? '关闭菜单' : '打开菜单'"
        @click="mobileMenuOpen = !mobileMenuOpen"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>

    <Transition name="mobile-menu">
      <nav v-if="mobileMenuOpen" id="mobile-navigation" class="mobile-nav" aria-label="移动端主导航">
        <RouterLink to="/" @click="closeMenu">首页</RouterLink>
        <RouterLink to="/characters" @click="closeMenu">角色档案</RouterLink>
        <RouterLink to="/memes" @click="closeMenu">表情包档案</RouterLink>
        <RouterLink to="/music" @click="closeMenu">哈基米音乐</RouterLink>
        <RouterLink to="/chronicle" @click="closeMenu">编年史</RouterLink>
        <RouterLink to="/haki" @click="closeMenu">哈气排行榜</RouterLink>
        <RouterLink to="/search" @click="closeMenu">搜索</RouterLink>
        <RouterLink to="/submit" @click="closeMenu">投稿</RouterLink>

        <div class="mobile-account">
          <template v-if="authStore.isLoggedIn && authStore.user">
            <RouterLink v-if="authStore.user.role === 'admin'" to="/admin" @click="closeMenu">⚙ 管理后台</RouterLink>
            <RouterLink to="/profile" @click="closeMenu">
              <img :src="authStore.user.avatar_url || defaultAvatar" :alt="authStore.user.username" />
              <span>
                <strong>{{ authStore.user.username }}</strong>
                <small>UID {{ formatUid(authStore.user.id) }} · 哈气值 {{ authStore.user.haki_value }}</small>
              </span>
            </RouterLink>
            <button type="button" @click="logout">退出登录</button>
          </template>
          <template v-else>
            <RouterLink to="/login" @click="closeMenu">登录</RouterLink>
            <RouterLink to="/register" @click="closeMenu">注册账号</RouterLink>
          </template>
        </div>
      </nav>
    </Transition>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 18px;
  z-index: 1000;
  width: min(1400px, calc(100% - 48px));
  margin: 18px auto 0;
}

.header-bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: clamp(18px, 3vw, 42px);
  min-height: 74px;
  padding: 10px 14px 10px 12px;
  border: 1px solid rgba(246, 197, 52, 0.45);
  border-radius: 24px;
  background: rgba(255, 253, 247, 0.76);
  box-shadow: 0 16px 38px rgba(95, 76, 39, 0.11);
  backdrop-filter: blur(16px) saturate(1.12);
}

.station-brand,
.desktop-nav a,
.header-actions a,
.mobile-nav a {
  color: inherit;
  text-decoration: none;
}

.station-brand {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  color: #2d2a23;
}

.brand-avatar {
  display: grid;
  width: 48px;
  height: 48px;
  flex: 0 0 48px;
  overflow: hidden;
  border: 3px solid #f6c534;
  border-radius: 50%;
  background: #ffe9aa;
  box-shadow: 0 4px 0 #e6b52c, 0 7px 18px rgba(135, 92, 24, 0.16);
}

.brand-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 22% 58%;
  filter: saturate(1.05) contrast(1.02);
  transform: scale(1.22);
}

.brand-copy {
  display: grid;
  gap: 2px;
  line-height: 1.1;
}

.brand-copy strong {
  font-size: 18px;
  font-weight: 900;
  letter-spacing: -0.06em;
}

.brand-copy small {
  color: #887b63;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.desktop-nav {
  display: flex;
  justify-content: center;
  gap: clamp(14px, 2.1vw, 31px);
}

.desktop-nav a {
  position: relative;
  color: #6a6254;
  font-size: 14px;
  font-weight: 800;
  white-space: nowrap;
}

.desktop-nav a::after {
  position: absolute;
  right: 12%;
  bottom: -8px;
  left: 12%;
  height: 3px;
  border-radius: 99px;
  background: #f6c534;
  content: '';
  opacity: 0;
  transform: scaleX(0.4);
  transition: 0.2s ease;
}

.desktop-nav a:hover,
.desktop-nav .router-link-active {
  color: #473716;
}

.desktop-nav a:hover::after,
.desktop-nav .router-link-active::after {
  opacity: 1;
  transform: scaleX(1);
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 9px;
}

.submit-link,
.admin-link,
.login-link,
.register-link,
.logout-button {
  min-height: 40px;
  border: 1px solid #eadfca;
  border-radius: 999px;
  padding: 0 14px;
  background: rgba(255, 253, 247, 0.82);
  color: #5b4a2d !important;
  font: inherit;
  font-size: 13px;
  font-weight: 850;
  line-height: 38px;
  white-space: nowrap;
}

.submit-link {
  border-color: #f4c63c;
  background: #f6c534;
  color: #3d321a !important;
}

.register-link {
  display: none;
}

.profile-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border: 1px solid rgba(238, 215, 153, 0.72);
  border-radius: 999px;
  background: rgba(255, 244, 202, 0.74);
}

.user-avatar {
  width: 34px;
  height: 34px;
  border: 2px solid #f6c534;
  border-radius: 50%;
  object-fit: cover;
}

.profile-link span {
  display: grid;
  gap: 1px;
  line-height: 1.15;
}

.profile-link strong {
  overflow: hidden;
  max-width: 104px;
  color: #4c3d25;
  font-size: 12px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.profile-link small {
  color: #857047;
  font-size: 10px;
  font-weight: 750;
  white-space: nowrap;
}

.logout-button {
  cursor: pointer;
}

.menu-toggle,
.mobile-nav {
  display: none;
}

@media (max-width: 1120px) {
  .brand-copy small,
  .profile-link small,
  .logout-button {
    display: none;
  }
}

@media (max-width: 860px) {
  .site-header {
    top: 12px;
    width: calc(100% - 32px);
    margin-top: 12px;
  }

  .header-bar {
    grid-template-columns: 1fr auto;
    min-height: 66px;
    padding: 8px 10px 8px 11px;
    border-radius: 21px;
  }

  .desktop-nav,
  .header-actions {
    display: none;
  }

  .brand-avatar {
    width: 44px;
    height: 44px;
    flex-basis: 44px;
  }

  .menu-toggle {
    display: grid;
    width: 43px;
    height: 43px;
    place-content: center;
    gap: 5px;
    border: 1px solid #eadfca;
    border-radius: 15px;
    background: rgba(255, 253, 247, 0.76);
  }

  .menu-toggle span {
    display: block;
    width: 19px;
    height: 2px;
    border-radius: 99px;
    background: #55472d;
    transition: transform 0.2s ease, opacity 0.2s ease;
  }

  .menu-toggle.active span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
  .menu-toggle.active span:nth-child(2) { opacity: 0; }
  .menu-toggle.active span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

  .mobile-nav {
    display: grid;
    gap: 4px;
    margin-top: 10px;
    padding: 12px;
    border: 1px solid rgba(246, 197, 52, 0.42);
    border-radius: 21px;
    background: rgba(255, 253, 247, 0.92);
    box-shadow: 0 16px 38px rgba(95, 76, 39, 0.14);
    backdrop-filter: blur(16px);
  }

  .mobile-nav > a,
  .mobile-account > a,
  .mobile-account button {
    display: flex;
    align-items: center;
    gap: 10px;
    border: 0;
    border-radius: 13px;
    padding: 12px 14px;
    background: transparent;
    color: #514631;
    font: inherit;
    font-size: 15px;
    font-weight: 850;
    text-align: left;
  }

  .mobile-nav > a:hover,
  .mobile-nav > .router-link-active,
  .mobile-account > a,
  .mobile-account button {
    background: #fff0b2;
  }

  .mobile-account {
    display: grid;
    gap: 7px;
    margin-top: 6px;
    border-top: 1px solid #eee1c9;
    padding-top: 12px;
  }

  .mobile-account img {
    width: 34px;
    height: 34px;
    border: 2px solid #f6c534;
    border-radius: 50%;
    object-fit: cover;
  }

  .mobile-account span {
    display: grid;
    gap: 2px;
  }

  .mobile-account small {
    color: #876f45;
    font-size: 11px;
  }
}

.mobile-menu-enter-active,
.mobile-menu-leave-active { transition: all 0.2s ease; }
.mobile-menu-enter-from,
.mobile-menu-leave-to { opacity: 0; transform: translateY(-8px); }
</style>
