import { FixedSizeList as List } from 'react-window'
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
  const useVirtualization = recommendations.length > 200

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`
  }


const Row = ({ reco }: { reco: RecommendationListItem }) => {
    const opt = reco.option_summary
    if (!opt) return null

    const optTarget1 = opt.option_targets?.[0]
    const optTarget2 = opt.option_targets?.[1]

    return (
      <tr
        onClick={() => onRowClick(reco)}
        className="hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0"
      >
        {/* Symbol */}
        <td className="px-4 py-3">
          <span className="font-semibold text-gray-900">{reco.symbol}</span>
        </td>

        {/* Option Type */}
        <td className="px-4 py-3">
          <span className="pill pill-buy font-semibold">{opt.option_type}</span>
        </td>

        {/* Strike Price */}
        <td className="px-4 py-3 text-gray-900 font-mono text-sm font-semibold">
          {formatPrice(opt.strike)}
        </td>

        {/* Expiry Date */}
        <td className="px-4 py-3 text-gray-700 text-sm">
          {new Date(opt.expiry).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
          })}
        </td>

        {/* Premium */}
        <td className="px-4 py-3">
          {reco.option_summary?.option_entry_price ? (
            <span className="font-mono text-sm text-blue-600 font-semibold">
              ${reco.option_summary.option_entry_price.toFixed(2)}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </td>

        {/* Target 1 */}
        <td className="px-4 py-3">
          {optTarget1 ? (
            <div className="flex flex-col">
              <span className="font-mono text-sm text-green-700 font-semibold">
                ${optTarget1.value.toFixed(2)}
              </span>
            </div>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </td>

        {/* Target 1 Confidence */}
        <td className="px-4 py-3">
          {optTarget1 ? (
            <span className="text-sm text-gray-700 font-medium">
              {formatPercent(optTarget1.confidence)}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </td>

        {/* Target 2 */}
        <td className="px-4 py-3">
          {optTarget2 ? (
            <div className="flex flex-col">
              <span className="font-mono text-sm text-green-700 font-semibold">
                ${optTarget2.value.toFixed(2)}
              </span>
            </div>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </td>

        {/* Target 2 Confidence */}
        <td className="px-4 py-3">
          {optTarget2 ? (
            <span className="text-sm text-gray-700 font-medium">
              {formatPercent(optTarget2.confidence)}
            </span>
          ) : (
            <span className="text-gray-400">—</span>
          )}
        </td>

        {/* Stock Entry Price (reference) */}
        <td className="px-4 py-3 text-gray-600 font-mono text-xs">
          {formatPrice(reco.entry_price)}
        </td>
      </tr>
    )
  }

  const VirtualizedRow = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const reco = recommendations[index]
    return (
      <div style={style}>
        <table className="w-full">
          <tbody>
            <Row reco={reco} />
          </tbody>
        </table>
      </div>
    )
  }

  const tableHeader = (
    <thead className="bg-gray-50 sticky top-0 z-10">
      <tr>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Symbol
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Option Type
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Strike Price
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Expiry Date
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Premium
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Target 1
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Target 1 Conf
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Target 2
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Target 2 Conf
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Stock Price
        </th>
      </tr>
    </thead>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <p className="mt-2 text-sm text-gray-500">Loading recommendations...</p>
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
            className="mx-auto h-12 w-12 text-gray-400"
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
          <h3 className="mt-2 text-sm font-medium text-gray-900">No call options available</h3>
          <p className="mt-1 text-sm text-gray-500">
            {recommendations.length === 0 
              ? 'Try adjusting your filters to see more results.'
              : 'No CALL options found in current recommendations.'}
          </p>
        </div>
      </div>
    )
  }

  if (useVirtualization) {
    // Filter to only show CALL options
    const callOptionsOnlyVirt = recommendations.filter(
      (reco) => reco.option_summary?.option_type === 'CALL'
    )

    return (
      <div className="bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          {tableHeader}
        </table>
        <List
          height={600}
          itemCount={callOptionsOnlyVirt.length}
          itemSize={80}
          width="100%"
        >
          {VirtualizedRow}
        </List>
      </div>
    )
  }

  return (
    <div className="bg-white overflow-auto" style={{ maxHeight: 'calc(100vh - 200px)' }}>
      <table className="min-w-full divide-y divide-gray-200">
        {tableHeader}
        <tbody className="bg-white divide-y divide-gray-100">
          {callOptionsOnly.map((reco) => (
            <Row key={reco.reco_id} reco={reco} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
