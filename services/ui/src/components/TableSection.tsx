import { useState } from 'react'

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

interface TableSectionProps {
  data: Recommendation[]
  isLoading: boolean
  favorites: number[]
  onToggleFavorite: (recoId: number) => void
}

export default function TableSection({ data, isLoading, favorites, onToggleFavorite }: TableSectionProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)
  const [sortField, setSortField] = useState<keyof Recommendation>('confidence')
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc')
  const [expandedRow, setExpandedRow] = useState<number | null>(null)

  // Sorting logic
  const sortedData = [...data].sort((a, b) => {
    const aVal = a[sortField]
    const bVal = b[sortField]
    
    if (aVal === undefined || bVal === undefined) return 0
    
    if (typeof aVal === 'number' && typeof bVal === 'number') {
      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal
    }
    
    const aStr = String(aVal)
    const bStr = String(bVal)
    return sortDirection === 'asc' 
      ? aStr.localeCompare(bStr) 
      : bStr.localeCompare(aStr)
  })

  // Pagination logic
  const totalPages = Math.ceil(sortedData.length / pageSize)
  const startIndex = (currentPage - 1) * pageSize
  const endIndex = startIndex + pageSize
  const paginatedData = sortedData.slice(startIndex, endIndex)

  const handleSort = (field: keyof Recommendation) => {
    if (field === sortField) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    setExpandedRow(null)
  }

  const handlePageSizeChange = (size: number) => {
    setPageSize(size)
    setCurrentPage(1)
    setExpandedRow(null)
  }

  const getSentimentEmoji = (side: string) => {
    if (side === 'bullish') return '🟢'
    if (side === 'bearish') return '🔴'
    return '🟡'
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600 font-black'
    if (confidence >= 0.6) return 'text-yellow-600 font-bold'
    return 'text-red-600 font-semibold'
  }

  const SortIcon = ({ field }: { field: keyof Recommendation }) => {
    if (sortField !== field) return <span className="text-gray-400">↕</span>
    return sortDirection === 'asc' ? <span>↑</span> : <span>↓</span>
  }

  if (isLoading) {
    return (
      <section className="bg-white shadow-xl rounded-2xl border-2 border-purple-200 p-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
            <p className="text-xl font-bold text-purple-900">Loading recommendations...</p>
          </div>
        </div>
      </section>
    )
  }

  if (data.length === 0) {
    return (
      <section className="bg-white shadow-xl rounded-2xl border-2 border-purple-200 p-8">
        <div className="text-center py-16">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-2xl font-bold text-gray-700 mb-2">No recommendations found</h3>
          <p className="text-gray-500">Try adjusting your filters or refresh the data</p>
        </div>
      </section>
    )
  }

  return (
    <section className="bg-white shadow-xl rounded-2xl border-2 border-purple-200 overflow-hidden">
      {/* Table Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4 flex items-center justify-between">
        <h2 className="text-2xl font-black text-white flex items-center gap-3">
          📊 Recommendations ({sortedData.length})
        </h2>
        
        {/* Page Size Selector */}
        <div className="flex items-center gap-3 bg-white/20 backdrop-blur-sm rounded-xl px-4 py-2">
          <span className="text-white font-bold text-sm">Rows per page:</span>
          {[10, 25, 50, 100].map((size) => (
            <button
              key={size}
              onClick={() => handlePageSizeChange(size)}
              className={`px-3 py-1 rounded-lg font-bold text-sm transition-all ${
                pageSize === size
                  ? 'bg-white text-purple-600'
                  : 'bg-white/10 text-white hover:bg-white/30'
              }`}
            >
              {size}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-purple-100 border-b-2 border-purple-300">
            <tr>
              <th className="px-4 py-3 text-left">
                <button onClick={() => {}} className="font-bold text-purple-900 text-sm">
                  ⭐
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('symbol')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Symbol <SortIcon field="symbol" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('stock_price')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Stock Price <SortIcon field="stock_price" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('strategy')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Strategy <SortIcon field="strategy" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('side')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Sentiment <SortIcon field="side" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('strike')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Strike <SortIcon field="strike" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('expiry')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Expiry <SortIcon field="expiry" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('premium')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Premium <SortIcon field="premium" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <button
                  onClick={() => handleSort('confidence')}
                  className="font-bold text-purple-900 hover:text-purple-600 flex items-center gap-2 text-sm"
                >
                  Confidence <SortIcon field="confidence" />
                </button>
              </th>
              <th className="px-4 py-3 text-left">
                <span className="font-bold text-purple-900 text-sm">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedData.map((rec, idx) => {
              const isFavorite = favorites.includes(rec.reco_id)
              const isExpanded = expandedRow === rec.reco_id
              
              return (
                <>
                  <tr
                    key={rec.reco_id}
                    className={`border-b border-purple-100 hover:bg-purple-50 transition-colors ${
                      idx % 2 === 0 ? 'bg-white' : 'bg-purple-50/30'
                    }`}
                  >
                    <td className="px-4 py-3">
                      <button
                        onClick={() => onToggleFavorite(rec.reco_id)}
                        className="text-2xl hover:scale-125 transition-transform"
                      >
                        {isFavorite ? '⭐' : '☆'}
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-black text-purple-900 text-lg">{rec.symbol}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-gray-700">{formatCurrency(rec.stock_price)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded-lg text-xs font-bold">
                        {rec.strategy}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="flex items-center gap-2 font-semibold">
                        {getSentimentEmoji(rec.side)} {rec.side}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-bold text-gray-700">{formatCurrency(rec.strike)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-semibold text-gray-600">{rec.expiry}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-bold text-green-600">{formatCurrency(rec.premium)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={getConfidenceColor(rec.confidence)}>
                        {formatPercent(rec.confidence)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => setExpandedRow(isExpanded ? null : rec.reco_id)}
                        className="px-3 py-1 bg-purple-500 text-white rounded-lg text-xs font-bold hover:bg-purple-600 transition-colors"
                      >
                        {isExpanded ? 'Hide' : 'Details'}
                      </button>
                    </td>
                  </tr>
                  
                  {/* Expanded Details Row */}
                  {isExpanded && (
                    <tr className="bg-purple-100 border-b-2 border-purple-300">
                      <td colSpan={10} className="px-4 py-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {/* Targets */}
                          <div className="bg-white rounded-xl p-4 shadow-md">
                            <h4 className="font-black text-purple-900 mb-3">🎯 Targets & Risk</h4>
                            <div className="space-y-2 text-sm">
                              <div className="flex justify-between">
                                <span className="font-semibold text-gray-600">Target 1:</span>
                                <span className="font-bold text-green-600">{formatCurrency(rec.target1)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="font-semibold text-gray-600">Target 2:</span>
                                <span className="font-bold text-green-600">{formatCurrency(rec.target2)}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="font-semibold text-gray-600">Stop Loss:</span>
                                <span className="font-bold text-red-600">{formatCurrency(rec.stop_loss)}</span>
                              </div>
                            </div>
                          </div>

                          {/* Greeks */}
                          {rec.greeks && (
                            <div className="bg-white rounded-xl p-4 shadow-md">
                              <h4 className="font-black text-purple-900 mb-3">📈 Greeks</h4>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                  <span className="font-semibold text-gray-600">Delta:</span>
                                  <span className="font-bold">{rec.greeks.delta?.toFixed(4) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-gray-600">Gamma:</span>
                                  <span className="font-bold">{rec.greeks.gamma?.toFixed(4) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-gray-600">Theta:</span>
                                  <span className="font-bold">{rec.greeks.theta?.toFixed(4) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="font-semibold text-gray-600">Vega:</span>
                                  <span className="font-bold">{rec.greeks.vega?.toFixed(4) || 'N/A'}</span>
                                </div>
                              </div>
                            </div>
                          )}

                          {/* Rationale */}
                          <div className="bg-white rounded-xl p-4 shadow-md">
                            <h4 className="font-black text-purple-900 mb-3">💡 Rationale</h4>
                            <p className="text-sm text-gray-700 leading-relaxed">
                              {rec.rationale}
                            </p>
                            {rec.quality && (
                              <div className="mt-3 pt-3 border-t border-purple-200">
                                <span className="px-3 py-1 bg-purple-500 text-white rounded-full text-xs font-bold">
                                  Quality: {rec.quality}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="bg-purple-50 px-6 py-4 border-t-2 border-purple-200 flex items-center justify-between">
        <div className="text-sm font-semibold text-purple-900">
          Showing {startIndex + 1} to {Math.min(endIndex, sortedData.length)} of {sortedData.length} recommendations
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={() => handlePageChange(1)}
            disabled={currentPage === 1}
            className="px-3 py-2 bg-white border-2 border-purple-300 text-purple-700 rounded-lg font-bold text-sm hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            ««
          </button>
          <button
            onClick={() => handlePageChange(currentPage - 1)}
            disabled={currentPage === 1}
            className="px-3 py-2 bg-white border-2 border-purple-300 text-purple-700 rounded-lg font-bold text-sm hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            «
          </button>
          
          {/* Page Numbers */}
          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
            let pageNum: number
            if (totalPages <= 5) {
              pageNum = i + 1
            } else if (currentPage <= 3) {
              pageNum = i + 1
            } else if (currentPage >= totalPages - 2) {
              pageNum = totalPages - 4 + i
            } else {
              pageNum = currentPage - 2 + i
            }
            
            return (
              <button
                key={pageNum}
                onClick={() => handlePageChange(pageNum)}
                className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
                  currentPage === pageNum
                    ? 'bg-purple-600 text-white shadow-lg'
                    : 'bg-white border-2 border-purple-300 text-purple-700 hover:bg-purple-100'
                }`}
              >
                {pageNum}
              </button>
            )
          })}
          
          <button
            onClick={() => handlePageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="px-3 py-2 bg-white border-2 border-purple-300 text-purple-700 rounded-lg font-bold text-sm hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            »
          </button>
          <button
            onClick={() => handlePageChange(totalPages)}
            disabled={currentPage === totalPages}
            className="px-3 py-2 bg-white border-2 border-purple-300 text-purple-700 rounded-lg font-bold text-sm hover:bg-purple-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            »»
          </button>
        </div>
      </div>
    </section>
  )
}
