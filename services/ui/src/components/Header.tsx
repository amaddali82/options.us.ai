import { useQuery } from '@tanstack/react-query'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface SystemStatus {
  database: string
  scheduler: string
  lastUpdate: string
}

interface HeaderProps {
  lastRefresh: Date | null
  onRefresh: () => Promise<void>
  isRefreshing: boolean
}

export default function Header({ lastRefresh, onRefresh, isRefreshing }: HeaderProps) {
  // Fetch system status
  const { data: status } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/health`)
      return response.json() as Promise<SystemStatus>
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    }).format(date)
  }

  return (
    <header className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 text-white shadow-2xl border-b-4 border-purple-800">
      <div className="max-w-[1600px] mx-auto px-8 py-6">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div>
            <h1 className="text-4xl font-black tracking-tight mb-2">
              🚀 Options Trading Intelligence
            </h1>
            <p className="text-purple-100 text-sm font-semibold">
              AI-Powered Real-Time Options Analysis • ML Predictions • Live Market Data
            </p>
          </div>

          {/* Status and Controls */}
          <div className="flex items-center gap-6">
            {/* System Status */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4 border border-white/20">
              <div className="text-xs font-bold text-purple-200 mb-2">SYSTEM STATUS</div>
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                  <span className="font-semibold">Database: </span>
                  <span className="text-green-300">{status?.database || 'Connected'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
                  <span className="font-semibold">Scheduler: </span>
                  <span className="text-green-300">Active</span>
                </div>
              </div>
            </div>

            {/* Last Update Info */}
            <div className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4 border border-white/20">
              <div className="text-xs font-bold text-purple-200 mb-2">LAST DATA SYNC</div>
              <div className="text-xl font-black text-white">
                {lastRefresh ? formatTime(lastRefresh) : 'Never'}
              </div>
              <div className="text-xs text-purple-200 mt-1">
                Auto-refresh: Every 10-30 min
              </div>
            </div>

            {/* Manual Refresh Button */}
            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className={`px-8 py-4 rounded-xl font-black text-lg transition-all shadow-xl ${
                isRefreshing
                  ? 'bg-gray-400 text-gray-700 cursor-not-allowed'
                  : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 hover:scale-105 active:scale-95 shadow-emerald-500/50'
              }`}
            >
              {isRefreshing ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Syncing...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  🔄 Sync Now
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
