import http from '@/api/http'

import type { AdminOverview, AdminSubmission, AdminUser, HakiRecord } from '@/types/admin'
import type { ChronicleEvent, ChronicleEventPayload } from '@/types/chronicle'

export interface GetAdminSubmissionsParams {
  submission_type?: 'meme' | 'music'
  status?: 'approved' | 'pending' | 'rejected'
  limit?: number
  offset?: number
}

export function getAdminOverview() {
  return http.get<AdminOverview>('/v1/admin/overview')
}

export function getAdminSubmissions(params: GetAdminSubmissionsParams = {}) {
  return http.get<AdminSubmission[]>('/v1/admin/submissions', { params })
}

export function deleteAdminMeme(contentId: number) {
  return http.delete(`/v1/admin/contents/memes/${contentId}`)
}

export function deleteAdminMusicTrack(contentId: number) {
  return http.delete(`/v1/admin/contents/music-tracks/${contentId}`)
}

export function updateAdminContentFeatured(
  contentType: 'meme' | 'music',
  contentId: number,
  isFeatured: boolean,
) {
  return http.put(`/v1/admin/contents/${contentType}/${contentId}/featured`, {
    is_featured: isFeatured,
  })
}

export function getAdminUsers(keyword?: string) {
  return http.get<AdminUser[]>('/v1/admin/users', {
    params: keyword ? { keyword } : undefined,
  })
}

export function adjustAdminUserHaki(userId: number, changeValue: number, reason: string) {
  return http.post<AdminUser>(`/v1/admin/users/${userId}/haki`, {
    change_value: changeValue,
    reason,
  })
}

export function getAdminUserHakiRecords(userId: number) {
  return http.get<HakiRecord[]>(`/v1/admin/users/${userId}/haki-records`)
}

export function getAdminChronicleEvents() {
  return http.get<ChronicleEvent[]>('/v1/admin/chronicle')
}

export function createAdminChronicleEvent(payload: ChronicleEventPayload) {
  return http.post<ChronicleEvent>('/v1/admin/chronicle', payload)
}

export function updateAdminChronicleEvent(eventId: number, payload: ChronicleEventPayload) {
  return http.put<ChronicleEvent>(`/v1/admin/chronicle/${eventId}`, payload)
}

export function deleteAdminChronicleEvent(eventId: number) {
  return http.delete(`/v1/admin/chronicle/${eventId}`)
}
