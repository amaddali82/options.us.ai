import { useState } from 'react'
import type { FiltersState } from '../types'
import HealthIndicator from './HealthIndicator'

interface FiltersBarProps {
  filters: FiltersState
  onFiltersChange: (filters: FiltersState) => void
  totalCount: number
  expiryDates: string[]
  onRefresh?: () => Promise<void>  // Refresh callback
}

export default function FiltersBar({
  filters,
  onFiltersChange,
  totalCount,
  expiryDates,
  onRefresh,
}: FiltersBarProps) {
  const [localSymbol, setLocalSymbol] = useState(filters.symbol)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null)

  const handleSymbolChange = (value: string) => {
    setLocalSymbol(value)
  }

  const handleSymbolBlur = () => {
    if (localSymbol !== filters.symbol) {
      onFiltersChange({ ...filters, symbol: localSymbol })
    }
  }

  const handleSymbolKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onFiltersChange({ ...filters, symbol: localSymbol })
    }
  }

  const handleRefresh = async () => {
    if (!onRefresh || isRefreshing) return
    
    setIsRefreshing(true)
    try {
      await onRefresh()
      setLastRefresh(new Date())
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 border-b-4 border-purple-700 px-8 py-6 shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-5xl font-black text-white drop-shadow-2xl tracking-tight">
            🚀 Options Trading Dashboard
          </h1>
          <p className="text-lg text-purple-200 mt-2 font-semibold">Live market data • Real-time updates • CALL options only</p>
        </div>
        <div className="flex items-center gap-6">
          {/* Refresh Button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className={`px-8 py-4 text-lg font-bold rounded-2xl transition-all shadow-xl border-2 ${
              isRefreshing
                ? 'bg-gray-400 text-gray-700 border-gray-500 cursor-not-allowed'
                : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white border-emerald-400 hover:from-emerald-600 hover:to-teal-700 hover:shadow-2xl hover:scale-105 active:scale-95'
            }`}
          >
            {isRefreshing ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Updating...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                🔄 Refresh Data
              </span>
            )}
          </button>
          
          {lastRefresh && (
            <div className="text-xs text-purple-200">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </div>
          )}
          
          <div className="px-8 py-4 bg-white rounded-2xl shadow-2xl border-4 border-purple-300">
            <div className="text-xs text-purple-700 uppercase tracking-widest font-black">Total Options</div>
            <div className="text-4xl font-black text-purple-900">{totalCount}</div>
          </div>
          <HealthIndicator />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 bg-gradient-to-br from-white via-purple-50 to-pink-50 p-8 rounded-2xl shadow-2xl border-4 border-purple-300">
        {/* Symbol Search */}
        <div className="flex flex-col">
          <label htmlFor="symbol" className="text-sm font-black text-purple-900 mb-2 uppercase tracking-widest">
            🔍 Symbol
          </label>
          <input
            id="symbol"
            type="text"
            placeholder="e.g., AAPL, TSLA..."
            value={localSymbol}
            onChange={(e) => handleSymbolChange(e.target.value)}
            onBlur={handleSymbolBlur}
            onKeyDown={handleSymbolKeyDown}
            className="px-5 py-3 border-3 border-purple-300 rounded-xl text-base font-semibold focus:outline-none focus:ring-4 focus:ring-purple-500 focus:border-purple-500 transition-all shadow-lg"
          />
        </div>

        {/* Min Confidence */}
        <div className="flex flex-col">
          <label 
            htmlFor="confidence" 
            className="text-sm font-black text-purple-900 mb-2 uppercase tracking-widest"
            title="Filter by minimum confidence level for option targets (TP1 and TP2)"
          >
            📈 Target Confidence: <span className="text-purple-700 text-lg">{(filters.minConfidence * 100).toFixed(0)}%+</span>
          </label>
          <input
            id="confidence"
            type="range"
            min="0"
            max="100"
            step="5"
            value={filters.minConfidence * 100}
            onChange={(e) =>
              onFiltersChange({
                ...filters,
                minConfidence: parseInt(e.target.value) / 100,
              })
            }
            className="w-full h-4 bg-gradient-to-r from-purple-300 via-pink-300 to-purple-300 rounded-lg appearance-none cursor-pointer accent-purple-600 mt-1 shadow-lg"
          />
          <div className="flex justify-between text-xs text-purple-700 mt-1 font-bold">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Expiry Filter */}
        <div className="flex flex-col">
          <label 
            htmlFor="expiry" 
            className="text-sm font-black text-purple-900 mb-2 uppercase tracking-widest"
            title="Filter by option expiry date"
          >
            📅 Expiry Date
          </label>
          <select
            id="expiry"
            value={filters.expiry}
            onChange={(e) =>
              onFiltersChange({ ...filters, expiry: e.target.value })
            }
            className="px-5 py-3 border-3 border-purple-300 rounded-xl text-base font-semibold focus:outline-none focus:ring-4 focus:ring-purple-500 focus:border-purple-500 bg-white transition-all shadow-lg"
          >
            <option value="all">All Expiry Dates</option>
            {expiryDates.map(date => (
              <option key={date} value={date}>
                {new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
              </option>
            ))}
          </select>
        </div>

        {/* Clear Filters Button */}
        <div className="flex flex-col justify-end">
          {(filters.expiry !== 'all' ||
            filters.minConfidence > 0 ||
            filters.symbol.trim() !== '') && (
            <button
              onClick={() => {
                setLocalSymbol('')
                onFiltersChange({
                  horizon: 'all',
                  minConfidence: 0,
                  symbol: '',
                  sort: 'rank',
                  optionsOnly: true,
                  expiry: 'all',
                  favorites: filters.favorites,
                })
              }}
              className="px-8 py-3 text-lg font-black text-white bg-gradient-to-r from-red-600 via-red-700 to-pink-600 rounded-xl hover:from-red-700 hover:via-red-800 hover:to-pink-700 transition-all shadow-xl hover:shadow-2xl hover:scale-105 active:scale-95"
            >
              ✖ Clear Filters
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
