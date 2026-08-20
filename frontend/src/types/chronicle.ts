export interface ChronicleEvent {
  id: number
  year: number
  date: string | null
  title: string
  content: string
  image_url: string | null
  sort_order: number
  created_at: string
}

export interface ChronicleEventPayload {
  year: number
  date?: string | null
  title: string
  content: string
  image_url?: string | null
  sort_order?: number
}
