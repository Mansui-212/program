import http from '@/api/http'

import type { Submission } from '@/types/submission'

export interface CreateSubmissionPayload {
  submission_type: 'meme' | 'music'
  title: string
  description?: string
  character_ids?: number[]
  source_name?: string
  source_url?: string
  author_name?: string
  file: File
}

export function createSubmission(payload: CreateSubmissionPayload) {
  const formData = new FormData()

  formData.append('submission_type', payload.submission_type)
  formData.append('title', payload.title)

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

  formData.append('file', payload.file)

  return http.post<Submission>('/v1/submissions', formData)
}

export function getMySubmissions(status?: Submission['status']) {
  return http.get<Submission[]>('/v1/submissions/me', {
    params: status ? { status } : undefined,
  })
}
