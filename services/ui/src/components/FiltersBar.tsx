import { useState } from 'react'
import type { FiltersState } from '../types'
import HealthIndicator from './HealthIndicator'

interface FiltersBarProps {
  filters: FiltersState
  onFiltersChange: (filters: FiltersState) => void
  totalCount: number
}

export default function FiltersBar({
  filters,
  onFiltersChange,
  totalCount,
}: FiltersBarProps) {
  const [localSymbol, setLocalSymbol] = useState(filters.symbol)

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

  return (
    <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 border-b border-gray-200 px-6 py-5 shadow-sm">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            📊 Options Trading Dashboard
          </h1>
          <p className="text-sm text-gray-600 mt-1">Real-time CALL options with live market data</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-4 py-2 bg-white rounded-lg shadow-sm">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Total Options</div>
            <div className="text-2xl font-bold text-blue-600">{totalCount}</div>
          </div>
          <HealthIndicator />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 bg-white p-4 rounded-lg shadow-sm">
        {/* Symbol Search */}
        <div className="flex flex-col">
          <label htmlFor="symbol" className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
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
            className="px-4 py-2 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent transition-all"
          />
        </div>

        {/* Min Confidence */}
        <div className="flex flex-col">
          <label htmlFor="confidence" className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
            📈 Min Confidence: <span className="text-blue-600">{(filters.minConfidence * 100).toFixed(0)}%</span>
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
            className="w-full h-3 bg-gradient-to-r from-gray-200 to-blue-200 rounded-lg appearance-none cursor-pointer accent-blue-600 mt-1"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Horizon Filter */}
        <div className="flex flex-col">
          <label htmlFor="horizon" className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
            ⏱️ Horizon
          </label>
          <select
            id="horizon"
            value={filters.horizon}
            onChange={(e) =>
              onFiltersChange({ ...filters, horizon: e.target.value })
            }
            className="px-4 py-2 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent bg-white transition-all"
          >
            <option value="all">All Horizons</option>
            <option value="intraday">Intraday</option>
            <option value="swing">Swing</option>
            <option value="position">Position</option>
          </select>
        </div>

        {/* Sort Dropdown */}
        <div className="flex flex-col">
          <label htmlFor="sort" className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
            🔢 Sort By
          </label>
          <select
            id="sort"
            value={filters.sort}
            onChange={(e) =>
              onFiltersChange({ ...filters, sort: e.target.value })
            }
            className="px-4 py-2 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent bg-white transition-all"
          >
            <option value="rank">🏆 Rank (Best First)</option>
            <option value="confidence">💪 Confidence (High to Low)</option>
            <option value="asof">🕒 Time (Newest First)</option>
          </select>
        </div>

        {/* Clear Filters Button */}
        <div className="flex flex-col justify-end">
          {(filters.horizon !== 'all' ||
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
                })
              }}
              className="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-red-500 to-pink-500 rounded-lg hover:from-red-600 hover:to-pink-600 transition-all shadow-sm"
            >
              ✖ Clear Filters
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
