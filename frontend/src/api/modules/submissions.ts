import http from '@/api/http'

import type { Submission } from '@/types/submission'

export interface CreateSubmissionPayload {
  submission_type: 'meme' | 'music'
  title: string
  description?: string
  character_ids?: number[]
  source_type?: 'upload' | 'video_upload'
  source_name?: string
  source_url?: string
  author_name?: string
  rights_confirmed?: boolean
  file?: File
}

export interface UpdateSubmissionPayload {
  title: string
  description?: string | null
  character_ids?: number[]
  source_name?: string | null
  source_url?: string | null
  source_author?: string | null
}

export function createSubmission(payload: CreateSubmissionPayload) {
  const formData = new FormData()

  formData.append('submission_type', payload.submission_type)
  formData.append('title', payload.title)

  if (payload.source_type) {
    formData.append('source_type', payload.source_type)
  }

  if (payload.description) {
    formData.append('description', payload.description)
  }

  for (const characterId of payload.character_ids || []) {
    formData.append('character_ids', String(characterId))
  }

  if (payload.source_name) {
    formData.append('source_name', payload.source_name)
  }

  if (payload.source_url) {
    formData.append('source_url', payload.source_url)
  }

  if (payload.author_name) {
    formData.append('author_name', payload.author_name)
  }

  if (payload.rights_confirmed) {
    formData.append('rights_confirmed', 'true')
  }

  if (payload.file) {
    formData.append('file', payload.file)
  }

  return http.post<Submission>('/v1/submissions', formData)
}

export function getMySubmissions(status?: Submission['status']) {
  return http.get<Submission[]>('/v1/submissions/me', {
    params: status ? { status } : undefined,
  })
}

export function updateMySubmission(
  submissionId: number,
  payload: UpdateSubmissionPayload,
) {
  return http.put<Submission>(`/v1/submissions/${submissionId}`, payload)
}
