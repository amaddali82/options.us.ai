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
    // Debounce: only update on blur or Enter
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
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">
            Trading Recommendations
          </h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-500">
            {totalCount} {totalCount === 1 ? 'recommendation' : 'recommendations'}
          </div>
          <div className="relative group">
            <HealthIndicator />
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        {/* Horizon Filter */}
        <div className="flex flex-col">
          <label
            htmlFor="horizon"
            className="text-xs font-medium text-gray-600 mb-1"
          >
            Horizon
          </label>
          <select
            id="horizon"
            value={filters.horizon}
            onChange={(e) =>
              onFiltersChange({ ...filters, horizon: e.target.value })
            }
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="all">All Horizons</option>
            <option value="intraday">Intraday</option>
            <option value="swing">Swing</option>
            <option value="position">Position</option>
          </select>
        </div>

        {/* Min Confidence Slider */}
        <div className="flex flex-col flex-1 min-w-[200px] max-w-[300px]">
          <label
            htmlFor="confidence"
            className="text-xs font-medium text-gray-600 mb-1"
          >
            Min Confidence: {(filters.minConfidence * 100).toFixed(0)}%
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
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
          />
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0%</span>
            <span>100%</span>
          </div>
        </div>

        {/* Symbol Search */}
        <div className="flex flex-col">
          <label
            htmlFor="symbol"
            className="text-xs font-medium text-gray-600 mb-1"
          >
            Symbol
          </label>
          <input
            id="symbol"
            type="text"
            placeholder="Search symbol..."
            value={localSymbol}
            onChange={(e) => handleSymbolChange(e.target.value)}
            onBlur={handleSymbolBlur}
            onKeyDown={handleSymbolKeyDown}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent w-40"
          />
        </div>

        {/* Sort Dropdown */}
        <div className="flex flex-col">
          <label
            htmlFor="sort"
            className="text-xs font-medium text-gray-600 mb-1"
          >
            Sort By
          </label>
          <select
            id="sort"
            value={filters.sort}
            onChange={(e) =>
              onFiltersChange({ ...filters, sort: e.target.value })
            }
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="rank">Rank (High to Low)</option>
            <option value="confidence">Confidence (High to Low)</option>
            <option value="time">Time (Newest First)</option>
          </select>
        </div>

        {/* Clear Filters */}
        {(filters.horizon !== 'all' ||
          filters.minConfidence > 0 ||
          filters.symbol.trim() !== '') && (
          <div className="flex items-end">
            <button
              onClick={() => {
                setLocalSymbol('')
                onFiltersChange({
                  horizon: 'all',
                  minConfidence: 0,
                  symbol: '',
                  sort: 'rank',
                })
              }}
              className="px-3 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
