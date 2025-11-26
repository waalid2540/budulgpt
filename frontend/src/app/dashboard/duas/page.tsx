'use client'

import { useEffect, useState } from 'react'
import { Heart, Sparkles, Copy, Check, AlertCircle, Loader2, Star, BookmarkPlus, Filter } from 'lucide-react'

interface DuaGeneration {
  id: string
  arabic_text: string
  transliteration: string
  english_translation: string
  theme: string
  occasion: string
  is_favorite: boolean
  created_at: string
}

export default function DuaStudioPage() {
  const [formData, setFormData] = useState({
    theme: '',
    occasion: '',
    customTheme: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [currentDua, setCurrentDua] = useState<DuaGeneration | null>(null)
  const [savedDuas, setSavedDuas] = useState<DuaGeneration[]>([])
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [usageInfo, setUsageInfo] = useState({ used: 0, limit: 0, plan: 'Basic' })
  const [activeTab, setActiveTab] = useState<'generate' | 'saved'>('generate')
  const [filterFavorites, setFilterFavorites] = useState(false)

  const themes = [
    'Gratitude & Thankfulness',
    'Seeking Guidance',
    'Protection & Safety',
    'Forgiveness & Repentance',
    'Patience & Strength',
    'Health & Healing',
    'Success & Prosperity',
    'Knowledge & Wisdom',
    'Family & Relationships',
    'Custom'
  ]

  const occasions = [
    'Morning',
    'Evening',
    'Before Sleep',
    'After Prayer',
    'During Difficulty',
    'Before Travel',
    'Before Exam/Work',
    'For Parents',
    'For Children',
    'General'
  ]

  useEffect(() => {
    fetchUsageInfo()
    fetchSavedDuas()
  }, [])

  const fetchUsageInfo = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/duas/usage`, {
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

  const fetchSavedDuas = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/duas/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSavedDuas(data)
      }
    } catch (err) {
      console.error('Failed to fetch saved duas:', err)
    }
  }

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const theme = formData.theme === 'Custom' ? formData.customTheme : formData.theme

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/duas/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          theme,
          occasion: formData.occasion
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate du\'a')
      }

      setCurrentDua(data)
      setSuccess('Du\'a generated successfully!')
      await fetchUsageInfo()
      await fetchSavedDuas()

    } catch (err: any) {
      setError(err.message || 'Failed to generate du\'a')
    } finally {
      setLoading(false)
    }
  }

  const toggleFavorite = async (duaId: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/duas/${duaId}/favorite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        // Update local state
        if (currentDua?.id === duaId) {
          setCurrentDua({ ...currentDua, is_favorite: !currentDua.is_favorite })
        }
        setSavedDuas(savedDuas.map(dua =>
          dua.id === duaId ? { ...dua, is_favorite: !dua.is_favorite } : dua
        ))
      }
    } catch (err) {
      console.error('Failed to toggle favorite:', err)
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const DuaCard = ({ dua }: { dua: DuaGeneration }) => (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Arabic Text */}
      <div className="mb-6 p-6 bg-gradient-to-r from-madina-green-50 to-madina-gold-50 rounded-xl">
        <p className="text-2xl text-right leading-loose font-arabic text-slate-800" dir="rtl">
          {dua.arabic_text}
        </p>
      </div>

      {/* Transliteration */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-slate-600 mb-2">Transliteration:</h4>
        <p className="text-slate-700 italic leading-relaxed">{dua.transliteration}</p>
      </div>

      {/* English Translation */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-slate-600 mb-2">Translation:</h4>
        <p className="text-slate-700 leading-relaxed">{dua.english_translation}</p>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-madina-green-100 text-madina-green-700 rounded-full text-xs font-medium">
            {dua.theme}
          </span>
          <span className="px-3 py-1 bg-madina-gold-100 text-madina-gold-700 rounded-full text-xs font-medium">
            {dua.occasion}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => copyToClipboard(
              `${dua.arabic_text}\n\n${dua.transliteration}\n\n${dua.english_translation}`,
              dua.id
            )}
            className="p-2 text-slate-600 hover:text-madina-green-600 hover:bg-slate-100 rounded-lg transition-colors"
            title="Copy to clipboard"
          >
            {copiedId === dua.id ? (
              <Check className="w-5 h-5 text-green-600" />
            ) : (
              <Copy className="w-5 h-5" />
            )}
          </button>
          <button
            onClick={() => toggleFavorite(dua.id)}
            className={`p-2 rounded-lg transition-colors ${
              dua.is_favorite
                ? 'text-red-500 bg-red-50 hover:bg-red-100'
                : 'text-slate-600 hover:text-red-500 hover:bg-slate-100'
            }`}
            title={dua.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart className={`w-5 h-5 ${dua.is_favorite ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  )

  const filteredDuas = filterFavorites
    ? savedDuas.filter(dua => dua.is_favorite)
    : savedDuas

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Du&apos;a & Dhikr Studio</h1>
          <p className="text-slate-600">Generate beautiful Islamic supplications with AI</p>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl">
            <Sparkles className="w-5 h-5 text-madina-gold-500" />
            <span className="text-sm font-semibold text-slate-700">
              {usageInfo.used} / {usageInfo.limit === -1 ? '∞' : usageInfo.limit} this month
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{usageInfo.plan} Plan</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200">
        <button
          onClick={() => setActiveTab('generate')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'generate'
              ? 'text-madina-green-600 border-b-2 border-madina-green-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Generate New
        </button>
        <button
          onClick={() => setActiveTab('saved')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'saved'
              ? 'text-madina-green-600 border-b-2 border-madina-green-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          My Du&apos;as ({savedDuas.length})
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Generation Form */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-6">Create New Du&apos;a</h2>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start space-x-3">
                <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-green-700">{success}</p>
              </div>
            )}

            <form onSubmit={handleGenerate} className="space-y-6">
              {/* Theme Selection */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Theme
                </label>
                <select
                  value={formData.theme}
                  onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                >
                  <option value="">Select a theme...</option>
                  {themes.map((theme) => (
                    <option key={theme} value={theme}>{theme}</option>
                  ))}
                </select>
              </div>

              {/* Custom Theme Input */}
              {formData.theme === 'Custom' && (
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-2">
                    Custom Theme
                  </label>
                  <input
                    type="text"
                    value={formData.customTheme}
                    onChange={(e) => setFormData({ ...formData, customTheme: e.target.value })}
                    placeholder="Enter your custom theme..."
                    required
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Occasion Selection */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Occasion
                </label>
                <select
                  value={formData.occasion}
                  onChange={(e) => setFormData({ ...formData, occasion: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                >
                  <option value="">Select an occasion...</option>
                  {occasions.map((occasion) => (
                    <option key={occasion} value={occasion}>{occasion}</option>
                  ))}
                </select>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || (usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit)}
                className="w-full bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Du&apos;a</span>
                  </>
                )}
              </button>

              {usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit && (
                <p className="text-sm text-center text-amber-600">
                  Monthly limit reached. Upgrade your plan for more generations.
                </p>
              )}
            </form>
          </div>

          {/* Current Generated Dua */}
          <div>
            {currentDua ? (
              <DuaCard dua={currentDua} />
            ) : (
              <div className="bg-gradient-to-br from-madina-green-50 to-madina-gold-50 rounded-2xl p-12 border border-madina-green-100 text-center">
                <Heart className="w-16 h-16 text-madina-green-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-700 mb-2">
                  Your generated du&apos;a will appear here
                </h3>
                <p className="text-slate-600">
                  Select a theme and occasion to generate a beautiful Islamic supplication
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Saved Tab */}
      {activeTab === 'saved' && (
        <div>
          {/* Filter */}
          <div className="mb-6 flex items-center justify-between">
            <button
              onClick={() => setFilterFavorites(!filterFavorites)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-colors ${
                filterFavorites
                  ? 'bg-red-50 text-red-600 border border-red-200'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Star className={`w-5 h-5 ${filterFavorites ? 'fill-current' : ''}`} />
              <span>{filterFavorites ? 'Showing Favorites' : 'Show All'}</span>
            </button>
            <p className="text-sm text-slate-600">
              {filteredDuas.length} du&apos;a{filteredDuas.length !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Duas Grid */}
          {filteredDuas.length > 0 ? (
            <div className="grid lg:grid-cols-2 gap-6">
              {filteredDuas.map((dua) => (
                <DuaCard key={dua.id} dua={dua} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <BookmarkPlus className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                {filterFavorites ? 'No favorite du\'as yet' : 'No saved du\'as yet'}
              </h3>
              <p className="text-slate-600">
                {filterFavorites
                  ? 'Mark du\'as as favorites to see them here'
                  : 'Generate your first du\'a to get started'
                }
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
