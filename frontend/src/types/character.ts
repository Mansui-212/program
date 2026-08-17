export interface Character {
  id: number
  slug: string
  name: string
  aliases: string | null
  description: string | null
  avatar_url: string | null
  theme_color: string | null
  sort_order: number
  is_featured: boolean
  created_at: string
  updated_at: string
}

export interface CharacterTimelineEvent {
  date: string
  title: string
  content: string
}

export interface CharacterDetail extends Character {
  avatar_large_url: string | null
  origin_story: string | null
  timeline: CharacterTimelineEvent[] | null
}
