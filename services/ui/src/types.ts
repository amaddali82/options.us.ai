/**
 * API Types - EXACTLY matching FastAPI backend schema
 * Do NOT include rationale in list items - only in detail endpoint
 */

export interface RecommendationListItem {
  reco_id: string
  asof: string  // ISO datetime
  symbol: string
  horizon: 'intraday' | 'swing' | 'position'
  side: 'BUY' | 'SELL' | 'HOLD'
  entry_price: number  // Always > 0
  confidence_overall: number  // 0.0 to 1.0
  expected_move_pct: number | null
  rank: number  // Calculated ranking score
  
  // First two targets only (no rationale in list)
  tp1?: TargetSummary
  tp2?: TargetSummary
  
  // Option summary if present
  option_summary?: OptionSummary
}

export interface TargetSummary {
  ordinal: number  // Target number (1, 2, 3...)
  value: number  // Target price (> 0)
  confidence: number  // 0.0 to 1.0
}

export interface OptionSummary {
  option_type: 'CALL' | 'PUT'
  expiry: string  // ISO date, must be future
  strike: number  // > 0
  option_entry_price?: number  // Premium price
  option_targets: TargetSummary[]  // Max 2 targets in list view
}

export interface RecommendationDetail {
  reco_id: string
  asof: string  // ISO datetime
  symbol: string
  horizon: 'intraday' | 'swing' | 'position'
  side: 'BUY' | 'SELL' | 'HOLD'
  entry_price: number  // > 0
  stop_price: number | null  // Stop loss price
  confidence_overall: number  // 0.0 to 1.0
  expected_move_pct: number | null
  rank: number
  
  // Rationale - ONLY in detail endpoint
  rationale: Record<string, any> | null
  quality: Record<string, any> | null
  
  // All targets (not limited to 2)
  targets: TargetDetail[]
  
  // Full option details if present
  option_idea?: OptionDetail
  
  created_at: string
  updated_at: string
}

// Rationale and quality are kept as generic objects
// to avoid tight coupling with backend structure

export interface TargetDetail {
  ordinal: number  // >= 1
  name: string | null
  target_type: string  // "price"
  value: number  // > 0
  confidence: number  // 0.0 to 1.0
  eta_minutes: number | null  // >= 0 if present
  notes: string | null
}

export interface OptionDetail {
  option_type: 'CALL' | 'PUT'
  expiry: string  // ISO date, must be future
  strike: number  // > 0
  option_entry_price: number  // > 0
  greeks: Record<string, any> | null
  iv: Record<string, any> | null
  notes: string | null
  option_targets: OptionTargetDetail[]
}

export interface OptionTargetDetail {
  ordinal: number  // >= 1
  name: string | null
  value: number  // Premium target (> 0)
  confidence: number  // 0.0 to 1.0
  eta_minutes: number | null  // >= 0 if present
  notes: string | null
}

export interface RecommendationsResponse {
  recommendations: RecommendationListItem[]
  meta: PaginationMeta  // Match backend field name
}

export interface PaginationMeta {
  total_returned: number  // Count of items in current response
  has_more: boolean  // Whether more items exist
  next_cursor: string | null  // Time-based cursor for next page
}

export interface FiltersState {
  horizon: string
  minConfidence: number
  symbol: string
  sort: string
  optionsOnly: boolean
}

export interface HealthResponse {
  status: string
  timestamp: string
  database?: string
}
