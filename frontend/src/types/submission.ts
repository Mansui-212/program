export interface Submission {
  id: number
  user_id: number
  submission_type: 'meme' | 'music'
  status: 'pending' | 'approved' | 'rejected'
  title: string
  description: string | null
  file_url: string
  source_type: 'upload' | 'video_upload' | 'douyin'
  content_id: number | null
  content_deleted: boolean
  content_is_featured?: boolean
  cover_url: string | null
  character_id: number | null
  character_ids: number[]
  source_name: string | null
  source_url: string | null
  source_author: string | null
  author_name: string | null
  author_uid: string | null
  reject_reason: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}
