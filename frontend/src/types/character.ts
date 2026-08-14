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
