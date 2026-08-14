import http from '@/api/http'

import type { Character } from '@/types/character'

export function getFeaturedCharacters() {
  return http.get<Character[]>('/v1/characters/featured')
}
