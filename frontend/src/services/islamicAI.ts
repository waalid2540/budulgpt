/**
 * Budul AI - Islamic AI Service Layer
 * Connects frontend to the trained Sunni Islamic AI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

export interface IslamicChatRequest {
  message: string
  context?: string
  madhab_preference?: 'general' | 'hanafi' | 'maliki' | 'shafii' | 'hanbali'
  language?: string
  include_citations?: boolean
}

export interface IslamicChatResponse {
  response: string
  authenticity_score: number
  citations: Array<{
    type: string
    reference: string
    source: string
    url?: string
  }>
  madhab_positions?: Record<string, string>
  confidence: string
  response_id: string
  timestamp: string
}

export interface QuranSearchRequest {
  query: string
  translation?: string
  include_arabic?: boolean
  surah_filter?: string
}

export interface HadithSearchRequest {
  query: string
  collection?: string
  authenticity_filter?: string
  include_arabic?: boolean
}

export interface FatwaRequest {
  question: string
  context?: string
  madhab?: string
  urgency?: string
}

class IslamicAIService {
  private baseURL: string

  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Main Islamic AI Chat
  async chat(request: IslamicChatRequest): Promise<IslamicChatResponse> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/islamic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Islamic AI API error: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Search Quran
  async searchQuran(request: QuranSearchRequest) {
    const response = await fetch(`${this.baseURL}/api/v1/search/quran`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Quran search error: ${response.status}`)
    }

    return response.json()
  }

  // Search Hadith
  async searchHadith(request: HadithSearchRequest) {
    const response = await fetch(`${this.baseURL}/api/v1/search/hadith`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Hadith search error: ${response.status}`)
    }

    return response.json()
  }

  // Generate Fatwa
  async generateFatwa(request: FatwaRequest) {
    const response = await fetch(`${this.baseURL}/api/v1/fatwa/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Fatwa generation error: ${response.status}`)
    }

    return response.json()
  }

  // Get Prayer Times
  async getPrayerTimes(lat: number, lng: number, date?: string) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lng: lng.toString(),
      ...(date && { date })
    })

    const response = await fetch(`${this.baseURL}/api/v1/prayer-times?${params}`)

    if (!response.ok) {
      throw new Error(`Prayer times error: ${response.status}`)
    }

    return response.json()
  }

  // Get Qibla Direction
  async getQiblaDirection(lat: number, lng: number) {
    const params = new URLSearchParams({
      lat: lat.toString(),
      lng: lng.toString()
    })

    const response = await fetch(`${this.baseURL}/api/v1/qibla?${params}`)

    if (!response.ok) {
      throw new Error(`Qibla direction error: ${response.status}`)
    }

    return response.json()
  }

  // Validate Islamic Content
  async validateIslamicContent(text: string) {
    const params = new URLSearchParams({ text })

    const response = await fetch(`${this.baseURL}/api/v1/validate/islamic?${params}`)

    if (!response.ok) {
      throw new Error(`Content validation error: ${response.status}`)
    }

    return response.json()
  }

  // Get API Stats
  async getAPIStats() {
    const response = await fetch(`${this.baseURL}/api/v1/stats`)

    if (!response.ok) {
      throw new Error(`API stats error: ${response.status}`)
    }

    return response.json()
  }

  // Health Check
  async healthCheck() {
    const response = await fetch(`${this.baseURL}/`)

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`)
    }

    return response.json()
  }
}

// Export singleton instance
export const islamicAIService = new IslamicAIService()
export default islamicAIService