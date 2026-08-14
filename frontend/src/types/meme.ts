export interface Meme {
  id: number
  slug: string
  title: string
  description: string | null
  image_url: string
  file_type: string
  character_id: number | null
  source_name: string | null
  source_url: string | null
  author_name: string | null
  view_count: number
  download_count: number
  sort_order: number
  is_featured: boolean
  created_at: string
  updated_at: string
}
