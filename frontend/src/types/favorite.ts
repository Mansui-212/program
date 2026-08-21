export type FavoriteTargetType = 'meme' | 'music'

export interface Favorite {
  id: number
  target_type: FavoriteTargetType
  target_id: number
  title: string
  description: string | null
  image_url: string | null
  audio_url: string | null
  cover_url: string | null
  author_name: string | null
  created_at: string
}

export interface FavoriteStatus {
  target_type: FavoriteTargetType
  target_id: number
  is_favorited: boolean
}
