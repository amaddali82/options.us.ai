import { useState } from 'react'
import type { RecommendationListItem } from '../types'

interface RecommendationsTableProps {
  recommendations: RecommendationListItem[]
  onRowClick: (reco: RecommendationListItem) => void
  isLoading: boolean
  favorites: string[]
  onToggleFavorite: (recoId: string) => void
}

type SortField = 'symbol' | 'strike' | 'entry_price' | 'expiry' | 'target1' | 'stock_price'
type SortDirection = 'asc' | 'desc'

export default function RecommendationsTable({
  recommendations,
  onRowClick,
  isLoading,
  favorites,
  onToggleFavorite,
}: RecommendationsTableProps) {
  const [sortField, setSortField] = useState<SortField>('symbol')
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc')

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <span className="ml-1 text-gray-300">⇅</span>
    }
    return (
      <span className="ml-1 text-indigo-200">
        {sortDirection === 'asc' ? '↑' : '↓'}
      </span>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="mt-2 text-sm text-gray-600">Loading options...</p>
        </div>
      </div>
    )
  }

  // Filter to only show CALL options
  const callOptionsOnly = recommendations.filter(
    (reco) => reco.option_summary?.option_type === 'CALL'
  )

  // Sort recommendations
  const sortedRecommendations = [...callOptionsOnly].sort((a, b) => {
    let aVal: any, bVal: any
    
    switch (sortField) {
      case 'symbol':
        aVal = a.symbol
        bVal = b.symbol
        break
      case 'strike':
        aVal = a.option_summary?.strike || 0
        bVal = b.option_summary?.strike || 0
        break
      case 'entry_price':
        aVal = a.option_summary?.option_entry_price || 0
        bVal = b.option_summary?.option_entry_price || 0
        break
      case 'expiry':
        aVal = new Date(a.option_summary?.expiry || 0).getTime()
        bVal = new Date(b.option_summary?.expiry || 0).getTime()
        break
      case 'target1':
        aVal = a.option_summary?.option_targets?.[0]?.value || 0
        bVal = b.option_summary?.option_targets?.[0]?.value || 0
        break
      case 'stock_price':
        aVal = a.entry_price
        bVal = b.entry_price
        break
      default:
        return 0
    }
    
    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1
    return 0
  })

  if (recommendations.length === 0 || callOptionsOnly.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-300"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-700">No call options available</h3>
          <p className="mt-1 text-sm text-gray-500">
            {recommendations.length === 0 
              ? 'Try adjusting your filters to see more results.'
              : 'No CALL options found in current recommendations.'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      <div className="overflow-x-auto">
        <table className="w-full table-auto divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-slate-700 via-slate-600 to-slate-700">
            <tr>
              <th className="px-6 py-5 text-left text-sm font-bold text-white uppercase tracking-wider">
                ⭐
              </th>
              <th 
                onClick={() => handleSort('symbol')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
              >
                <div className="flex items-center">
                  Symbol <SortIcon field="symbol" />
                </div>
              </th>
              <th className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider">
                Type
              </th>
              <th 
                onClick={() => handleSort('strike')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
                title="Strike Price: The fixed price at which you can buy the stock if you exercise the option contract"
              >
                <div className="flex items-center">
                  Strike Price <SortIcon field="strike" />
                </div>
              </th>
              <th 
                onClick={() => handleSort('entry_price')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
              >
                <div className="flex items-center">
                  Entry Price <SortIcon field="entry_price" />
                </div>
              </th>
              <th 
                onClick={() => handleSort('expiry')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
              >
                <div className="flex items-center">
                  Expiry Date <SortIcon field="expiry" />
                </div>
              </th>
              <th 
                onClick={() => handleSort('target1')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
              >
                <div className="flex items-center">
                  Target 1 <SortIcon field="target1" />
                </div>
              </th>
              <th className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider">
                Target 2
              </th>
              <th className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider">
                Confidence
              </th>
              <th 
                onClick={() => handleSort('stock_price')}
                className="px-8 py-5 text-left text-sm font-bold text-white uppercase tracking-wider cursor-pointer hover:bg-slate-600 transition-colors"
                title="Stock Price: Current market price of the underlying stock"
              >
                <div className="flex items-center">
                  Stock Price <SortIcon field="stock_price" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-100">
            {sortedRecommendations.map((reco, idx) => {
              const opt = reco.option_summary
              if (!opt) return null

              const optTarget1 = opt.option_targets?.[0]
              const optTarget2 = opt.option_targets?.[1]

              return (
                <tr
                  key={reco.reco_id}
                  className={`hover:bg-slate-100 cursor-pointer transition-all hover:shadow-sm ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-slate-50'
                  }`}
                >
                  {/* Favorite Star */}
                  <td className="px-6 py-5 whitespace-nowrap">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onToggleFavorite(reco.reco_id)
                      }}
                      className="text-2xl hover:scale-110 transition-transform"
                      title={favorites.includes(reco.reco_id) ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      {favorites.includes(reco.reco_id) ? '⭐' : '☆'}
                    </button>
                  </td>

                  {/* Symbol */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    <span className="text-xl font-bold text-slate-800">{reco.symbol}</span>
                  </td>

                  {/* Option Type */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    <span className="inline-flex items-center px-4 py-1.5 rounded-full text-base font-bold bg-emerald-100 text-emerald-800">
                      {opt.option_type}
                    </span>
                  </td>

                  {/* Strike Price */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    <span className="text-lg font-bold text-gray-900">
                      {formatPrice(opt.strike)}
                    </span>
                  </td>

                  {/* Entry Price (Premium) */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    {opt.option_entry_price ? (
                      <span className="text-lg font-extrabold text-teal-700">
                        {formatPrice(opt.option_entry_price)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Expiry Date */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    <span className="text-base font-medium text-gray-700">{formatDate(opt.expiry)}</span>
                  </td>

                  {/* Target 1 */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    {optTarget1 ? (
                      <span className="text-lg font-bold text-emerald-600">
                        {formatPrice(optTarget1.value)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 1 Confidence */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    {optTarget1 ? (
                      <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-base font-bold bg-emerald-100 text-emerald-900">
                        {formatPercent(optTarget1.confidence)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 2 */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    {optTarget2 ? (
                      <span className="text-lg font-bold text-amber-600">
                        {formatPrice(optTarget2.value)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 2 Confidence */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    {optTarget2 ? (
                      <span className="inline-flex items-center px-3 py-1.5 rounded-lg text-base font-bold bg-amber-100 text-amber-900">
                        {formatPercent(optTarget2.confidence)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Stock Price */}
                  <td className="px-8 py-5 whitespace-nowrap" onClick={() => onRowClick(reco)}>
                    <span className="text-base font-semibold text-gray-700">{formatPrice(reco.entry_price)}</span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
