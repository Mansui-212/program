import http from '@/api/http'

import type { AuthResponse, User } from '@/types/user'

export interface RegisterPayload {
  username: string
  password: string
}

export interface LoginPayload {
  username: string
  password: string
}

export function register(payload: RegisterPayload) {
  return http.post<AuthResponse>('/v1/auth/register', payload)
}

export function login(payload: LoginPayload) {
  return http.post<AuthResponse>('/v1/auth/login', payload)
}

export function getMe() {
  return http.get<User>('/v1/auth/me')
}
