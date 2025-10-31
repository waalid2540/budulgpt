'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Bell, Search, Trash2, Settings, ArrowLeft, Mail, MessageCircle, Smartphone, TrendingDown, Sparkles, Calendar, DollarSign, Star, MapPin } from 'lucide-react'

interface SavedSearch {
  id: string
  name: string
  destination: string
  budget_max: number
  hotel_rating: number
  alert_enabled: boolean
  last_checked: string
  best_price_found: number
  created_at: string
  alert_email: boolean
  alert_whatsapp: boolean
  alert_sms: boolean
}

interface Alert {
  id: string
  type: string
  message: string
  deal: {
    hotel_name: string
    old_price?: number
    new_price: number
  }
  sent_at: string
  is_read: boolean
}

export default function UmrahDealsDashboard() {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [userEmail, setUserEmail] = useState('user@example.com') // TODO: Get from auth
  const [showPreferencesModal, setShowPreferencesModal] = useState(false)
  const [selectedSearch, setSelectedSearch] = useState<SavedSearch | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)

      // Load saved searches
      const searchesRes = await fetch(`/api/v1/umrah-deals/saved-searches?user_email=${encodeURIComponent(userEmail)}`)
      const searchesData = await searchesRes.json()
      setSavedSearches(searchesData.searches || [])

      // Load alerts
      const alertsRes = await fetch(`/api/v1/umrah-deals/alerts?user_email=${encodeURIComponent(userEmail)}`)
      const alertsData = await alertsRes.json()
      setAlerts(alertsData.alerts || [])
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteSearch = async (searchId: string) => {
    if (!confirm('Are you sure you want to delete this saved search?')) return

    try {
      await fetch(`/api/v1/umrah-deals/saved-search/${searchId}`, {
        method: 'DELETE'
      })
      setSavedSearches(savedSearches.filter(s => s.id !== searchId))
    } catch (error) {
      console.error('Failed to delete search:', error)
      alert('Failed to delete search. Please try again.')
    }
  }

  const handleUpdatePreferences = async () => {
    if (!selectedSearch) return

    try {
      await fetch(`/api/v1/umrah-deals/saved-search/${selectedSearch.id}/alerts`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: selectedSearch.alert_email,
          whatsapp: selectedSearch.alert_whatsapp,
          sms: selectedSearch.alert_sms
        })
      })

      setShowPreferencesModal(false)
      alert('Alert preferences updated successfully!')
    } catch (error) {
      console.error('Failed to update preferences:', error)
      alert('Failed to update preferences. Please try again.')
    }
  }

  const openPreferencesModal = (search: SavedSearch) => {
    setSelectedSearch({ ...search })
    setShowPreferencesModal(true)
  }

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'price_drop':
        return <TrendingDown className="w-5 h-5 text-green-500" />
      case 'new_deal':
        return <Sparkles className="w-5 h-5 text-madina-gold-400" />
      default:
        return <Bell className="w-5 h-5 text-madina-green-500" />
    }
  }

  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-madina-green-400/20 to-madina-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-madina-green-100 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">م</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                  MadinaGPT
                </h1>
              </div>
            </Link>
            <div className="flex items-center space-x-4">
              <Link
                href="/umrah-deals"
                className="flex items-center space-x-2 text-slate-700 hover:text-madina-green-600 font-medium transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back to Search</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative pt-24 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-12">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                  <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                    Dashboard
                  </span>
                </h1>
                <p className="text-slate-600 text-lg">
                  Manage your saved searches and view price alerts
                </p>
              </div>
              <Link
                href="/umrah-deals"
                className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-xl transition-all duration-300 flex items-center space-x-2"
              >
                <Search className="w-5 h-5" />
                <span>New Search</span>
              </Link>
            </div>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-madina-green-500"></div>
            </div>
          ) : (
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Saved Searches */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-xl">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-800 flex items-center space-x-2">
                      <Search className="w-6 h-6 text-madina-green-500" />
                      <span>Saved Searches</span>
                    </h2>
                    <span className="text-sm text-slate-500 font-medium">
                      {savedSearches.length} {savedSearches.length === 1 ? 'search' : 'searches'}
                    </span>
                  </div>

                  {savedSearches.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gradient-to-br from-madina-green-100 to-madina-green-200 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Search className="w-8 h-8 text-madina-green-600" />
                      </div>
                      <p className="text-slate-600 mb-4">No saved searches yet</p>
                      <Link
                        href="/umrah-deals"
                        className="text-madina-green-600 hover:text-madina-green-700 font-semibold"
                      >
                        Create your first search
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {savedSearches.map((search) => (
                        <div
                          key={search.id}
                          className="bg-white rounded-xl p-5 border border-madina-green-100 hover:shadow-lg transition-all duration-300"
                        >
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="text-lg font-bold text-slate-800 mb-2">
                                {search.name}
                              </h3>
                              <div className="flex flex-wrap gap-3 text-sm text-slate-600">
                                <div className="flex items-center space-x-1">
                                  <MapPin className="w-4 h-4 text-madina-green-500" />
                                  <span>{search.destination}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <DollarSign className="w-4 h-4 text-madina-gold-400" />
                                  <span>Up to ${search.budget_max}</span>
                                </div>
                                <div className="flex items-center space-x-1">
                                  <Star className="w-4 h-4 text-yellow-500" />
                                  <span>{search.hotel_rating}+ stars</span>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => openPreferencesModal(search)}
                                className="p-2 hover:bg-madina-green-50 rounded-lg transition-colors"
                                title="Manage alert preferences"
                              >
                                <Settings className="w-5 h-5 text-slate-600" />
                              </button>
                              <button
                                onClick={() => handleDeleteSearch(search.id)}
                                className="p-2 hover:bg-red-50 rounded-lg transition-colors"
                                title="Delete search"
                              >
                                <Trash2 className="w-5 h-5 text-red-600" />
                              </button>
                            </div>
                          </div>

                          <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                            <div className="flex items-center space-x-4 text-sm">
                              <div className="flex items-center space-x-1">
                                {search.alert_email && <Mail className="w-4 h-4 text-madina-green-500" />}
                                {search.alert_whatsapp && <MessageCircle className="w-4 h-4 text-green-500" />}
                                {search.alert_sms && <Smartphone className="w-4 h-4 text-blue-500" />}
                              </div>
                              {search.best_price_found && (
                                <div className="text-madina-green-600 font-semibold">
                                  Best price: ${search.best_price_found}
                                </div>
                              )}
                            </div>
                            <div className="flex items-center space-x-2 text-xs text-slate-500">
                              <Calendar className="w-3 h-3" />
                              <span>Last checked: {new Date(search.last_checked).toLocaleDateString()}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Recent Alerts */}
              <div className="space-y-6">
                <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-xl">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-slate-800 flex items-center space-x-2">
                      <Bell className="w-6 h-6 text-madina-green-500" />
                      <span>Recent Alerts</span>
                    </h2>
                    {alerts.filter(a => !a.is_read).length > 0 && (
                      <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {alerts.filter(a => !a.is_read).length} new
                      </span>
                    )}
                  </div>

                  {alerts.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="w-16 h-16 bg-gradient-to-br from-madina-gold-100 to-madina-gold-200 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Bell className="w-8 h-8 text-madina-gold-600" />
                      </div>
                      <p className="text-slate-600 text-sm">No alerts yet</p>
                      <p className="text-slate-500 text-xs mt-2">
                        You'll be notified when prices drop
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-[600px] overflow-y-auto">
                      {alerts.map((alert) => (
                        <div
                          key={alert.id}
                          className={`p-4 rounded-xl border transition-all duration-300 ${
                            alert.is_read
                              ? 'bg-white border-slate-100'
                              : 'bg-gradient-to-r from-madina-green-50 to-madina-gold-50 border-madina-green-200 shadow-md'
                          }`}
                        >
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 mt-1">
                              {getAlertIcon(alert.type)}
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-semibold text-slate-800 mb-1">
                                {alert.message}
                              </p>
                              <div className="text-xs text-slate-600 mb-2">
                                <span className="font-medium">{alert.deal.hotel_name}</span>
                                {alert.deal.old_price && (
                                  <span className="ml-2">
                                    <span className="line-through text-slate-400">${alert.deal.old_price}</span>
                                    <span className="ml-1 text-green-600 font-bold">${alert.deal.new_price}</span>
                                  </span>
                                )}
                              </div>
                              <div className="flex items-center space-x-1 text-xs text-slate-500">
                                <Calendar className="w-3 h-3" />
                                <span>{new Date(alert.sent_at).toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Quick Stats */}
                <div className="bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-2xl p-6 text-white shadow-xl">
                  <h3 className="text-lg font-bold mb-4">Your Stats</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-madina-green-100 text-sm">Active Searches</span>
                      <span className="text-2xl font-bold">{savedSearches.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-madina-green-100 text-sm">Total Alerts</span>
                      <span className="text-2xl font-bold">{alerts.length}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-madina-green-100 text-sm">Unread Alerts</span>
                      <span className="text-2xl font-bold">{alerts.filter(a => !a.is_read).length}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Alert Preferences Modal */}
      {showPreferencesModal && selectedSearch && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-8 shadow-2xl transform transition-all">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-slate-800 flex items-center space-x-2">
                <Settings className="w-6 h-6 text-madina-green-500" />
                <span>Alert Preferences</span>
              </h3>
              <button
                onClick={() => setShowPreferencesModal(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6">
              <p className="text-slate-600 mb-4">
                Managing alerts for: <span className="font-bold text-slate-800">{selectedSearch.name}</span>
              </p>

              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Mail className="w-5 h-5 text-madina-green-500" />
                    <div>
                      <div className="font-semibold text-slate-800">Email Alerts</div>
                      <div className="text-xs text-slate-500">Get notified via email</div>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedSearch.alert_email}
                      onChange={(e) => setSelectedSearch({ ...selectedSearch, alert_email: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-madina-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-madina-green-500"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <MessageCircle className="w-5 h-5 text-green-500" />
                    <div>
                      <div className="font-semibold text-slate-800">WhatsApp Alerts</div>
                      <div className="text-xs text-slate-500">Get notified via WhatsApp</div>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedSearch.alert_whatsapp}
                      onChange={(e) => setSelectedSearch({ ...selectedSearch, alert_whatsapp: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-500"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <Smartphone className="w-5 h-5 text-blue-500" />
                    <div>
                      <div className="font-semibold text-slate-800">SMS Alerts</div>
                      <div className="text-xs text-slate-500">Get notified via text message</div>
                    </div>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedSearch.alert_sms}
                      onChange={(e) => setSelectedSearch({ ...selectedSearch, alert_sms: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-slate-300 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                  </label>
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowPreferencesModal(false)}
                className="flex-1 px-6 py-3 border-2 border-slate-200 text-slate-700 rounded-xl font-semibold hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUpdatePreferences}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all duration-300"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
