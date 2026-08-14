export interface User {
  id: number
  username: string
  nickname: string
  avatar_url: string | null
  haki_value: number
  role: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}
