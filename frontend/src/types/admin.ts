import type { Submission } from '@/types/submission'

export interface AdminUser {
  id: number
  username: string
  avatar_url: string | null
  haki_value: number
  role: string
  created_at: string
}

export interface AdminSubmission extends Submission {
  user: AdminUser
}

export interface HakiRecord {
  id: number
  user_id: number
  change_value: number
  reason: string
  action: string | null
  target_type: string | null
  target_id: number | null
  source_user_id: number | null
  created_at: string
}

export interface AdminOverview {
  total_uploads: number
  published_contents: number
  user_count: number
  total_haki_value: number
}

export type ContentStatus = 'active' | 'withdrawn' | 'removed'

export type BatchMemeUploadStatus = 'imported' | 'duplicate' | 'invalid'

export interface BatchMemeUploadItem {
  filename: string
  status: BatchMemeUploadStatus
  title: string | null
  detail: string | null
}

export interface BatchMemeUploadResult {
  total_candidates: number
  imported: number
  skipped_duplicates: number
  skipped_invalid: number
  haki_gained: number
  items: BatchMemeUploadItem[]
}
