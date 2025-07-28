'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `بسم الله الرحمن الرحيم

Assalamu alaikum and welcome to BudulGPT! 🌙

I'm here to help you with authentic Islamic knowledge, guidance, and answers. I can assist you with:

• **Quranic verses** and their interpretations
• **Hadith** explanations and authenticity  
• **Islamic jurisprudence** (Fiqh) questions
• **Daily Islamic practices** and worship
• **Islamic history** and scholars
• **Personal guidance** within Islamic framework

How can I assist you on your Islamic journey today?`,
      timestamp: new Date()
    }
  ])
  
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
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
      // Call BudulGPT Backend API
      const response = await fetch('https://budulgpt-backend.onrender.com/api/v1/chat/islamic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          context: '',
          madhab_preference: 'general',
          language: 'en',
          include_citations: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      const aiResponse: Message = {
        id: data.response_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(data.timestamp || new Date().toISOString())
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Error calling BudulGPT API:', error)
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I\'m having trouble connecting to the Islamic AI service right now. Please make sure the backend is running. Would you like to try again?',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiResponse])
    } finally {
      setIsLoading(false)
    }
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
                <span className="text-white font-bold text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-islamic-gradient">BudulGPT</h1>
                <p className="text-sm text-islamic-green-600 font-medium">Islamic AI Assistant • Built on Authentic Sources</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="hidden md:block text-right">
                <div className="text-sm text-islamic-green-700 font-medium">Scholar Verified</div>
                <div className="text-xs text-islamic-green-600">Real-time Islamic Citations</div>
              </div>
              <button className="btn-islamic-outline flex items-center gap-2">
                <span>➕</span>
                New Chat
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto flex flex-col h-[calc(100vh-80px)]">
        {/* Messages */}
        <div className="flex-1 px-6 py-6 overflow-y-auto" ref={scrollAreaRef}>
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-10 h-10 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1 shadow-islamic">
                    <span className="text-white text-sm">🤖</span>
                  </div>
                )}
                
                <div className={`max-w-3xl ${message.role === 'user' ? 'order-2' : ''}`}>
                  <div className={`${
                    message.role === 'user' 
                      ? 'chat-message-user' 
                      : 'chat-message-ai'
                  }`}>
                    <div className="prose prose-sm max-w-none text-inherit">
                      <div className="whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  </div>
                </div>
                
                {message.role === 'user' && (
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0 mt-1 order-3">
                    <span className="text-gray-600 text-sm">👤</span>
                  </div>
                )}
              </div>
            ))}
            
            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-8 h-8 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <span className="text-white text-sm">🤖</span>
                </div>
                <div className="bg-white border-islamic-green-100 rounded-2xl p-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-islamic-green-600 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-islamic-green-600 rounded-full animate-pulse" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-islamic-green-600 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <span className="text-sm text-gray-500 ml-2">BudulGPT is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Input */}
        <div className="border-t bg-white px-6 py-4">
          <div className="flex gap-4">
            <input
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about Islam..."
              className="input-islamic flex-1"
              disabled={isLoading}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isLoading}
              className="btn-islamic-primary"
            >
              <span>🚀</span>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2 text-center">
            BudulGPT provides Islamic guidance. For complex religious matters, consult qualified scholars.
          </p>
        </div>
      </div>
    </div>
  )
}