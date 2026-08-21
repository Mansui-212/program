import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MemesView from '../views/MemesView.vue'
import MusicView from '@/views/MusicView.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/characters',
      name: 'characters',
      component: () => import('@/views/CharactersView.vue'),
    },

    {
      path: '/users/:uid/submissions',
      name: 'user-submissions',
      component: () => import('@/views/UserSubmissionsView.vue'),
    },
    {
      path: '/users/:uid',
      name: 'user-profile',
      component: () => import('@/views/UserProfileView.vue'),
    },

    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/memes',
      name: 'memes',
      component: MemesView,
    },
    {
      path: '/music',
      name: 'music',
      component: MusicView,
    },
    {
      path: '/character/:slug',
      name: 'character-detail',
      component: () => import('@/views/CharacterDetail.vue'),
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
    },
    {
      path: '/chronicle',
      name: 'chronicle',
      component: () => import('@/views/ChronicleView.vue'),
    },
    {
      path: '/haki',
      name: 'haki-ranking',
      component: () => import('@/views/HakiRankView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
    },
    {
      path: '/profile/submissions',
      name: 'my-submissions',
      component: () => import('@/views/MySubmissionsView.vue'),
    },
    {
      path: '/submit',
      name: 'submit',
      component: () => import('@/views/SubmitView.vue'),
    },
    {
      path: '/admin',
      name: 'admin-home',
      component: () => import('@/views/admin/AdminHome.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/admin/submissions',
      name: 'admin-submissions',
      component: () => import('@/views/admin/AdminSubmissions.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/admin/memes/batch',
      name: 'admin-meme-batch-upload',
      component: () => import('@/views/admin/AdminMemeBatchUpload.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/admin/users',
      name: 'admin-users',
      component: () => import('@/views/admin/AdminUsers.vue'),
      meta: { requiresAdmin: true },
    },
    {
      path: '/admin/chronicle',
      name: 'admin-chronicle',
      component: () => import('@/views/admin/AdminChronicle.vue'),
      meta: { requiresAdmin: true },
    },
  ],
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAdmin) return true

  const authStore = useAuthStore()

  if (authStore.token && !authStore.user) {
    await authStore.fetchMe()
  }

  if (authStore.user?.role === 'admin') return true

  return { name: 'home' }
})

export default router
