import http from '@/api/http'

import type { HakiRankingUser, PublicSubmission, PublicUser, User } from '@/types/user'

export function uploadMyAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return http.post<User>('/v1/users/me/avatar', formData)
}

export function getPublicUser(uid: string) {
  return http.get<PublicUser>(`/v1/users/${uid}`)
}

export function getPublicUserSubmissions(uid: string) {
  return http.get<PublicSubmission[]>(`/v1/users/${uid}/submissions`)
}

export function getHakiRanking(limit = 50) {
  return http.get<HakiRankingUser[]>('/v1/users/ranking', { params: { limit } })
}
