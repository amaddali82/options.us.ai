import type { RecommendationListItem } from '../types'

interface RecommendationsTableProps {
  recommendations: RecommendationListItem[]
  onRowClick: (reco: RecommendationListItem) => void
  isLoading: boolean
}

export default function RecommendationsTable({
  recommendations,
  onRowClick,
  isLoading,
}: RecommendationsTableProps) {

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
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-100">
          <thead className="bg-gradient-to-r from-blue-50 to-indigo-50">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Option Type
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Strike Price
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Entry Price
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Expiry Date
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Target 1
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Target 2
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Confidence
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                Stock Price
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-50">
            {callOptionsOnly.map((reco, idx) => {
              const opt = reco.option_summary
              if (!opt) return null

              const optTarget1 = opt.option_targets?.[0]
              const optTarget2 = opt.option_targets?.[1]

              return (
                <tr
                  key={reco.reco_id}
                  onClick={() => onRowClick(reco)}
                  className={`hover:bg-blue-50 cursor-pointer transition-colors ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  }`}
                >
                  {/* Symbol */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-bold text-gray-900">{reco.symbol}</span>
                  </td>

                  {/* Option Type */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">
                      {opt.option_type}
                    </span>
                  </td>

                  {/* Strike Price */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-base font-semibold text-gray-900">
                      {formatPrice(opt.strike)}
                    </span>
                  </td>

                  {/* Entry Price (Premium) */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {opt.option_entry_price ? (
                      <span className="text-base font-bold text-blue-600">
                        {formatPrice(opt.option_entry_price)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Expiry Date */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-700">{formatDate(opt.expiry)}</span>
                  </td>

                  {/* Target 1 */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {optTarget1 ? (
                      <span className="text-base font-semibold text-green-700">
                        {formatPrice(optTarget1.value)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 1 Confidence */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {optTarget1 ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-sm font-medium bg-green-100 text-green-800">
                        {formatPercent(optTarget1.confidence)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 2 */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {optTarget2 ? (
                      <span className="text-base font-semibold text-blue-700">
                        {formatPrice(optTarget2.value)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Target 2 Confidence */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    {optTarget2 ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-md text-sm font-medium bg-blue-100 text-blue-800">
                        {formatPercent(optTarget2.confidence)}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>

                  {/* Stock Price */}
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-600">{formatPrice(reco.entry_price)}</span>
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
