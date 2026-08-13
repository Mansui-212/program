import http from '@/api/http'

export interface HealthResponse {
  status: string
  backend: string
  database: string
  database_test: number
}

export function getHealth() {
  return http.get<HealthResponse>('/v1/system/health')
}
