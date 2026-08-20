import http from '@/api/http'

import type { ChronicleEvent } from '@/types/chronicle'

export function getChronicleEvents() {
  return http.get<ChronicleEvent[]>('/v1/chronicle')
}
