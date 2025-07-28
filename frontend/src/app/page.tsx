'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowRight, MessageCircle, Zap, Shield, Globe, Users, Star, Play, Menu, X, Sparkles, Brain, Video, Image as ImageIcon } from 'lucide-react'

export default function HomePage() {
  const [isScrolled, setIsScrolled] = useState(false)
  const [activeFeature, setActiveFeature] = useState(0)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4)
    }, 3000)
    return () => clearInterval(interval)
  }, [])

  const features = [
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Budul GPT",
      description: "Islamic Conversational AI with scholar-verified knowledge",
      gradient: "from-emerald-500 to-teal-600",
      link: "/chat"
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Budul API",
      description: "Islamic AI for Developers with enterprise-grade API",
      gradient: "from-blue-500 to-indigo-600",
      link: "/api"
    },
    {
      icon: <Video className="w-8 h-8" />,
      title: "Budul Studio",
      description: "Islamic Video Generation with AI-powered content",
      gradient: "from-purple-500 to-pink-600",
      link: "/studio"
    },
    {
      icon: <ImageIcon className="w-8 h-8" />,
      title: "Budul Vision",
      description: "Islamic Image Creation with cultural authenticity",
      gradient: "from-orange-500 to-red-600",
      link: "/vision"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-emerald-50 to-amber-50 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-amber-400/20 to-orange-400/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-emerald-300/10 to-emerald-500/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-white/80 backdrop-blur-xl border-b border-emerald-100 shadow-lg' 
          : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">ب</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                  Budul AI
                </h1>
                <p className="text-xs text-emerald-600 font-medium">The OpenAI for Islam</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#products" className="text-slate-700 hover:text-emerald-600 font-medium transition-colors">
                Products
              </Link>
              <Link href="/docs" className="text-slate-700 hover:text-emerald-600 font-medium transition-colors">
                Docs
              </Link>
              <Link href="/pricing" className="text-slate-700 hover:text-emerald-600 font-medium transition-colors">
                Pricing
              </Link>
              <Link href="/about" className="text-slate-700 hover:text-emerald-600 font-medium transition-colors">
                About
              </Link>
            </div>

            {/* CTA Buttons */}
            <div className="flex items-center space-x-4">
              <Link 
                href="/auth/login"
                className="text-slate-700 hover:text-emerald-600 font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link 
                href="/auth/register"
                className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-6 py-2 rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-8 border border-emerald-200 shadow-lg">
              <span className="text-2xl">🕌</span>
              <span className="text-emerald-700 font-semibold">Introducing Budul AI</span>
              <Sparkles className="w-4 h-4 text-amber-500" />
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-600 bg-clip-text text-transparent">
                Islamic Intelligence
              </span>
              <br />
              <span className="text-slate-800">for the Modern World</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 leading-relaxed max-w-3xl mx-auto">
              Built on the foundation of Islamic wisdom, serving <span className="font-bold text-emerald-600">1.8 billion Muslims</span> worldwide 
              with AI-powered tools for authentic knowledge, creative content, and spiritual guidance.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link 
                href="/chat"
                className="group bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center space-x-3"
              >
                <Brain className="w-6 h-6" />
                <span>Try Budul GPT</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link 
                href="/docs"
                className="group bg-white/60 backdrop-blur-xl text-slate-700 px-8 py-4 rounded-2xl font-semibold text-lg border border-emerald-200 hover:shadow-xl transform hover:scale-105 transition-all duration-300 flex items-center space-x-3"
              >
                <Zap className="w-6 h-6" />
                <span>Explore API</span>
              </Link>
            </div>

            {/* Social Proof */}
            <div className="flex items-center justify-center space-x-8 text-sm text-slate-600">
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-amber-400 fill-current" />
                <span className="font-medium">Scholar Verified</span>
              </div>
              <div className="flex items-center space-x-2">
                <Globe className="w-5 h-5 text-emerald-500" />
                <span className="font-medium">50+ Languages</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-blue-500" />
                <span className="font-medium">1.8B Muslims</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Floating Product Cards */}
      <section id="products" className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                Islamic AI Products
              </span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Complete suite of Islamic AI tools designed for individuals, developers, and organizations worldwide
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className={`group relative bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 hover:border-emerald-200 shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-500 ${
                  activeFeature === index ? 'ring-2 ring-emerald-500 scale-105' : ''
                }`}
                onMouseEnter={() => setActiveFeature(index)}
              >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-3xl transition-opacity duration-500`}></div>
                
                {/* Icon */}
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-slate-800 mb-4 group-hover:text-emerald-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* Features List */}
                <div className="space-y-3 mb-8">
                  {index === 0 && (
                    <>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                        <span>Quran & Hadith citations</span>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
                        <span>Multi-madhab support</span>
                      </div>
                    </>
                  )}
                  {index === 1 && (
                    <>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                        <span>RESTful API endpoints</span>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                        <span>99.9% uptime SLA</span>
                      </div>
                    </>
                  )}
                  {index === 2 && (
                    <>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        <span>Text-to-video AI</span>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        <span>Arabic calligraphy</span>
                      </div>
                    </>
                  )}
                  {index === 3 && (
                    <>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span>Islamic art generation</span>
                      </div>
                      <div className="flex items-center space-x-3 text-sm text-slate-600">
                        <div className="w-2 h-2 bg-orange-400 rounded-full"></div>
                        <span>Cultural authenticity</span>
                      </div>
                    </>
                  )}
                </div>

                {/* CTA Button */}
                <Link 
                  href={feature.link}
                  className={`w-full bg-gradient-to-r ${feature.gradient} text-white py-3 rounded-xl font-semibold text-center block hover:shadow-lg transform hover:scale-105 transition-all duration-200`}
                >
                  Explore {feature.title}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-3xl p-12 text-white relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-32 h-32 border border-white rounded-full"></div>
              <div className="absolute top-20 right-20 w-24 h-24 border border-white rounded-full"></div>
              <div className="absolute bottom-10 left-20 w-40 h-40 border border-white rounded-full"></div>
            </div>

            <div className="relative grid md:grid-cols-4 gap-8 text-center">
              <div>
                <div className="text-5xl font-bold mb-2">1.8B+</div>
                <div className="text-emerald-100 font-medium">Muslims Worldwide</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">3,430+</div>
                <div className="text-emerald-100 font-medium">Islamic Texts</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">50+</div>
                <div className="text-emerald-100 font-medium">Languages</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">99.9%</div>
                <div className="text-emerald-100 font-medium">Uptime</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Start Your <span className="bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">Islamic AI Journey</span>
          </h2>
          <p className="text-xl text-slate-600 mb-12">
            Join thousands of Muslims worldwide using Budul AI for authentic Islamic guidance and creative tools
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              href="/auth/register"
              className="bg-gradient-to-r from-emerald-600 to-teal-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3"
            >
              <span>Get Started Free</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link 
              href="/contact"
              className="bg-white/60 backdrop-blur-xl text-slate-700 px-8 py-4 rounded-2xl font-semibold text-lg border border-emerald-200 hover:shadow-xl transform hover:scale-105 transition-all duration-300"
            >
              Contact Sales
            </Link>
          </div>

          {/* Quote */}
          <div className="mt-16 p-8 bg-white/40 backdrop-blur-xl rounded-3xl border border-emerald-200">
            <p className="text-lg italic text-slate-700 mb-4 font-medium">
              "Your Grandfather's Wisdom, Tomorrow's Technology"
            </p>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
              <span className="text-sm text-emerald-600 font-semibold">Founder, Budul AI</span>
              <div className="w-2 h-2 bg-emerald-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative bg-slate-900 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-12">
            {/* Logo Section */}
            <div>
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">ب</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold">Budul AI</h3>
                  <p className="text-slate-400 text-sm">The OpenAI for Islam</p>
                </div>
              </div>
              <p className="text-slate-300 leading-relaxed">
                Islamic Intelligence for the Modern World. Built with Islamic values for the global Muslim community.
              </p>
            </div>

            {/* Products */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Products</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/chat" className="hover:text-emerald-400 transition-colors">Budul GPT</Link></li>
                <li><Link href="/api" className="hover:text-emerald-400 transition-colors">Budul API</Link></li>
                <li><Link href="/studio" className="hover:text-emerald-400 transition-colors">Budul Studio</Link></li>
                <li><Link href="/vision" className="hover:text-emerald-400 transition-colors">Budul Vision</Link></li>
              </ul>
            </div>

            {/* Resources */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/docs" className="hover:text-emerald-400 transition-colors">Documentation</Link></li>
                <li><Link href="/blog" className="hover:text-emerald-400 transition-colors">Blog</Link></li>
                <li><Link href="/community" className="hover:text-emerald-400 transition-colors">Community</Link></li>
                <li><Link href="/support" className="hover:text-emerald-400 transition-colors">Support</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/about" className="hover:text-emerald-400 transition-colors">About</Link></li>
                <li><Link href="/careers" className="hover:text-emerald-400 transition-colors">Careers</Link></li>
                <li><Link href="/privacy" className="hover:text-emerald-400 transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-emerald-400 transition-colors">Terms</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-8 text-center text-slate-400">
            <p>&copy; 2024 Budul AI. Built with Islamic values for the global Muslim community.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}