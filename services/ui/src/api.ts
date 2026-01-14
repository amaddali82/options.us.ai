/// <reference types="vite/client" />

import type {
  RecommendationsResponse,
  RecommendationDetail,
  FiltersState,
  HealthResponse,
} from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Typed fetch client for API communication
 */

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new ApiError(
        `API Error: ${response.statusText}`,
        response.status,
        data
      )
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      0
    )
  }
}

/**
 * Fetch recommendations list with filters
 */
export async function fetchRecommendations(
  filters: FiltersState,
  cursor?: string | null
): Promise<RecommendationsResponse> {
  const params = new URLSearchParams()

  params.append('limit', '200')
  params.append('sort', filters.sort)

  if (filters.horizon && filters.horizon !== 'all') {
    params.append('horizon', filters.horizon)
  }

  if (filters.minConfidence > 0) {
    params.append('min_conf', filters.minConfidence.toFixed(2))
  }

  if (filters.symbol.trim()) {
    params.append('symbol', filters.symbol.trim().toUpperCase())
  }

  if (cursor) {
    params.append('cursor', cursor)
  }

  return fetchApi<RecommendationsResponse>(
    `/recommendations?${params.toString()}`
  )
}

/**
 * Fetch recommendation details by ID
 */
export async function fetchRecommendationDetail(
  recoId: string
): Promise<RecommendationDetail> {
  return fetchApi<RecommendationDetail>(`/recommendations/${recoId}`)
}

/**
 * Health check
 */
export async function checkHealth(): Promise<HealthResponse> {
  return fetchApi<HealthResponse>('/health')
}

export { ApiError }
