import { useQuery } from '@tanstack/react-query'
import { fetchRecommendationDetail } from '../api'
import type { RecommendationListItem } from '../types'

interface RecommendationDrawerProps {
  recommendation: RecommendationListItem | null
  onClose: () => void
}

export default function RecommendationDrawer({
  recommendation,
  onClose,
}: RecommendationDrawerProps) {
  const { data: detail, isLoading } = useQuery({
    queryKey: ['recommendation', recommendation?.reco_id],
    queryFn: () => fetchRecommendationDetail(recommendation!.reco_id),
    enabled: !!recommendation,
  })

  if (!recommendation) {
    return null
  }

  const formatPrice = (price: number) => `$${price.toFixed(2)}`
  const formatPercent = (value: number) => `${(value * 100).toFixed(1)}%`
  const formatDate = (isoDate: string) =>
    new Date(isoDate).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })

  // Safe accessors for generic rationale and quality objects
  const getRationale = () => detail?.rationale as any
  const getQuality = () => detail?.quality as any
  const getSentimentScore = () => getRationale()?.sentiment_score ?? 0.5

  const getSideBadgeClass = (side: string) => {
    switch (side) {
      case 'BUY':
        return 'pill pill-buy text-base px-4 py-1'
      case 'SELL':
        return 'pill pill-sell text-base px-4 py-1'
      case 'HOLD':
        return 'pill pill-hold text-base px-4 py-1'
      default:
        return 'pill text-base px-4 py-1'
    }
  }

  const getHorizonBadgeClass = (horizon: string) => {
    switch (horizon) {
      case 'intraday':
        return 'pill pill-intraday text-base px-4 py-1'
      case 'swing':
        return 'pill pill-swing text-base px-4 py-1'
      case 'position':
        return 'pill pill-position text-base px-4 py-1'
      default:
        return 'pill text-base px-4 py-1'
    }
  }

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return 'text-success-600'
    if (score >= 0.5) return 'text-warning-600'
    return 'text-danger-600'
  }

  const getSentimentLabel = (score: number) => {
    if (score >= 0.8) return 'Very Bullish'
    if (score >= 0.7) return 'Bullish'
    if (score >= 0.5) return 'Neutral'
    if (score >= 0.3) return 'Bearish'
    return 'Very Bearish'
  }

  const sentimentScore = getSentimentScore()
  const rationale = getRationale()
  const quality = getQuality()

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed inset-y-0 right-0 w-full max-w-3xl bg-white shadow-2xl z-50 overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-gray-900">
              {recommendation.symbol}
            </h2>
            <span className={getSideBadgeClass(recommendation.side)}>
              {recommendation.side}
            </span>
            <span className={getHorizonBadgeClass(recommendation.horizon)}>
              {recommendation.horizon}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
            </div>
          ) : detail ? (
            <>
              {/* Key Metrics */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Key Metrics
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Overall Confidence</div>
                    <div className="text-2xl font-bold text-primary-600">
                      {formatPercent(detail.confidence_overall)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Entry Price</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {formatPrice(detail.entry_price)}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Stop Price</div>
                    <div className="text-2xl font-bold text-danger-600">
                      {detail.stop_price ? formatPrice(detail.stop_price) : '—'}
                    </div>
                  </div>
                </div>
              </section>

              {/* Target Ladder - Underlying */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Target Ladder - Underlying
                </h3>
                <div className="space-y-2">
                  {detail.targets.map((target: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between bg-gradient-to-r from-primary-50 to-transparent p-4 rounded-lg border-l-4 border-primary-500"
                    >
                      <div className="flex items-center gap-4">
                        <div className="flex items-center justify-center w-10 h-10 bg-primary-100 text-primary-700 rounded-full font-semibold text-sm">
                          TP{target.ordinal}
                        </div>
                        <div>
                          <div className="text-xl font-bold text-gray-900">
                            {formatPrice(target.value)}
                          </div>
                          <div className="text-sm text-gray-500">
                            ETA: {target.eta_minutes ? Math.round(target.eta_minutes) : 'N/A'} min
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600 mb-1">Confidence</div>
                        <div className="text-lg font-semibold text-primary-600">
                          {formatPercent(target.confidence)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Target Ladder - Options */}
              {detail.option_idea && detail.option_idea.option_targets.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Target Ladder - Option Premiums
                  </h3>
                  <div className="bg-gradient-to-br from-success-50 to-blue-50 p-4 rounded-lg mb-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <div className="text-sm text-gray-600">Option Strategy</div>
                        <div className="text-xl font-bold text-gray-900">
                          {detail.option_idea.option_type} ${detail.option_idea.strike.toFixed(2)}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-600">Expiry</div>
                        <div className="text-base font-semibold text-gray-900">
                          {formatDate(detail.option_idea.expiry)}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {detail.option_idea.option_targets.map((target: any, idx: number) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between bg-gradient-to-r from-success-50 to-transparent p-4 rounded-lg border-l-4 border-success-500"
                      >
                        <div className="flex items-center gap-4">
                          <div className="flex items-center justify-center w-10 h-10 bg-success-100 text-success-700 rounded-full font-semibold text-sm">
                            OP{target.ordinal}
                          </div>
                          <div>
                            <div className="text-xl font-bold text-gray-900">
                              {formatPrice(target.value)}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600 mb-1">Confidence</div>
                          <div className="text-lg font-semibold text-success-600">
                            {formatPercent(target.confidence)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Sentiment Meter */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Market Sentiment
                </h3>
                <div className="bg-gradient-to-br from-gray-50 to-blue-50 p-6 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Sentiment Score</div>
                      <div className={`text-3xl font-bold ${getSentimentColor(sentimentScore)}`}>
                        {sentimentScore.toFixed(2)}
                      </div>
                      <div className="text-sm font-medium text-gray-700 mt-1">
                        {getSentimentLabel(sentimentScore)}
                      </div>
                    </div>
                    <div className="text-6xl">
                      {sentimentScore >= 0.7 ? '📈' : sentimentScore >= 0.5 ? '➡️' : '📉'}
                    </div>
                  </div>
                  
                  {/* Sentiment Bar */}
                  <div className="relative w-full h-4 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`absolute h-full transition-all ${
                        sentimentScore >= 0.7
                          ? 'bg-success-500'
                          : sentimentScore >= 0.5
                          ? 'bg-warning-500'
                          : 'bg-danger-500'
                      }`}
                      style={{ width: `${sentimentScore * 100}%` }}
                    />
                  </div>
                  
                  <div className="flex justify-between text-xs text-gray-500 mt-2">
                    <span>Bearish</span>
                    <span>Neutral</span>
                    <span>Bullish</span>
                  </div>
                </div>
              </section>

              {/* Catalysts & Event Tags */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Catalysts & Events
                </h3>
                <div className="space-y-4">
                  {/* Catalysts List */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm font-medium text-gray-600 mb-3">
                      Key Catalysts
                    </div>
                    <div className="space-y-2">
                      {(rationale?.catalysts || []).map((catalyst: string, idx: number) => (
                        <div key={idx} className="flex items-start gap-2">
                          <span className="inline-block px-3 py-1 bg-success-100 text-success-700 rounded-full text-sm font-medium">
                            ✓
                          </span>
                          <span className="text-gray-900 flex-1">{catalyst}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Event Tags */}
                  {rationale?.event_tags && rationale.event_tags.length > 0 && (
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm font-medium text-gray-600 mb-3">
                        Event Tags
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {rationale.event_tags.map((tag: string, idx: number) => (
                          <span
                            key={idx}
                            className="pill bg-blue-100 text-blue-700 text-sm"
                          >
                            {tag.replace(/_/g, ' ')}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </section>

              {/* Top Drivers / Thesis */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Top Drivers
                </h3>
                <div className="bg-gradient-to-br from-gray-50 to-primary-50 p-5 rounded-lg">
                  <div className="prose prose-sm max-w-none">
                    <p className="text-gray-900 leading-relaxed">
                      {rationale?.thesis || 'No thesis available'}
                    </p>
                  </div>
                </div>
              </section>

              {/* Risks */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Risk Factors
                </h3>
                <div className="bg-danger-50 p-4 rounded-lg">
                  <div className="space-y-2">
                    {(rationale?.risks || []).map((risk: string, idx: number) => (
                      <div key={idx} className="flex items-start gap-2 text-gray-900">
                        <svg
                          className="h-5 w-5 text-danger-500 flex-shrink-0 mt-0.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                          />
                        </svg>
                        {risk}
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              {/* Quality Metrics */}
              <section>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Quality Metrics
                </h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">
                      Liquidity Score
                    </div>
                    <div className="text-xl font-bold text-gray-900">
                      {quality?.liquidity_score?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Signal Strength</div>
                    <div className="text-xl font-bold text-gray-900">
                      {quality?.signal_strength?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Data Quality</div>
                    <div className="text-lg font-medium text-gray-900 capitalize">
                      {quality?.data_quality || 'Unknown'}
                    </div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Model Version</div>
                    <div className="text-lg font-medium text-gray-900">
                      {quality?.model_version || 'N/A'}
                    </div>
                  </div>
                </div>
              </section>
            </>
          ) : null}
        </div>
      </div>
    </>
  )
}
