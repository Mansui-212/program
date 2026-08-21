export interface User {
  id: number
  username: string
  avatar_url: string | null
  haki_value: number
  role: string
  created_at: string
  updated_at: string
}

export interface PublicUser {
  id: number
  uid: string
  username: string
  avatar_url: string | null
  haki_value: number
  created_at: string
  submission_count: number
}

export interface PublicSubmission {
  id: number
  submission_type: 'meme' | 'music'
  title: string
  description: string | null
  file_url: string
  cover_url: string | null
  content_id: number | null
  created_at: string
}

export interface HakiRankingUser {
  id: number
  uid: string
  username: string
  avatar_url: string | null
  haki_value: number
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
