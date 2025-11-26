'use client'

import { useEffect, useState } from 'react'
import { BookOpen, Sparkles, Copy, Check, AlertCircle, Loader2, Star, Search, Filter } from 'lucide-react'

interface Story {
  id: string
  title: string
  content: string
  moral_lesson: string
  age_group: string
  theme?: string
  is_custom: boolean
  read_count: number
  created_at: string
}

export default function StoryStudioPage() {
  const [formData, setFormData] = useState({
    theme: '',
    age_group: '',
    customTheme: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [currentStory, setCurrentStory] = useState<Story | null>(null)
  const [myStories, setMyStories] = useState<Story[]>([])
  const [prebuiltStories, setPrebuiltStories] = useState<Story[]>([])
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [usageInfo, setUsageInfo] = useState({ used: 0, limit: 0, plan: 'Basic' })
  const [activeTab, setActiveTab] = useState<'generate' | 'mystories' | 'library'>('generate')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedAgeFilter, setSelectedAgeFilter] = useState<string>('')

  const themes = [
    'Prophet Stories',
    'Sahaba Stories',
    'Good Manners & Akhlaq',
    'Honesty & Truthfulness',
    'Kindness & Compassion',
    'Courage & Bravery',
    'Patience & Perseverance',
    'Gratitude & Thankfulness',
    'Helping Others',
    'Respecting Parents',
    'Sharing & Generosity',
    'Custom'
  ]

  const ageGroups = [
    '3-5 years',
    '6-8 years',
    '9-12 years',
    '13+ years'
  ]

  useEffect(() => {
    fetchUsageInfo()
    fetchMyStories()
    fetchPrebuiltStories()
  }, [])

  const fetchUsageInfo = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stories/usage`, {
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

  const fetchMyStories = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stories/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setMyStories(data)
      }
    } catch (err) {
      console.error('Failed to fetch my stories:', err)
    }
  }

  const fetchPrebuiltStories = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stories/prebuilt`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      if (response.ok) {
        const data = await response.json()
        setPrebuiltStories(data)
      }
    } catch (err) {
      console.error('Failed to fetch prebuilt stories:', err)
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

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stories/generate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          theme,
          age_group: formData.age_group
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to generate story')
      }

      setCurrentStory(data)
      setSuccess('Story generated successfully!')
      await fetchUsageInfo()
      await fetchMyStories()

    } catch (err: any) {
      setError(err.message || 'Failed to generate story')
    } finally {
      setLoading(false)
    }
  }

  const markAsRead = async (storyId: string) => {
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/stories/${storyId}/read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      // Update read count locally
      setMyStories(myStories.map(story =>
        story.id === storyId ? { ...story, read_count: story.read_count + 1 } : story
      ))
      setPrebuiltStories(prebuiltStories.map(story =>
        story.id === storyId ? { ...story, read_count: story.read_count + 1 } : story
      ))
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const StoryCard = ({ story, showReadButton = false }: { story: Story, showReadButton?: boolean }) => (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold text-slate-800 mb-2">{story.title}</h3>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-medium">
              {story.age_group}
            </span>
            {story.theme && (
              <span className="px-3 py-1 bg-madina-green-100 text-madina-green-700 rounded-full text-xs font-medium">
                {story.theme}
              </span>
            )}
            {!story.is_custom && (
              <span className="px-3 py-1 bg-madina-gold-100 text-madina-gold-700 rounded-full text-xs font-medium">
                Pre-built
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => copyToClipboard(
              `${story.title}\n\n${story.content}\n\nMoral: ${story.moral_lesson}`,
              story.id
            )}
            className="p-2 text-slate-600 hover:text-madina-green-600 hover:bg-slate-100 rounded-lg transition-colors"
            title="Copy story"
          >
            {copiedId === story.id ? (
              <Check className="w-5 h-5 text-green-600" />
            ) : (
              <Copy className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Story Content */}
      <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl">
        <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{story.content}</p>
      </div>

      {/* Moral Lesson */}
      <div className="mb-4 p-4 bg-madina-gold-50 rounded-xl border-l-4 border-madina-gold-400">
        <h4 className="text-sm font-semibold text-madina-gold-800 mb-1">Moral Lesson:</h4>
        <p className="text-slate-700">{story.moral_lesson}</p>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-200">
        <div className="text-sm text-slate-500">
          Read {story.read_count} time{story.read_count !== 1 ? 's' : ''}
        </div>
        {showReadButton && (
          <button
            onClick={() => markAsRead(story.id)}
            className="px-4 py-2 bg-madina-green-500 text-white rounded-lg font-medium hover:bg-madina-green-600 transition-colors text-sm"
          >
            Mark as Read
          </button>
        )}
      </div>
    </div>
  )

  const filteredPrebuiltStories = prebuiltStories.filter(story => {
    const matchesSearch = story.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         story.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesAge = !selectedAgeFilter || story.age_group === selectedAgeFilter
    return matchesSearch && matchesAge
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Kids Story Studio</h1>
          <p className="text-slate-600">Create engaging Islamic stories for children</p>
        </div>
        <div className="text-right">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-white border border-slate-200 rounded-xl">
            <Sparkles className="w-5 h-5 text-purple-500" />
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
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Generate New
        </button>
        <button
          onClick={() => setActiveTab('mystories')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'mystories'
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          My Stories ({myStories.length})
        </button>
        <button
          onClick={() => setActiveTab('library')}
          className={`px-6 py-3 font-medium transition-colors ${
            activeTab === 'library'
              ? 'text-purple-600 border-b-2 border-purple-600'
              : 'text-slate-600 hover:text-slate-800'
          }`}
        >
          Story Library ({prebuiltStories.length})
        </button>
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Generation Form */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-6">Create New Story</h2>

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
                  Story Theme
                </label>
                <select
                  value={formData.theme}
                  onChange={(e) => setFormData({ ...formData, theme: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
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
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              )}

              {/* Age Group Selection */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Age Group
                </label>
                <select
                  value={formData.age_group}
                  onChange={(e) => setFormData({ ...formData, age_group: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="">Select age group...</option>
                  {ageGroups.map((age) => (
                    <option key={age} value={age}>{age}</option>
                  ))}
                </select>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || (usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit)}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-4 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    <span>Generate Story</span>
                  </>
                )}
              </button>

              {usageInfo.limit !== -1 && usageInfo.used >= usageInfo.limit && (
                <p className="text-sm text-center text-amber-600">
                  Monthly limit reached. Upgrade your plan for more stories.
                </p>
              )}
            </form>
          </div>

          {/* Current Generated Story */}
          <div>
            {currentStory ? (
              <StoryCard story={currentStory} showReadButton />
            ) : (
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-12 border border-purple-100 text-center">
                <BookOpen className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-700 mb-2">
                  Your story will appear here
                </h3>
                <p className="text-slate-600">
                  Select a theme and age group to generate an engaging Islamic story
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* My Stories Tab */}
      {activeTab === 'mystories' && (
        <div>
          {myStories.length > 0 ? (
            <div className="grid lg:grid-cols-2 gap-6">
              {myStories.map((story) => (
                <StoryCard key={story.id} story={story} showReadButton />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <BookOpen className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                No stories yet
              </h3>
              <p className="text-slate-600">
                Generate your first story to get started
              </p>
            </div>
          )}
        </div>
      )}

      {/* Library Tab */}
      {activeTab === 'library' && (
        <div>
          {/* Search and Filter */}
          <div className="mb-6 flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="text"
                placeholder="Search stories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>
            <select
              value={selectedAgeFilter}
              onChange={(e) => setSelectedAgeFilter(e.target.value)}
              className="px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Ages</option>
              {ageGroups.map((age) => (
                <option key={age} value={age}>{age}</option>
              ))}
            </select>
          </div>

          {/* Stories Grid */}
          {filteredPrebuiltStories.length > 0 ? (
            <div className="grid lg:grid-cols-2 gap-6">
              {filteredPrebuiltStories.map((story) => (
                <StoryCard key={story.id} story={story} showReadButton />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-2xl p-12 border border-slate-200 text-center">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">
                No stories found
              </h3>
              <p className="text-slate-600">
                Try adjusting your search or filters
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
