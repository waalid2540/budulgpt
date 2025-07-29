'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Send, Bot, User, AlertCircle, CheckCircle, Clock, Sparkles, Book, Globe } from 'lucide-react'
import budulAPI, { ChatMessage, ChatResponse } from '@/services/budulAPI'

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>()
  const [error, setError] = useState<string | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection()
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const checkBackendConnection = async () => {
    try {
      await budulAPI.healthCheck()
      setIsConnected(true)
      setError(null)
    } catch (error) {
      setIsConnected(false)
      setError('Unable to connect to Islamic AI backend. Please ensure the backend is running.')
      console.error('Backend connection failed:', error)
    }
  }

  const generateSessionId = () => {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading || !isConnected) return

    const currentSessionId = sessionId || generateSessionId()
    if (!sessionId) setSessionId(currentSessionId)

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setError(null)

    try {
      // Send to Islamic AI backend
      const response: ChatResponse = await budulAPI.chat({
        message: userMessage.content,
        session_id: currentSessionId,
        context: {
          knowledge_level: 'intermediate',
          madhab: 'general',
          language: 'en'
        }
      })

      // Add AI response to chat
      const aiMessage: ChatMessage = {
        id: response.response_id,
        role: 'assistant',
        content: response.response_text,
        timestamp: new Date(response.generated_at),
        citations: response.citations,
        confidence_score: response.confidence_score,
        authenticity_score: response.authenticity_score
      }

      setMessages(prev => [...prev, aiMessage])

    } catch (error) {
      console.error('Chat error:', error)
      setError(error instanceof Error ? error.message : 'Failed to get response from Islamic AI')
      
      // Add error message to chat
      const errorMessage: ChatMessage = {
        id: `error_${Date.now()}`,
        role: 'assistant',
        content: 'I apologize, but I\'m having trouble connecting to the Islamic knowledge base. Please try again or check if the backend service is running.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
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

  const formatCitations = (citations?: any[]) => {
    if (!citations || citations.length === 0) return null

    return (
      <div className="mt-4 p-3 bg-emerald-50 border-l-4 border-emerald-400 rounded-r-lg">
        <h4 className="font-semibold text-emerald-800 mb-2 flex items-center">
          <Book className="w-4 h-4 mr-2" />
          Islamic Sources
        </h4>
        {citations.map((citation, index) => (
          <div key={index} className="text-sm text-emerald-700 mb-1">
            <span className="font-medium">{citation.reference}:</span> {citation.text}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-amber-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-xl border-b border-emerald-100 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">ب</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Budul GPT
                </h1>
                <p className="text-sm text-slate-600">Islamic AI Assistant</p>
              </div>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className={`text-sm font-medium ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white/60 backdrop-blur-xl rounded-3xl border border-emerald-100 shadow-xl overflow-hidden">
          
          {/* Welcome Message */}
          {messages.length === 0 && (
            <div className="p-8 text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <Bot className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-4">
                السلام عليكم! Welcome to Budul GPT
              </h2>
              <p className="text-slate-600 mb-6 leading-relaxed">
                I'm your Islamic AI assistant, trained on authentic Islamic sources. 
                Ask me about Islamic knowledge, and I'll provide responses with Quran and Hadith citations.
              </p>
              
              {!isConnected && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
                  <div className="flex items-center justify-center space-x-2 text-red-600">
                    <AlertCircle className="w-5 h-5" />
                    <span className="font-medium">Backend Disconnected</span>
                  </div>
                  <p className="text-red-600 text-sm mt-2">
                    The Islamic AI backend is not responding. Please start the backend server.
                  </p>
                  <button
                    onClick={checkBackendConnection}
                    className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors"
                  >
                    Retry Connection
                  </button>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left">
                <div className="p-4 bg-emerald-50 rounded-xl">
                  <Sparkles className="w-6 h-6 text-emerald-600 mb-2" />
                  <h3 className="font-semibold text-emerald-800 mb-1">Scholar Verified</h3>
                  <p className="text-emerald-700 text-sm">All responses backed by authentic Islamic sources</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-xl">
                  <Book className="w-6 h-6 text-blue-600 mb-2" />
                  <h3 className="font-semibold text-blue-800 mb-1">Quran & Hadith</h3>
                  <p className="text-blue-700 text-sm">Direct citations from Islamic texts</p>
                </div>
                <div className="p-4 bg-amber-50 rounded-xl">
                  <Globe className="w-6 h-6 text-amber-600 mb-2" />
                  <h3 className="font-semibold text-amber-800 mb-1">Multi-Madhab</h3>
                  <p className="text-amber-700 text-sm">Supporting different schools of thought</p>
                </div>
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="mx-6 mt-6 p-4 bg-red-50 border border-red-200 rounded-xl">
              <div className="flex items-center space-x-2 text-red-600">
                <AlertCircle className="w-5 h-5" />
                <span className="font-medium">Connection Error</span>
              </div>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          )}

          {/* Messages */}
          <div className="max-h-96 overflow-y-auto p-6 space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
                  {/* Avatar */}
                  <div className={`flex items-center space-x-2 mb-2 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                      message.role === 'user' 
                        ? 'bg-emerald-600 text-white' 
                        : 'bg-teal-600 text-white'
                    }`}>
                      {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </div>
                    <span className="text-sm font-medium text-slate-600">
                      {message.role === 'user' ? 'You' : 'Budul GPT'}
                    </span>
                  </div>

                  {/* Message Content */}
                  <div className={`rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-emerald-600 text-white rounded-br-md'
                      : 'bg-white border border-emerald-100 text-slate-800 rounded-bl-md shadow-sm'
                  }`}>
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

                    {/* AI Response Metadata */}
                    {message.role === 'assistant' && (message.confidence_score || message.authenticity_score) && (
                      <div className="mt-3 pt-3 border-t border-slate-200 flex items-center space-x-4 text-xs text-slate-500">
                        {message.confidence_score && (
                          <div className="flex items-center space-x-1">
                            <CheckCircle className="w-3 h-3" />
                            <span>Confidence: {Math.round(message.confidence_score * 100)}%</span>
                          </div>
                        )}
                        {message.authenticity_score && (
                          <div className="flex items-center space-x-1">
                            <Book className="w-3 h-3" />
                            <span>Authenticity: {Math.round(message.authenticity_score * 100)}%</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Citations */}
                  {message.role === 'assistant' && formatCitations(message.citations)}

                  {/* Timestamp */}
                  <div className={`mt-1 flex items-center ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <span className="text-xs text-slate-400 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{message.timestamp.toLocaleTimeString()}</span>
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-emerald-100 rounded-2xl rounded-bl-md p-4 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    <span className="text-slate-500 text-sm ml-2">Budul GPT is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-emerald-100 p-6">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={isConnected ? "Ask me about Islamic knowledge..." : "Backend disconnected - check connection"}
                  className="w-full p-4 border border-emerald-200 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent bg-white/80 backdrop-blur-sm"
                  rows={2}
                  disabled={!isConnected || isLoading}
                />
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading || !isConnected}
                className="px-6 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white rounded-xl hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-3 flex items-center justify-between text-xs text-slate-500">
              <span>Press Enter to send, Shift + Enter for new line</span>
              {sessionId && (
                <span>Session: {sessionId.slice(-8)}</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}