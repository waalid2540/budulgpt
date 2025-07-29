// Enterprise-grade Budul AI API Service
// Connects to your Islamic AI backend with full functionality

const API_BASE_URL = 'https://budulgpt-backend.onrender.com/api/v1' // Force production URL

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  citations?: Citation[]
  confidence_score?: number
  authenticity_score?: number
}

export interface Citation {
  type: 'quran' | 'hadith' | 'scholar'
  reference: string
  text: string
  relevance: number
}

export interface ChatRequest {
  message: string
  session_id?: string
  context?: {
    knowledge_level?: 'beginner' | 'intermediate' | 'advanced'
    madhab?: 'hanafi' | 'maliki' | 'shafii' | 'hanbali' | 'jafari' | 'general'
    language?: string
  }
}

export interface ChatResponse {
  response_id: string
  message: string
  session_id: string
  response_text: string
  confidence_score: number
  authenticity_score: number
  citations: Citation[]
  sources: string[]
  related_topics: string[]
  requires_scholar_review: boolean
  content_warnings: string[]
  prayer_times?: any
  qibla_direction?: number
  generated_at: string
  processing_time_ms: number
}

class BudulAPI {
  private baseUrl: string
  private headers: Record<string, string>

  constructor() {
    this.baseUrl = API_BASE_URL
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    }
  }

  // Set authentication token if user is logged in
  setAuthToken(token: string) {
    this.headers['Authorization'] = `Bearer ${token}`
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const healthUrl = this.baseUrl.replace('/api/v1', '')
      console.log('🏥 Health check URL:', healthUrl)
      
      const response = await fetch(healthUrl)
      console.log('🏥 Health check response status:', response.status)
      
      if (!response.ok) throw new Error(`Health check failed with status: ${response.status}`)
      const data = await response.json()
      console.log('🏥 Health check data:', data)
      
      // Adapt response to expected format
      return {
        status: data.status === 'operational' ? 'healthy' : data.status,
        service: data.service || 'Budul AI'
      }
    } catch (error) {
      console.error('❌ Backend health check failed:', error)
      throw error
    }
  }

  // Chat with Islamic AI
  async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/islamic`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(request)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Chat request failed')
      }

      const data = await response.json()
      
      // Adapt your backend response format to frontend expectations
      return {
        response_id: data.response_id || 'resp_' + Date.now(),
        message: request.message,
        session_id: request.session_id || 'session_' + Date.now(),
        response_text: data.response || data.response_text || '',
        confidence_score: data.authenticity_score || 0.9,
        authenticity_score: data.authenticity_score || 0.9,
        citations: data.citations || [],
        sources: data.citations?.map((c: any) => c.reference) || [],
        related_topics: [],
        requires_scholar_review: false,
        content_warnings: [],
        generated_at: data.timestamp || new Date().toISOString(),
        processing_time_ms: 1000
      }
    } catch (error) {
      console.error('Chat API error:', error)
      throw error
    }
  }

  // Stream chat for real-time responses
  async streamChat(request: ChatRequest, onChunk: (chunk: string) => void, onComplete: () => void, onError: (error: string) => void) {
    try {
      const response = await fetch(`${this.baseUrl}/chat/stream`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({ ...request, stream: true })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Stream chat failed')
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('No response stream available')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'content' && data.chunk) {
                onChunk(data.chunk)
              } else if (data.type === 'complete') {
                onComplete()
                return
              } else if (data.type === 'error') {
                onError(data.error)
                return
              }
            } catch (e) {
              console.error('Error parsing stream data:', e)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream chat error:', error)
      onError(error instanceof Error ? error.message : 'Stream chat failed')
    }
  }

  // Get conversation history
  async getConversationHistory(sessionId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/history/${sessionId}`, {
        headers: this.headers
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to get conversation history')
      }

      return await response.json()
    } catch (error) {
      console.error('Get conversation history error:', error)
      throw error
    }
  }

  // Get available Islamic topics
  async getIslamicTopics(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/topics`)
      if (!response.ok) throw new Error('Failed to get Islamic topics')
      return await response.json()
    } catch (error) {
      console.error('Get Islamic topics error:', error)
      return []
    }
  }

  // Get available madhabs
  async getMadhabs(): Promise<string[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/madhabs`)
      if (!response.ok) throw new Error('Failed to get madhabs')
      return await response.json()
    } catch (error) {
      console.error('Get madhabs error:', error)
      return ['general']
    }
  }

  // Update user preferences
  async updatePreferences(preferences: any): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/preferences`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(preferences)
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to update preferences')
      }

      return await response.json()
    } catch (error) {
      console.error('Update preferences error:', error)
      throw error
    }
  }

  // WebSocket connection for real-time chat
  createWebSocket(userId: string, sessionId: string, onMessage: (data: any) => void, onError: (error: Event) => void): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws').replace('/api/v1', '')
    const ws = new WebSocket(`${wsUrl}/api/v1/chat/ws/${userId}/${sessionId}`)

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('WebSocket message parse error:', error)
      }
    }

    ws.onerror = onError

    return ws
  }
}

// Export singleton instance
export const budulAPI = new BudulAPI()

// Export for React components
export default budulAPI