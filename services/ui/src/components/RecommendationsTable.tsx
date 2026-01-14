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

  const getSideBadgeClass = (side: string) => {
    switch (side) {
      case 'BUY':
        return 'pill pill-buy'
      case 'SELL':
        return 'pill pill-sell'
      case 'HOLD':
        return 'pill pill-hold'
      default:
        return 'pill'
    }
  }

  const getHorizonBadgeClass = (horizon: string) => {
    switch (horizon) {
      case 'intraday':
        return 'pill pill-intraday'
      case 'swing':
        return 'pill pill-swing'
      case 'position':
        return 'pill pill-position'
      default:
        return 'pill'
    }
  }

  const formatPrice = (price: number) => {
    return `$${price.toFixed(2)}`
  }

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`
  }

  const formatOptionSummary = (opt: any) => {
    if (!opt) return '—'
    return `${opt.option_type} ${opt.strike.toFixed(2)} ${new Date(opt.expiry).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' })}`
  }


  const Row = ({ reco }: { reco: RecommendationListItem }) => (
    <tr
      onClick={() => onRowClick(reco)}
      className="hover:bg-gray-50 cursor-pointer transition-colors border-b border-gray-100 last:border-b-0"
    >
      {/* Symbol */}
      <td className="px-4 py-3">
        <span className="font-semibold text-gray-900">{reco.symbol}</span>
      </td>

      {/* Side */}
      <td className="px-4 py-3">
        <span className={getSideBadgeClass(reco.side)}>{reco.side}</span>
      </td>

      {/* Horizon */}
      <td className="px-4 py-3">
        <span className={getHorizonBadgeClass(reco.horizon)}>
          {reco.horizon}
        </span>
      </td>

      {/* Conf */}
      <td className="px-4 py-3 font-mono text-sm">
        {formatPercent(reco.confidence_overall)}
      </td>

      {/* Entry */}
      <td className="px-4 py-3 text-gray-900 font-mono text-sm">
        {formatPrice(reco.entry_price)}
      </td>

      {/* TP1 (Conf) */}
      <td className="px-4 py-3">
        {reco.tp1 ? (
          <div className="flex flex-col">
            <span className="font-mono text-sm text-gray-900">
              {formatPrice(reco.tp1.target_price)}
            </span>
            <span className="text-xs text-gray-500">
              ({formatPercent(reco.tp1.confidence)})
            </span>
          </div>
        ) : (
          <span className="text-gray-400">—</span>
        )}
      </td>

      {/* TP2 (Conf) */}
      <td className="px-4 py-3">
        {reco.tp2 ? (
          <div className="flex flex-col">
            <span className="font-mono text-sm text-gray-900">
              {formatPrice(reco.tp2.value)}
            </span>
            <span className="text-xs text-gray-500">
              ({formatPercent(reco.tp2.confidence)})
            </span>
          </div>
        ) : (
          <span className="text-gray-400">—</span>
        )}
      </td>

      {/* Stop */}
      <td className="px-4 py-3 text-gray-900 font-mono text-sm">
        —
      </td>

      {/* Option (type strike expiry) */}
      <td className="px-4 py-3">
        <span className="text-xs text-gray-600">
          {formatOptionSummary(reco.option_summary)}
        </span>
      </td>

      {/* Opt TP1 (Conf) */}
      <td className="px-4 py-3">
        <span className="text-gray-400">—</span>
      </td>

      {/* Opt TP2 (Conf) */}
      <td className="px-4 py-3">
        <span className="text-gray-400">—</span>
      </td>
    </tr>
  )

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
          Side
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Horizon
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Conf
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Entry
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          TP1 (Conf)
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          TP2 (Conf)
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Stop
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Option
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Opt TP1
        </th>
        <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
          Opt TP2
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

  if (recommendations.length === 0) {
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
          <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters to see more results.
          </p>
        </div>
      </div>
    )
  }

  if (useVirtualization) {
    return (
      <div className="bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          {tableHeader}
        </table>
        <List
          height={600}
          itemCount={recommendations.length}
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
          {recommendations.map((reco) => (
            <Row key={reco.reco_id} reco={reco} />
          ))}
        </tbody>
      </table>
    </div>
  )
}
