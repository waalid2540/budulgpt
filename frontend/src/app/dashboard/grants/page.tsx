'use client'

import { useEffect, useState } from 'react'
import {
  DollarSign,
  Search,
  Filter,
  BookmarkPlus,
  Bookmark,
  ExternalLink,
  AlertCircle,
  Loader2,
  Sparkles,
  FileText,
  Calendar,
  MapPin,
  Building,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react'

interface Grant {
  id: string
  title: string
  description: string
  amount_min?: number
  amount_max?: number
  deadline?: string
  eligibility: string
  category: string
  organization: string
  location: string
  url: string
  created_at: string
}

interface SavedGrant {
  id: string
  grant: Grant
  status: string
  notes: string
  ai_summary?: string
  application_draft?: string
  created_at: string
  updated_at: string
}

export default function GrantFinderPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [grants, setGrants] = useState<Grant[]>([])
  const [savedGrants, setSavedGrants] = useState<SavedGrant[]>([])
  const [activeTab, setActiveTab] = useState<'search' | 'saved'>('search')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedLocation, setSelectedLocation] = useState('')
  const [minAmount, setMinAmount] = useState('')
  const [maxAmount, setMaxAmount] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [generatingAI, setGeneratingAI] = useState<string | null>(null)
  const [hasPro, setHasPro] = useState(false)

  const categories = [
    'Education',
    'Youth Programs',
    'Community Development',
    'Religious Activities',
    'Health & Wellness',
    'Arts & Culture',
    'Infrastructure',
    'Emergency Relief',
    'Environmental',
    'Technology'
  ]

  const statuses = [
    { value: 'interested', label: 'Interested', color: 'bg-blue-100 text-blue-700' },
    { value: 'researching', label: 'Researching', color: 'bg-yellow-100 text-yellow-700' },
    { value: 'preparing', label: 'Preparing', color: 'bg-orange-100 text-orange-700' },
    { value: 'submitted', label: 'Submitted', color: 'bg-purple-100 text-purple-700' },
    { value: 'awarded', label: 'Awarded', color: 'bg-green-100 text-green-700' },
    { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-700' }
  ]

  useEffect(() => {
    fetchSavedGrants()
    checkPlanAccess()
  }, [])

  const checkPlanAccess = () => {
    const org = localStorage.getItem('organization')
    if (org) {
      const orgData = JSON.parse(org)
      setHasPro(orgData.plan === 'pro' || orgData.plan === 'enterprise')
    }
  }

  const fetchSavedGrants = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/saved`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSavedGrants(data)
      }
    } catch (err) {
      console.error('Failed to fetch saved grants:', err)
    }
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const params = new URLSearchParams()

      if (searchQuery) params.append('query', searchQuery)
      if (selectedCategory) params.append('category', selectedCategory)
      if (selectedLocation) params.append('location', selectedLocation)
      if (minAmount) params.append('min_amount', minAmount)
      if (maxAmount) params.append('max_amount', maxAmount)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/search?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to search grants')
      }

      setGrants(data)
    } catch (err: any) {
      setError(err.message || 'Failed to search grants')
    } finally {
      setLoading(false)
    }
  }

  const saveGrant = async (grant: Grant) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/saved`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          grant_id: grant.id,
          status: 'interested',
          notes: ''
        })
      })

      if (response.ok) {
        await fetchSavedGrants()
      }
    } catch (err) {
      console.error('Failed to save grant:', err)
    }
  }

  const unsaveGrant = async (savedGrantId: string) => {
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/saved/${savedGrantId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      await fetchSavedGrants()
    } catch (err) {
      console.error('Failed to unsave grant:', err)
    }
  }

  const updateGrantStatus = async (savedGrantId: string, status: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/saved/${savedGrantId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status })
      })

      if (response.ok) {
        await fetchSavedGrants()
      }
    } catch (err) {
      console.error('Failed to update status:', err)
    }
  }

  const generateAISummary = async (savedGrantId: string) => {
    if (!hasPro) return

    setGeneratingAI(savedGrantId)
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/grants/saved/${savedGrantId}/generate-summary`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )

      if (response.ok) {
        await fetchSavedGrants()
      }
    } catch (err) {
      console.error('Failed to generate summary:', err)
    } finally {
      setGeneratingAI(null)
    }
  }

  const isGrantSaved = (grantId: string) => {
    return savedGrants.some(sg => sg.grant.id === grantId)
  }

  const formatAmount = (min?: number, max?: number) => {
    if (!min && !max) return 'Amount not specified'
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`
    if (min) return `From $${min.toLocaleString()}`
    return `Up to $${max?.toLocaleString()}`
  }

  const formatDeadline = (deadline?: string) => {
    if (!deadline) return 'Rolling deadline'
    const date = new Date(deadline)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
  }

  const GrantCard = ({ grant, saved = false, savedGrantId }: { grant: Grant, saved?: boolean, savedGrantId?: string }) => (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-800 mb-2">{grant.title}</h3>
          <div className="flex items-center space-x-2 text-sm text-slate-600">
            <Building className="w-4 h-4" />
            <span>{grant.organization}</span>
          </div>
        </div>
        {!saved ? (
          <button
            onClick={() => saveGrant(grant)}
            disabled={isGrantSaved(grant.id)}
            className={`p-2 rounded-lg transition-colors ${
              isGrantSaved(grant.id)
                ? 'bg-green-50 text-green-600'
                : 'text-slate-600 hover:text-green-600 hover:bg-slate-100'
            }`}
            title={isGrantSaved(grant.id) ? 'Already saved' : 'Save grant'}
          >
            {isGrantSaved(grant.id) ? <Bookmark className="w-5 h-5 fill-current" /> : <BookmarkPlus className="w-5 h-5" />}
          </button>
        ) : (
          <button
            onClick={() => savedGrantId && unsaveGrant(savedGrantId)}
            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            title="Remove from saved"
          >
            <XCircle className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Description */}
      <p className="text-slate-700 mb-4 line-clamp-3">{grant.description}</p>

      {/* Details */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center space-x-2 text-sm">
          <DollarSign className="w-4 h-4 text-green-600" />
          <span className="font-semibold text-slate-700">{formatAmount(grant.amount_min, grant.amount_max)}</span>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <Calendar className="w-4 h-4 text-blue-600" />
          <span className="text-slate-600">{formatDeadline(grant.deadline)}</span>
        </div>
        <div className="flex items-center space-x-2 text-sm">
          <MapPin className="w-4 h-4 text-purple-600" />
          <span className="text-slate-600">{grant.location}</span>
        </div>
      </div>

      {/* Category */}
      <div className="mb-4">
        <span className="px-3 py-1 bg-madina-green-100 text-madina-green-700 rounded-full text-xs font-medium">
          {grant.category}
        </span>
      </div>

      {/* Eligibility */}
      <div className="mb-4 p-3 bg-slate-50 rounded-lg">
        <h4 className="text-xs font-semibold text-slate-600 mb-1">Eligibility:</h4>
        <p className="text-sm text-slate-700">{grant.eligibility}</p>
      </div>

      {/* Action */}
      <a
        href={grant.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-center space-x-2 w-full px-4 py-2 bg-madina-green-500 text-white rounded-lg font-medium hover:bg-madina-green-600 transition-colors"
      >
        <span>View Grant</span>
        <ExternalLink className="w-4 h-4" />
      </a>
    </div>
  )

  const SavedGrantCard = ({ savedGrant }: { savedGrant: SavedGrant }) => {
    const statusInfo = statuses.find(s => s.value === savedGrant.status) || statuses[0]

    return (
      <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
        <GrantCard grant={savedGrant.grant} saved savedGrantId={savedGrant.id} />

        <div className="mt-4 pt-4 border-t border-slate-200 space-y-4">
          {/* Status Selector */}
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Status</label>
            <select
              value={savedGrant.status}
              onChange={(e) => updateGrantStatus(savedGrant.id, e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-madina-green-500"
            >
              {statuses.map(status => (
                <option key={status.value} value={status.value}>{status.label}</option>
              ))}
            </select>
          </div>

          {/* AI Features (Pro/Enterprise) */}
          {hasPro && (
            <div className="space-y-3">
              {/* AI Summary */}
              {savedGrant.ai_summary ? (
                <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                  <h4 className="text-sm font-semibold text-purple-800 mb-2 flex items-center space-x-2">
                    <Sparkles className="w-4 h-4" />
                    <span>AI Summary</span>
                  </h4>
                  <p className="text-sm text-slate-700">{savedGrant.ai_summary}</p>
                </div>
              ) : (
                <button
                  onClick={() => generateAISummary(savedGrant.id)}
                  disabled={generatingAI === savedGrant.id}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 transition-colors disabled:opacity-50"
                >
                  {generatingAI === savedGrant.id ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      <span>Generate AI Summary</span>
                    </>
                  )}
                </button>
              )}

              {/* Application Draft */}
              {savedGrant.application_draft && (
                <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                  <h4 className="text-sm font-semibold text-green-800 mb-2 flex items-center space-x-2">
                    <FileText className="w-4 h-4" />
                    <span>Application Draft</span>
                  </h4>
                  <p className="text-sm text-slate-700 whitespace-pre-wrap">{savedGrant.application_draft}</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Grant Finder</h1>
          <p className="text-slate-600">Discover funding opportunities for your organization</p>
        </div>
        {!hasPro && (
          <div className="text-right">
            <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-xs font-medium">
              View Only - Upgrade for AI Features
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('search')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'search'
              ? 'text-green-600 border-b-2 border-green-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Search Grants
        </button>
        <button
          onClick={() => setActiveTab('saved')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'saved'
              ? 'text-green-600 border-b-2 border-green-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Saved Grants ({savedGrants.length})
        </button>
      </div>

      {/* Search Tab */}
      {activeTab === 'search' && (
        <div>
          {/* Search Form */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200 mb-6">
            <form onSubmit={handleSearch} className="space-y-4">
              {/* Search Input */}
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search for grants..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              {/* Filter Toggle */}
              <button
                type="button"
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 text-sm font-medium"
              >
                <Filter className="w-4 h-4" />
                <span>{showFilters ? 'Hide' : 'Show'} Filters</span>
              </button>

              {/* Filters */}
              {showFilters && (
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Category</label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => setSelectedCategory(e.target.value)}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      <option value="">All Categories</option>
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Location</label>
                    <input
                      type="text"
                      placeholder="e.g., California"
                      value={selectedLocation}
                      onChange={(e) => setSelectedLocation(e.target.value)}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Min Amount</label>
                    <input
                      type="number"
                      placeholder="$0"
                      value={minAmount}
                      onChange={(e) => setMinAmount(e.target.value)}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Max Amount</label>
                    <input
                      type="number"
                      placeholder="$1,000,000"
                      value={maxAmount}
                      onChange={(e) => setMaxAmount(e.target.value)}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                </div>
              )}

              {/* Search Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-green-500 to-emerald-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:transform-none flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    <span>Search Grants</span>
                  </>
                )}
              </button>
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}
          </div>

          {/* Results */}
          {grants.length > 0 ? (
            <div>
              <p className="text-sm text-slate-600 mb-4">Found {grants.length} grants</p>
              <div className="grid lg:grid-cols-2 gap-6">
                {grants.map((grant) => (
                  <GrantCard key={grant.id} grant={grant} />
                ))}
              </div>
            </div>
          ) : (
            !loading && (
              <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
                <DollarSign className="w-16 h-16 text-slate-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-700 mb-2">
                  No grants found
                </h3>
                <p className="text-slate-600">
                  Try searching with different keywords or filters
                </p>
              </div>
            )
          )}
        </div>
      )}

      {/* Saved Tab */}
      {activeTab === 'saved' && (
        <div>
          {savedGrants.length > 0 ? (
            <div className="grid lg:grid-cols-2 gap-6">
              {savedGrants.map((savedGrant) => (
                <SavedGrantCard key={savedGrant.id} savedGrant={savedGrant} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <Bookmark className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                No saved grants yet
              </h3>
              <p className="text-slate-600">
                Save grants from the search results to track your applications
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
