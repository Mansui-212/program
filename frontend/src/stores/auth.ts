import { defineStore } from 'pinia'

import { getMe, login as loginRequest, register as registerRequest } from '@/api/modules/auth'

import type { LoginPayload, RegisterPayload } from '@/api/modules/auth'
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('hakimi_token') || '',
    user: null as User | null,
    loading: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && !!state.user,
  },

  actions: {
    async register(payload: RegisterPayload) {
      const response = await registerRequest(payload)

      this.token = response.data.access_token
      this.user = response.data.user

      localStorage.setItem('hakimi_token', this.token)
    },

    async login(payload: LoginPayload) {
      const response = await loginRequest(payload)

      this.token = response.data.access_token
      this.user = response.data.user

      localStorage.setItem('hakimi_token', this.token)
    },

    async fetchMe() {
      if (!this.token) return

      this.loading = true

      try {
        const response = await getMe()
        this.user = response.data
      } catch (error) {
        console.error('获取当前用户失败', error)
        this.logout()
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('hakimi_token')
    },
  },
})
