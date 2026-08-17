import type { CharacterDetail } from '@/types/character'
import type { Meme } from '@/types/meme'
import type { MusicTrack } from '@/types/musicTrack'

export type SearchPrimaryType = 'characters' | 'memes' | 'music' | 'none'

export interface SearchResult {
  keyword: string
  primary_type: SearchPrimaryType
  characters: CharacterDetail[]
  memes: Meme[]
  music: MusicTrack[]
}
