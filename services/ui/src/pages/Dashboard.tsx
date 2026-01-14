import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchRecommendations } from '../api'
import FiltersBar from '../components/FiltersBar'
import RecommendationsTable from '../components/RecommendationsTable'
import RecommendationDrawer from '../components/RecommendationDrawer'
import type { FiltersState, RecommendationListItem } from '../types'

export default function Dashboard() {
  const [filters, setFilters] = useState<FiltersState>({
    horizon: 'all',
    minConfidence: 0,
    symbol: '',
    sort: 'rank',
  })

  const [selectedRecommendation, setSelectedRecommendation] =
    useState<RecommendationListItem | null>(null)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['recommendations', filters],
    queryFn: () => fetchRecommendations(filters),
  })

  const handleRowClick = (reco: RecommendationListItem) => {
    setSelectedRecommendation(reco)
  }

  const handleDrawerClose = () => {
    setSelectedRecommendation(null)
  }

  if (isError) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md">
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-danger-100 rounded-full mb-4">
            <svg
              className="h-6 w-6 text-danger-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">
            Connection Error
          </h2>
          <p className="text-gray-600 text-center mb-4">
            {error instanceof Error ? error.message : 'Failed to load recommendations'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <FiltersBar
        filters={filters}
        onFiltersChange={setFilters}
        totalCount={data?.meta.total_returned ?? 0}
      />
      
      <div className="container mx-auto px-6 py-6">
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <RecommendationsTable
            recommendations={data?.recommendations ?? []}
            onRowClick={handleRowClick}
            isLoading={isLoading}
          />
        </div>
      </div>

      <RecommendationDrawer
        recommendation={selectedRecommendation}
        onClose={handleDrawerClose}
      />
    </div>
  )
}
