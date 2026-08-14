export interface Submission {
  id: number
  user_id: number
  submission_type: 'meme' | 'music'
  status: 'pending' | 'approved' | 'rejected'
  title: string
  description: string | null
  file_url: string
  cover_url: string | null
  character_id: number | null
  source_name: string | null
  source_url: string | null
  author_name: string | null
  reject_reason: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}
