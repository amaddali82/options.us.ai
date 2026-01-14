import { useState, useEffect } from 'react'
import axios from 'axios'
import { Activity, TrendingUp, AlertCircle } from 'lucide-react'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [symbol, setSymbol] = useState('AAPL')
  const [recommendation, setRecommendation] = useState(null)

  useEffect(() => {
    fetchHealth()
  }, [])

  const fetchHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`)
      setHealth(response.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to connect to API')
      setLoading(false)
    }
  }

  const fetchRecommendation = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/recommendations`, {
        symbol: symbol,
        timeframe: '1d',
        indicators: []
      })
      setRecommendation(response.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to fetch recommendation')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-12 text-center">
          <div className="flex items-center justify-center mb-4">
            <TrendingUp className="w-12 h-12 text-primary-500 mr-3" />
            <h1 className="text-4xl font-bold">Trading Intelligence</h1>
          </div>
          <p className="text-gray-400 text-lg">AI-Powered Trading Recommendations</p>
        </header>

        {/* Health Status */}
        <div className="mb-8 bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="flex items-center mb-2">
            <Activity className="w-5 h-5 mr-2 text-green-500" />
            <h2 className="text-xl font-semibold">System Status</h2>
          </div>
          {loading && !health && <p className="text-gray-400">Checking connection...</p>}
          {health && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-700 p-3 rounded">
                <p className="text-gray-400 text-sm">Status</p>
                <p className="text-green-400 font-semibold capitalize">{health.status}</p>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <p className="text-gray-400 text-sm">Service</p>
                <p className="font-semibold">{health.service}</p>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <p className="text-gray-400 text-sm">Version</p>
                <p className="font-semibold">{health.version}</p>
              </div>
              <div className="bg-gray-700 p-3 rounded">
                <p className="text-gray-400 text-sm">Last Check</p>
                <p className="font-semibold text-xs">{new Date(health.timestamp).toLocaleTimeString()}</p>
              </div>
            </div>
          )}
          {error && !health && (
            <div className="flex items-center text-red-400 mt-4">
              <AlertCircle className="w-5 h-5 mr-2" />
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Recommendation Form */}
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-8">
          <h2 className="text-2xl font-semibold mb-4">Get Recommendation</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="Enter symbol (e.g., AAPL)"
              className="flex-1 bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
            />
            <button
              onClick={fetchRecommendation}
              disabled={!symbol || loading}
              className="bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-2 rounded-lg font-semibold transition-colors"
            >
              {loading ? 'Loading...' : 'Analyze'}
            </button>
          </div>
        </div>

        {/* Recommendation Results */}
        {recommendation && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <h2 className="text-2xl font-semibold mb-4">Analysis Results</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-gray-400 text-sm mb-1">Symbol</p>
                <p className="text-2xl font-bold text-primary-400">{recommendation.symbol}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Recommendation</p>
                <p className={`text-2xl font-bold ${
                  recommendation.recommendation === 'BUY' ? 'text-green-400' :
                  recommendation.recommendation === 'SELL' ? 'text-red-400' :
                  'text-yellow-400'
                }`}>
                  {recommendation.recommendation}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Confidence</p>
                <div className="flex items-center">
                  <div className="flex-1 bg-gray-700 rounded-full h-3 mr-3">
                    <div
                      className="bg-primary-500 h-3 rounded-full"
                      style={{ width: `${recommendation.confidence * 100}%` }}
                    ></div>
                  </div>
                  <span className="font-semibold">{(recommendation.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-1">Timestamp</p>
                <p className="font-semibold">{new Date(recommendation.timestamp).toLocaleString()}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-400 text-sm mb-1">Reasoning</p>
                <p className="text-gray-200">{recommendation.reasoning}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
