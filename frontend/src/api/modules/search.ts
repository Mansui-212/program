import http from '@/api/http'

import type { SearchResult } from '@/types/search'

export function searchSite(keyword: string) {
  return http.get<SearchResult>('/v1/search', {
    params: {
      q: keyword,
    },
  })
}
