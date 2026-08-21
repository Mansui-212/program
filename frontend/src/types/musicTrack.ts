export interface MusicTrack {
  id: number
  slug: string
  title: string
  description: string | null
  audio_url: string
  cover_url: string | null
  duration_seconds: number | null
  character_id: number | null
  character_ids: number[]
  original_title: string | null
  source_type: 'upload' | 'video_upload' | 'douyin'
  source_name: string | null
  source_url: string | null
  source_author: string | null
  author_name: string | null
  author_id: number | null
  author_uid: string | null
  play_count: number
  sort_order: number
  is_featured: boolean
  created_at: string
  updated_at: string
}

export interface MusicTrackCharacter {
  id: number
  slug: string
  name: string
  avatar_url: string | null
  theme_color: string | null
}

export interface MusicTrackDetail extends MusicTrack {
  character: MusicTrackCharacter | null
}
