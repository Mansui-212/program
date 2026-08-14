import http from '@/api/http'

import type { Meme } from '@/types/meme'

export interface GetMemesParams {
  limit?: number
  offset?: number
  character_slug?: string
  keyword?: string
  order?: 'latest' | 'featured' | 'popular'
}

export function getMemes(params: GetMemesParams = {}) {
  return http.get<Meme[]>('/v1/memes', {
    params,
  })
}

export function getLatestMemes(limit = 8) {
  return http.get<Meme[]>('/v1/memes/latest', {
    params: {
      limit,
    },
  })
}

export function getFeaturedMemes(limit = 8) {
  return http.get<Meme[]>('/v1/memes/featured', {
    params: {
      limit,
    },
  })
}
