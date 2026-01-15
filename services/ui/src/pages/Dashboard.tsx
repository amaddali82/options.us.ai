import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import Header from '../components/Header'
import FiltersSection, { Filters } from '../components/FiltersSection'
import TableSection from '../components/TableSection'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface TargetSummary {
  ordinal: number
  value: number
  confidence: number
}

interface OptionSummary {
  option_type: string
  expiry: string
  strike: number
  option_entry_price?: number
  option_targets?: TargetSummary[]
}

interface ApiRecommendation {
  reco_id: string
  symbol: string
  side: string
  entry_price: number
  confidence_overall: number
  horizon: string
  tp1?: TargetSummary
  tp2?: TargetSummary
  option_summary?: OptionSummary
}

interface Recommendation {
  reco_id: number
  symbol: string
  stock_price: number
  strategy: string
  side: string
  strike: number
  expiry: string
  premium: number
  target1: number
  target2: number
  stop_loss: number
  confidence: number
  rationale: string
  quality: string
  option_entry_price?: number
  greeks?: any
  iv?: any
  last_updated?: string
}

export default function Dashboard() {
  const queryClient = useQueryClient()
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  
  const [filters, setFilters] = useState<Filters>({
    search: '',
    strategy: 'all',
    expiration: 'all',
    sentiment: 'all',
    minConfidence: 0,
    favorites: [],
    showFavoritesOnly: false
  })

  // Fetch recommendations
  const { data: apiRecommendations = [], isLoading } = useQuery<ApiRecommendation[]>({
    queryKey: ['recommendations'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/recommendations`)
      if (!response.ok) throw new Error('Failed to fetch recommendations')
      const data = await response.json()
      return data.recommendations || []
    },
    refetchInterval: 60000, // Refetch every minute
  })

  // Transform API data to match TableSection interface
  const recommendations: Recommendation[] = apiRecommendations
    .filter(api => api.option_summary) // Only show options
    .map((api) => {
      const optTargets = api.option_summary?.option_targets || []
      const optTarget1 = optTargets.find(t => t.ordinal === 1)?.value || 0
      const optTarget2 = optTargets.find(t => t.ordinal === 2)?.value || 0
      const optPremium = api.option_summary?.option_entry_price || 0
      
      // Calculate stop loss as 30% below entry premium
      const stopLoss = optPremium * 0.7
      
      return {
        reco_id: parseInt(api.reco_id) || 0,
        symbol: api.symbol,
        stock_price: api.entry_price,
        strategy: api.option_summary?.option_type?.toLowerCase() || 'unknown',
        side: api.side.toLowerCase(),
        strike: api.option_summary?.strike || 0,
        expiry: api.option_summary?.expiry || '',
        premium: optPremium,
        target1: optTarget1,
        target2: optTarget2,
        stop_loss: stopLoss,
        confidence: api.confidence_overall,
        rationale: `${api.horizon} ${api.side} opportunity with ${api.option_summary?.option_type}`,
        quality: api.confidence_overall >= 0.8 ? 'high' : api.confidence_overall >= 0.6 ? 'medium' : 'low',
        option_entry_price: optPremium
      }
    })

  // Manual refresh function
  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      const response = await fetch(`${API_URL}/recommendations/refresh`, {
        method: 'POST',
      })
      
      if (!response.ok) {
        throw new Error('Failed to refresh data')
      }
      
      // Invalidate and refetch
      await queryClient.invalidateQueries({ queryKey: ['recommendations'] })
      setLastRefresh(new Date())
    } catch (error) {
      console.error('Error refreshing data:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  // Apply filters to recommendations
  const filteredRecommendations = recommendations.filter(reco => {
    // Search filter
    if (filters.search && !reco.symbol.toUpperCase().includes(filters.search.toUpperCase())) {
      return false
    }
    
    // Strategy filter
    if (filters.strategy !== 'all' && reco.strategy !== filters.strategy) {
      return false
    }
    
    // Expiration filter
    if (filters.expiration !== 'all') {
      const expiryDate = new Date(reco.expiry)
      const today = new Date()
      const daysUntilExpiry = Math.ceil((expiryDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      
      if (filters.expiration === '0-7' && (daysUntilExpiry < 0 || daysUntilExpiry > 7)) return false
      if (filters.expiration === '8-30' && (daysUntilExpiry < 8 || daysUntilExpiry > 30)) return false
      if (filters.expiration === '31-60' && (daysUntilExpiry < 31 || daysUntilExpiry > 60)) return false
      if (filters.expiration === '61+' && daysUntilExpiry < 61) return false
    }
    
    // Sentiment filter
    if (filters.sentiment !== 'all' && reco.side !== filters.sentiment) {
      return false
    }
    
    // Confidence filter
    if (reco.confidence < filters.minConfidence) {
      return false
    }
    
    // Favorites filter
    if (filters.showFavoritesOnly && !filters.favorites.includes(reco.reco_id)) {
      return false
    }
    
    return true
  })

  const handleToggleFavorite = (recoId: number) => {
    setFilters(prev => ({
      ...prev,
      favorites: prev.favorites.includes(recoId)
        ? prev.favorites.filter(id => id !== recoId)
        : [...prev.favorites, recoId]
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50">
      <Header
        lastRefresh={lastRefresh}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />
      
      <div className="max-w-[1600px] mx-auto px-8 py-8 space-y-6">
        <FiltersSection
          filters={filters}
          onFiltersChange={setFilters}
        />
        
        <TableSection
          data={filteredRecommendations}
          isLoading={isLoading}
          favorites={filters.favorites}
          onToggleFavorite={handleToggleFavorite}
        />
      </div>
    </div>
  )
}
