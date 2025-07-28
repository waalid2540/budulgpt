'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Plus, MessageCircle, Book, Lightbulb, User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import { Button } from '../../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card'
import { Input } from '../../components/ui/input'
import { ScrollArea } from '../../components/ui/scroll-area'
import { Badge } from '../../components/ui/badge'
import ReactMarkdown from 'react-markdown'
import { islamicAIService } from '../../services/islamicAI'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  citations?: Citation[]
  islamicTopics?: string[]
  confidenceScore?: number
}

interface Citation {
  type: 'quran' | 'hadith' | 'source'
  reference: string
  displayText: string
  url?: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `بسم الله الرحمن الرحيم

Assalamu alaikum and welcome to Budul AI! 🌙

I'm here to help you with authentic Islamic knowledge, guidance, and answers. I can assist you with:

• **Quranic verses** and their interpretations
• **Hadith** explanations and authenticity
• **Islamic jurisprudence** (Fiqh) questions
• **Daily Islamic practices** and worship
• **Islamic history** and scholars
• **Personal guidance** within Islamic framework

How can I assist you on your Islamic journey today?`,
      timestamp: new Date(),
      islamicTopics: ['greeting', 'introduction'],
      confidenceScore: 1.0
    }
  ])
  
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestions] = useState([
    "What are the five pillars of Islam?",
    "How do I perform wudu properly?",
    "What time should I pray Fajr?",
    "Explain the meaning of Surah Al-Fatiha"
  ])
  
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    const currentMessage = inputMessage
    setInputMessage('')
    setIsLoading(true)

    try {
      // Call Budul AI Backend API using service layer
      const data = await islamicAIService.chat({
        message: currentMessage,
        context: '',
        madhab_preference: 'general',
        language: 'en',
        include_citations: true
      })
      
      const aiResponse: Message = {
        id: data.response_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp || new Date().toISOString()),
        citations: data.citations?.map((citation: any) => ({
          type: citation.type as 'quran' | 'hadith' | 'source',
          reference: citation.reference,
          displayText: citation.source || citation.reference,
          url: citation.url
        })) || [],
        islamicTopics: extractTopics(currentMessage),
        confidenceScore: data.authenticity_score || 0.9
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Error calling Budul AI API:', error)
      
      // Fallback to mock response if API fails
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the Islamic AI service right now. Please make sure the backend is running on port 8000. Would you like to try again?',
        timestamp: new Date(),
        citations: [],
        islamicTopics: ['error'],
        confidenceScore: 0.5
      }
      setMessages(prev => [...prev, aiResponse])
    } finally {
      setIsLoading(false)
    }
  }

  const generateMockResponse = (query: string): string => {
    if (query.toLowerCase().includes('prayer') || query.toLowerCase().includes('salah')) {
      return `Prayer (Salah) is one of the five pillars of Islam and a direct connection between a Muslim and Allah (SWT).

**The Five Daily Prayers:**
1. **Fajr** - Dawn prayer (2 rakats)
2. **Dhuhr** - Midday prayer (4 rakats)
3. **Asr** - Afternoon prayer (4 rakats)
4. **Maghrib** - Sunset prayer (3 rakats)
5. **Isha** - Night prayer (4 rakats)

The Prophet (ﷺ) said: *"The first thing for which a person will be called to account on the Day of Resurrection is prayer."* [Sunan at-Tirmidhi]

**Benefits of Regular Prayer:**
- Spiritual purification and connection with Allah
- Structure and discipline in daily life
- Community bonding through congregational prayers
- Mindfulness and reflection throughout the day

Would you like specific guidance on prayer timings, proper ablution (wudu), or the steps of performing prayer?

والله أعلم (And Allah knows best)`
    }

    if (query.toLowerCase().includes('wudu') || query.toLowerCase().includes('ablution')) {
      return `Wudu (ablution) is the ritual purification required before prayer. Here are the essential steps:

**Steps of Wudu:**
1. **Intention (Niyyah)** - Make intention in your heart
2. **Bismillah** - Say "Bismillah" (In the name of Allah)
3. **Wash hands** - Three times up to the wrists
4. **Rinse mouth** - Three times
5. **Clean nose** - Sniff water and blow out three times
6. **Wash face** - Three times from forehead to chin, ear to ear
7. **Wash arms** - Right then left, three times up to elbows
8. **Wipe head** - Once with wet hands
9. **Wipe ears** - Inside and outside once
10. **Wash feet** - Right then left, three times up to ankles

**Things that break Wudu:**
- Using the restroom
- Passing gas
- Deep sleep
- Touching private parts
- Loss of consciousness

The Prophet (ﷺ) said: *"Wudu is half of faith."* [Sahih Muslim]

والله أعلم (And Allah knows best)`
    }

    return `Thank you for your question about "${query}". 

I'm here to provide authentic Islamic guidance based on the Quran and Sunnah. For specific religious rulings or complex matters, I always recommend consulting with qualified Islamic scholars who can consider your particular circumstances.

Could you please provide more details about what specific aspect you'd like to learn about? This will help me give you the most relevant and beneficial response.

بارك الله فيك (May Allah bless you)`
  }

  const generateMockCitations = (query: string): Citation[] => {
    if (query.toLowerCase().includes('prayer')) {
      return [
        {
          type: 'hadith',
          reference: 'Sunan at-Tirmidhi, Book 2, Hadith 413',
          displayText: 'Sunan at-Tirmidhi',
          url: 'https://sunnah.com/tirmidhi:413'
        },
        {
          type: 'quran',
          reference: '2:3',
          displayText: 'Quran 2:3',
          url: 'https://quran.com/2/3'
        }
      ]
    }

    if (query.toLowerCase().includes('wudu')) {
      return [
        {
          type: 'hadith',
          reference: 'Sahih Muslim, Book 2, Hadith 432',
          displayText: 'Sahih Muslim',
          url: 'https://sunnah.com/muslim:432'
        },
        {
          type: 'quran',
          reference: '5:6',
          displayText: 'Quran 5:6',
          url: 'https://quran.com/5/6'
        }
      ]
    }

    return []
  }

  const extractTopics = (query: string): string[] => {
    const topics = []
    if (query.toLowerCase().includes('prayer') || query.toLowerCase().includes('salah')) {
      topics.push('prayer', 'worship')
    }
    if (query.toLowerCase().includes('wudu') || query.toLowerCase().includes('ablution')) {
      topics.push('purification', 'wudu')
    }
    return topics
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion)
    inputRef.current?.focus()
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-islamic-gradient bg-islamic-pattern">
      {/* Header */}
      <div className="nav-islamic border-b border-islamic-green-100">
        <div className="container-islamic">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-xl flex items-center justify-center shadow-islamic">
                <span className="text-white font-bold text-xl arabic">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-islamic-gradient">Budul GPT</h1>
                <p className="text-sm text-islamic-green-600 font-medium">Islamic AI Assistant • Built on Grandfather's Wisdom</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:block text-right">
                <div className="text-sm text-islamic-green-700 font-medium">Scholar Verified</div>
                <div className="text-xs text-islamic-green-600">Real-time Islamic Citations</div>
              </div>
              <button className="btn-islamic-outline flex items-center gap-2">
                <Plus className="h-4 w-4" />
                New Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-80px)]">
        {/* Messages */}
        <ScrollArea className="flex-1 px-6 py-6" ref={scrollAreaRef}>
          <div className="space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.role === 'assistant' && (
                    <div className="w-10 h-10 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-islamic">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                  )}
                  
                  <div className={`max-w-3xl ${message.role === 'user' ? 'order-2' : ''}`}>
                    <Card className={`${
                      message.role === 'user' 
                        ? 'chat-message-user' 
                        : 'chat-message-ai'
                    }`}>
                      <CardContent className="p-4">
                        <div className="prose prose-sm max-w-none text-inherit">
                        <ReactMarkdown 
                          components={{
                            p: ({children}) => <p className="mb-3 last:mb-0">{children}</p>,
                            strong: ({children}) => <strong className="font-semibold text-islamic-gold-600">{children}</strong>,
                            em: ({children}) => <em className="italic text-islamic-green-700">{children}</em>,
                            ul: ({children}) => <ul className="list-disc list-inside space-y-1 ml-2">{children}</ul>,
                            ol: ({children}) => <ol className="list-decimal list-inside space-y-1 ml-2">{children}</ol>,
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                      
                      {/* Citations */}
                      {message.citations && message.citations.length > 0 && (
                        <div className="chat-citation">
                          <div className="flex items-center gap-2 mb-2">
                            <Book className="h-4 w-4 text-islamic-gold-600" />
                            <span className="text-sm font-semibold text-islamic-gold-700">Islamic Sources:</span>
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {message.citations.map((citation, index) => (
                              <span key={index} className="inline-block px-2 py-1 bg-islamic-gold-100 text-islamic-gold-800 rounded-md text-xs font-medium">
                                {citation.displayText}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                        
                        {/* Islamic Topics */}
                        {message.islamicTopics && message.islamicTopics.length > 0 && (
                          <div className="mt-2">
                            <div className="flex flex-wrap gap-1">
                              {message.islamicTopics.map((topic, index) => (
                                <Badge key={index} variant="secondary" className="text-xs capitalize">
                                  {topic}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Confidence Score */}
                        {message.confidenceScore && message.role === 'assistant' && (
                          <div className="mt-2 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-gray-500">
                                Confidence: {Math.round(message.confidenceScore * 100)}%
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                                <ThumbsUp className="h-3 w-3" />
                              </Button>
                              <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                                <ThumbsDown className="h-3 w-3" />
                              </Button>
                              <Button size="sm" variant="ghost" className="h-6 w-6 p-0">
                                <Copy className="h-3 w-3" />
                              </Button>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                  
                  {message.role === 'user' && (
                    <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0 mt-1 order-3">
                      <User className="h-4 w-4 text-gray-600" />
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            
            {/* Loading indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-amber-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <Card className="bg-white border-emerald-100">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      <span className="text-sm text-gray-500 ml-2">Budul AI is thinking...</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </ScrollArea>

        {/* Suggestions */}
        {messages.length === 1 && (
          <div className="px-6 py-4">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="h-4 w-4 text-emerald-600" />
              <span className="text-sm font-medium text-emerald-600">Suggested questions:</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-left justify-start h-auto p-3 border-emerald-200 hover:border-emerald-300"
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t bg-white px-6 py-4">
          <div className="flex gap-4">
            <Input
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Islam..."
              className="flex-1 border-emerald-200 focus:border-emerald-500"
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="bg-gradient-to-r from-emerald-600 to-amber-600 hover:from-emerald-700 hover:to-amber-700"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            Budul AI provides Islamic guidance. For complex religious matters, consult qualified scholars.
          </p>
        </div>
      </div>
    </div>
  )
}