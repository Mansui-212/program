import http from '@/api/http'

import type { Meme } from '@/types/meme'

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
