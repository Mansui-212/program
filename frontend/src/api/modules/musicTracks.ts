import http from '@/api/http'

import type { MusicTrack, MusicTrackDetail } from '@/types/musicTrack'

export interface GetMusicTracksParams {
  limit?: number
  offset?: number
  keyword?: string
  order?: 'latest' | 'featured' | 'popular'
}

export function getMusicTracks(params: GetMusicTracksParams = {}) {
  return http.get<MusicTrack[]>('/v1/music-tracks', {
    params,
  })
}

export function getLatestMusicTracks(limit = 8) {
  return http.get<MusicTrack[]>('/v1/music-tracks/latest', {
    params: {
      limit,
    },
  })
}

export function getFeaturedMusicTracks(limit = 8) {
  return http.get<MusicTrack[]>('/v1/music-tracks/featured', {
    params: {
      limit,
    },
  })
}

export function getMusicTrackDetail(slug: string) {
  return http.get<MusicTrackDetail>(`/v1/music-tracks/${slug}`)
}

export function withdrawMusicTrack(trackId: number) {
  return http.delete(`/v1/music-tracks/${trackId}/withdraw`)
}
