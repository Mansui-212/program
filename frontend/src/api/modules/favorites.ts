import http from '@/api/http'

import type { Favorite, FavoriteStatus, FavoriteTargetType } from '@/types/favorite'

export function getMyFavorites() {
  return http.get<Favorite[]>('/v1/favorites/me')
}

export function getFavoriteStatus(targetType: FavoriteTargetType, targetId: number) {
  return http.get<FavoriteStatus>(`/v1/favorites/me/${targetType}/${targetId}`)
}

export function createFavorite(targetType: FavoriteTargetType, targetId: number) {
  return http.post<FavoriteStatus>('/v1/favorites', {
    target_type: targetType,
    target_id: targetId,
  })
}

export function deleteFavorite(targetType: FavoriteTargetType, targetId: number) {
  return http.delete(`/v1/favorites/${targetType}/${targetId}`)
}

export function recordDownload(targetType: FavoriteTargetType, targetId: number) {
  return http.post('/v1/engagements/downloads', {
    target_type: targetType,
    target_id: targetId,
  })
}
