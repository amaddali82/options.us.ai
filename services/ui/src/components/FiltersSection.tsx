import { useState, KeyboardEvent } from 'react'

export interface Filters {
  search: string
  strategy: string
  expiration: string
  sentiment: string
  minConfidence: number
  favorites: number[]
  showFavoritesOnly: boolean
}

interface FiltersSectionProps {
  filters: Filters
  onFiltersChange: (filters: Filters) => void
}

export default function FiltersSection({ filters, onFiltersChange }: FiltersSectionProps) {
  const [symbolInput, setSymbolInput] = useState('')

  const handleSymbolChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase()
    setSymbolInput(value)
  }

  const handleSymbolKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onFiltersChange({ ...filters, search: symbolInput })
    }
  }

  const handleSymbolBlur = () => {
    onFiltersChange({ ...filters, search: symbolInput })
  }

  const handleStrategyChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, strategy: e.target.value })
  }

  const handleExpirationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, expiration: e.target.value })
  }

  const handleSentimentChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onFiltersChange({ ...filters, sentiment: e.target.value })
  }

  const handleConfidenceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFiltersChange({ ...filters, minConfidence: parseFloat(e.target.value) })
  }

  const handleFavoritesToggle = () => {
    onFiltersChange({ ...filters, showFavoritesOnly: !filters.showFavoritesOnly })
  }

  const handleReset = () => {
    setSymbolInput('')
    onFiltersChange({
      search: '',
      strategy: 'all',
      expiration: 'all',
      sentiment: 'all',
      minConfidence: 0,
      favorites: filters.favorites, // Keep favorites
      showFavoritesOnly: false
    })
  }

  return (
    <section className="bg-white shadow-xl rounded-2xl border-2 border-purple-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-black text-purple-900 flex items-center gap-3">
          🔍 Smart Filters
        </h2>
        <div className="flex items-center gap-3">
          {/* Favorites Toggle */}
          <button
            onClick={handleFavoritesToggle}
            className={`px-6 py-3 rounded-xl font-bold text-sm transition-all shadow-lg ${
              filters.showFavoritesOnly
                ? 'bg-gradient-to-r from-yellow-500 to-amber-500 text-white scale-105 shadow-yellow-500/50'
                : 'bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 hover:scale-105 hover:shadow-purple-300/50'
            }`}
          >
            {filters.showFavoritesOnly ? '⭐ Favorites Only' : '☆ Show All'}
            {filters.favorites.length > 0 && (
              <span className="ml-2 px-2 py-0.5 bg-white/30 rounded-full text-xs font-black">
                {filters.favorites.length}
              </span>
            )}
          </button>

          {/* Reset Filters */}
          <button
            onClick={handleReset}
            className="px-6 py-3 bg-gradient-to-r from-gray-200 to-gray-300 text-gray-700 rounded-xl font-bold text-sm hover:from-gray-300 hover:to-gray-400 transition-all hover:scale-105 shadow-lg"
          >
            ↺ Reset
          </button>
        </div>
      </div>

      {/* Filter Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Symbol Search */}
        <div>
          <label className="block text-sm font-bold text-purple-800 mb-2">
            Symbol
          </label>
          <input
            type="text"
            value={symbolInput}
            onChange={handleSymbolChange}
            onKeyDown={handleSymbolKeyDown}
            onBlur={handleSymbolBlur}
            placeholder="e.g., AAPL"
            className="w-full px-4 py-3 border-2 border-purple-300 rounded-xl focus:ring-4 focus:ring-purple-300 focus:border-purple-500 font-semibold text-lg transition-all"
          />
        </div>

        {/* Strategy Filter */}
        <div>
          <label className="block text-sm font-bold text-purple-800 mb-2">
            Strategy
          </label>
          <select
            value={filters.strategy}
            onChange={handleStrategyChange}
            className="w-full px-4 py-3 border-2 border-purple-300 rounded-xl focus:ring-4 focus:ring-purple-300 focus:border-purple-500 font-semibold text-lg transition-all cursor-pointer"
          >
            <option value="all">All Strategies</option>
            <option value="long_call">Long Call</option>
            <option value="long_put">Long Put</option>
            <option value="bull_call_spread">Bull Call Spread</option>
            <option value="bear_put_spread">Bear Put Spread</option>
            <option value="iron_condor">Iron Condor</option>
            <option value="butterfly">Butterfly</option>
          </select>
        </div>

        {/* Expiration Filter */}
        <div>
          <label className="block text-sm font-bold text-purple-800 mb-2">
            Expiration
          </label>
          <select
            value={filters.expiration}
            onChange={handleExpirationChange}
            className="w-full px-4 py-3 border-2 border-purple-300 rounded-xl focus:ring-4 focus:ring-purple-300 focus:border-purple-500 font-semibold text-lg transition-all cursor-pointer"
          >
            <option value="all">All Expirations</option>
            <option value="0-7">0-7 days</option>
            <option value="8-30">8-30 days</option>
            <option value="31-60">31-60 days</option>
            <option value="61+">61+ days</option>
          </select>
        </div>

        {/* Sentiment Filter */}
        <div>
          <label className="block text-sm font-bold text-purple-800 mb-2">
            Sentiment
          </label>
          <select
            value={filters.sentiment}
            onChange={handleSentimentChange}
            className="w-full px-4 py-3 border-2 border-purple-300 rounded-xl focus:ring-4 focus:ring-purple-300 focus:border-purple-500 font-semibold text-lg transition-all cursor-pointer"
          >
            <option value="all">All Sentiments</option>
            <option value="bullish">🟢 Bullish</option>
            <option value="bearish">🔴 Bearish</option>
            <option value="neutral">🟡 Neutral</option>
          </select>
        </div>

        {/* Confidence Filter */}
        <div>
          <label className="block text-sm font-bold text-purple-800 mb-2">
            Min Confidence: {(filters.minConfidence * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={filters.minConfidence}
            onChange={handleConfidenceChange}
            className="w-full h-3 bg-gradient-to-r from-purple-200 to-pink-300 rounded-lg appearance-none cursor-pointer accent-purple-600"
          />
        </div>
      </div>

      {/* Active Filters Summary */}
      {(filters.search || filters.strategy !== 'all' || filters.expiration !== 'all' || 
        filters.sentiment !== 'all' || filters.minConfidence > 0 || filters.showFavoritesOnly) && (
        <div className="mt-4 p-4 bg-purple-50 rounded-xl border-2 border-purple-200">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-purple-900">Active Filters:</span>
            {filters.search && (
              <span className="px-3 py-1 bg-purple-500 text-white rounded-full text-sm font-bold">
                Symbol: {filters.search}
              </span>
            )}
            {filters.strategy !== 'all' && (
              <span className="px-3 py-1 bg-indigo-500 text-white rounded-full text-sm font-bold">
                Strategy: {filters.strategy}
              </span>
            )}
            {filters.expiration !== 'all' && (
              <span className="px-3 py-1 bg-pink-500 text-white rounded-full text-sm font-bold">
                Expiration: {filters.expiration} days
              </span>
            )}
            {filters.sentiment !== 'all' && (
              <span className="px-3 py-1 bg-teal-500 text-white rounded-full text-sm font-bold">
                Sentiment: {filters.sentiment}
              </span>
            )}
            {filters.minConfidence > 0 && (
              <span className="px-3 py-1 bg-emerald-500 text-white rounded-full text-sm font-bold">
                Confidence ≥ {(filters.minConfidence * 100).toFixed(0)}%
              </span>
            )}
            {filters.showFavoritesOnly && (
              <span className="px-3 py-1 bg-yellow-500 text-white rounded-full text-sm font-bold">
                ⭐ Favorites Only
              </span>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
