import { useQuery } from '@tanstack/react-query'
import { checkHealth } from '../api'

export default function HealthIndicator() {
  const { data, isError } = useQuery({
    queryKey: ['health'],
    queryFn: checkHealth,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  })

  const isHealthy = !isError && data?.status === 'ok'
  const isDegraded = !isError && data?.status === 'degraded'

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5">
        {/* Status dot */}
        <div
          className={`w-2 h-2 rounded-full transition-colors ${
            isHealthy
              ? 'bg-success-500 animate-pulse'
              : isDegraded
              ? 'bg-warning-500'
              : 'bg-danger-500'
          }`}
          title={
            isHealthy
              ? 'Backend healthy'
              : isDegraded
              ? 'Backend degraded'
              : 'Backend offline'
          }
        />
        
        {/* Status text (optional, shows on hover) */}
        <span className="text-xs text-gray-500 hidden sm:inline">
          {isHealthy ? 'Online' : isDegraded ? 'Degraded' : 'Offline'}
        </span>
      </div>

      {/* Detailed status on hover */}
      {data && (
        <div className="hidden group-hover:block absolute top-full right-0 mt-2 p-2 bg-gray-900 text-white text-xs rounded shadow-lg z-50 whitespace-nowrap">
          <div>Status: {data.status}</div>
          {data.database && <div>DB: {data.database}</div>}
          <div>
            Last check: {new Date(data.timestamp).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  )
}
