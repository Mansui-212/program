import http from '@/api/http'

import type { User } from '@/types/user'

export function uploadMyAvatar(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  return http.post<User>('/v1/users/me/avatar', formData)
}
