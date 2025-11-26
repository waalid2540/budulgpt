'use client'

import { useEffect, useState } from 'react'
import {
  MapPin,
  Search,
  Calendar,
  DollarSign,
  Users,
  Star,
  ExternalLink,
  Bell,
  BellOff,
  Loader2,
  AlertCircle,
  Plane,
  Hotel,
  Sparkles
} from 'lucide-react'

interface SearchResult {
  id: string
  query: string
  results: any
  created_at: string
}

interface SavedSearch {
  id: string
  query: string
  departure_city?: string
  month?: string
  budget?: number
  alert_enabled: boolean
  created_at: string
}

export default function UmrahHajjPage() {
  const [formData, setFormData] = useState({
    query: '',
    departure_city: '',
    month: '',
    budget: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchResults, setSearchResults] = useState<any>(null)
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [usageInfo, setUsageInfo] = useState({ used: 0, limit: 0, plan: 'Basic' })
  const [activeTab, setActiveTab] = useState<'search' | 'saved'>('search')

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]

  useEffect(() => {
    fetchUsageInfo()
    fetchSavedSearches()
  }, [])

  const fetchUsageInfo = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/usage`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setUsageInfo(data)
      }
    } catch (err) {
      console.error('Failed to fetch usage info:', err)
    }
  }

  const fetchSavedSearches = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/saved-searches`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSavedSearches(data)
      }
    } catch (err) {
      console.error('Failed to fetch saved searches:', err)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const params = new URLSearchParams()

      params.append('query', formData.query)
      if (formData.departure_city) params.append('departure_city', formData.departure_city)
      if (formData.month) params.append('month', formData.month)
      if (formData.budget) params.append('budget', formData.budget)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/search?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to search deals')
      }

      setSearchResults(data)
      await fetchUsageInfo()
    } catch (err: any) {
      setError(err.message || 'Failed to search for Umrah deals')
    } finally {
      setLoading(false)
    }
  }

  const saveSearch = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/saved-searches`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: formData.query,
          departure_city: formData.departure_city || null,
          month: formData.month || null,
          budget: formData.budget ? parseInt(formData.budget) : null,
          alert_enabled: true
        })
      })

      if (response.ok) {
        await fetchSavedSearches()
      }
    } catch (err) {
      console.error('Failed to save search:', err)
    }
  }

  const toggleAlert = async (searchId: string, currentState: boolean) => {
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/saved-searches/${searchId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          alert_enabled: !currentState
        })
      })
      await fetchSavedSearches()
    } catch (err) {
      console.error('Failed to toggle alert:', err)
    }
  }

  const deleteSearch = async (searchId: string) => {
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/umrah/saved-searches/${searchId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      await fetchSavedSearches()
    } catch (err) {
      console.error('Failed to delete search:', err)
    }
  }

  const canSaveSearches = usageInfo.plan === 'Pro' || usageInfo.plan === 'Enterprise' || usageInfo.plan === 'pro' || usageInfo.plan === 'enterprise'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Umrah & Hajj Alerts</h1>
          <p className="text-slate-600">Find the best travel deals for your spiritual journey</p>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl">
            <Sparkles className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-semibold text-slate-700">
              {usageInfo.used} / {usageInfo.limit === -1 ? '∞' : usageInfo.limit} searches
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{usageInfo.plan} Plan</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('search')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'search'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Search Deals
        </button>
        <button
          onClick={() => setActiveTab('saved')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'saved'
              ? 'text-blue-600 border-b-2 border-blue-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Saved Searches ({savedSearches.length})
        </button>
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div>
          {/* Search Form */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 mb-6">
            <form onSubmit={handleSearch} className="space-y-4">
              {/* Main Query */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  What are you looking for?
                </label>
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    placeholder="e.g., Umrah packages December 2025"
                    value={formData.query}
                    onChange={(e) => setFormData({ ...formData, query: e.target.value })}
                    required
                    className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Filters */}
              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Departure City
                  </label>
                  <input
                    type="text"
                    placeholder="e.g., New York"
                    value={formData.departure_city}
                    onChange={(e) => setFormData({ ...formData, departure_city: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Travel Month
                  </label>
                  <select
                    value={formData.month}
                    onChange={(e) => setFormData({ ...formData, month: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Month</option>
                    {months.map(month => (
                      <option key={month} value={month}>{month}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Budget (USD)
                  </label>
                  <input
                    type="number"
                    placeholder="e.g., 5000"
                    value={formData.budget}
                    onChange={(e) => setFormData({ ...formData, budget: e.target.value })}
                    className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              {/* Search Button */}
              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={loading || (usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit)}
                  className="flex-1 bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:transform-none flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Searching...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-5 h-5" />
                      <span>Search Deals</span>
                    </>
                  )}
                </button>

                {canSaveSearches && searchResults && (
                  <button
                    type="button"
                    onClick={saveSearch}
                    className="px-6 py-3 bg-white border-2 border-blue-500 text-blue-600 rounded-xl font-semibold hover:bg-blue-50 transition-colors flex items-center space-x-2"
                  >
                    <Bell className="w-5 h-5" />
                    <span>Save & Alert</span>
                  </button>
                )}
              </div>

              {usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit && (
                <p className="text-sm text-center text-amber-600">
                  Monthly search limit reached. Upgrade your plan for more searches.
                </p>
              )}
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {!canSaveSearches && (
              <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
                <p className="text-sm text-amber-700">
                  <strong>Upgrade to Pro</strong> to save searches and enable price alerts
                </p>
              </div>
            )}
          </div>

          {/* Search Results */}
          {searchResults && (
            <div className="bg-white rounded-2xl p-6 border border-slate-200">
              <h2 className="text-xl font-bold text-slate-800 mb-6 flex items-center space-x-2">
                <Sparkles className="w-6 h-6 text-blue-500" />
                <span>AI-Powered Search Results</span>
              </h2>

              <div className="prose prose-slate max-w-none">
                <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl border border-blue-200">
                  <p className="text-slate-700 whitespace-pre-wrap leading-relaxed">
                    {searchResults.results}
                  </p>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between pt-6 border-t border-slate-200">
                <p className="text-sm text-slate-500">
                  Powered by Perplexity AI • Real-time data
                </p>
                <div className="flex items-center space-x-2">
                  <Plane className="w-4 h-4 text-blue-500" />
                  <Hotel className="w-4 h-4 text-blue-500" />
                  <MapPin className="w-4 h-4 text-blue-500" />
                </div>
              </div>
            </div>
          )}

          {!searchResults && !loading && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-12 border border-blue-100 text-center">
              <MapPin className="w-16 h-16 text-blue-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                Ready to find your perfect journey?
              </h3>
              <p className="text-slate-600">
                Enter your search criteria to discover the best Umrah and Hajj packages
              </p>
            </div>
          )}
        </div>
      )}

      {/* Saved Searches Tab */}
      {activeTab === 'saved' && (
        <div>
          {savedSearches.length > 0 ? (
            <div className="space-y-4">
              {savedSearches.map((search) => (
                <div
                  key={search.id}
                  className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-bold text-slate-800 mb-2">{search.query}</h3>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {search.departure_city && (
                          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium flex items-center space-x-1">
                            <MapPin className="w-3 h-3" />
                            <span>{search.departure_city}</span>
                          </span>
                        )}
                        {search.month && (
                          <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium flex items-center space-x-1">
                            <Calendar className="w-3 h-3" />
                            <span>{search.month}</span>
                          </span>
                        )}
                        {search.budget && (
                          <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium flex items-center space-x-1">
                            <DollarSign className="w-3 h-3" />
                            <span>${search.budget.toLocaleString()}</span>
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-slate-500">
                        Saved {new Date(search.created_at).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleAlert(search.id, search.alert_enabled)}
                        className={`p-2 rounded-lg transition-colors ${
                          search.alert_enabled
                            ? 'bg-green-50 text-green-600'
                            : 'bg-slate-100 text-slate-400'
                        }`}
                        title={search.alert_enabled ? 'Alerts enabled' : 'Alerts disabled'}
                      >
                        {search.alert_enabled ? (
                          <Bell className="w-5 h-5 fill-current" />
                        ) : (
                          <BellOff className="w-5 h-5" />
                        )}
                      </button>
                      <button
                        onClick={() => deleteSearch(search.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <Bell className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                No saved searches yet
              </h3>
              <p className="text-slate-600 mb-4">
                Save your searches to track prices and get notified of new deals
              </p>
              {!canSaveSearches && (
                <p className="text-sm text-amber-600">
                  Upgrade to Pro to enable saved searches and price alerts
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
