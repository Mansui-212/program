import http from '@/api/http'

import type { Character, CharacterDetail } from '@/types/character'
import type { Meme } from '@/types/meme'
import type { MusicTrack } from '@/types/musicTrack'

export function getFeaturedCharacters() {
  return http.get<Character[]>('/v1/characters/featured')
}

export function getCharacterDetail(slug: string) {
  return http.get<CharacterDetail>(`/v1/characters/${slug}`)
}

export function getCharacterMemes(characterId: number) {
  return http.get<Meme[]>(`/v1/characters/${characterId}/memes`)
}

export function getCharacterMusic(characterId: number) {
  return http.get<MusicTrack[]>(`/v1/characters/${characterId}/music`)
}
