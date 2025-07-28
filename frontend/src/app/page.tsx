'use client'

import { motion } from 'framer-motion'
import { ArrowRight, MessageCircle, Code, Video, Image, Globe, Users, Shield, Zap, Star, Play } from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-islamic-gradient bg-islamic-pattern">
      {/* Navigation */}
      <nav className="nav-islamic sticky top-0 z-50">
        <div className="container-islamic">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-xl flex items-center justify-center shadow-islamic">
                <span className="text-white font-bold text-xl arabic">ب</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-islamic-gradient">Budul AI</span>
                <div className="text-xs text-islamic-green-600 font-medium">The OpenAI for Islam</div>
              </div>
            </div>
            
            <div className="hidden lg:flex items-center space-x-8">
              <Link href="#products" className="nav-link-islamic">Products</Link>
              <Link href="/docs" className="nav-link-islamic">Documentation</Link>
              <Link href="/pricing" className="nav-link-islamic">Pricing</Link>
              <Link href="/about" className="nav-link-islamic">About</Link>
              <Link href="/community" className="nav-link-islamic">Community</Link>
            </div>
            
            <div className="flex items-center space-x-4">
              <Link href="/auth/login">
                <button className="text-islamic-green-700 hover:text-islamic-green-900 px-4 py-2 font-medium transition-colors">
                  Sign In
                </button>
              </Link>
              <Link href="/auth/register">
                <button className="btn-islamic-primary">
                  Get Started
                </button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-islamic">
        <div className="container-islamic relative z-10">
          <div className="max-w-5xl mx-auto text-center py-20 lg:py-32">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-islamic"
            >
              <div className="mb-6">
                <span className="inline-block px-4 py-2 bg-islamic-green-100 text-islamic-green-800 rounded-full text-sm font-semibold mb-8">
                  🕌 Introducing Budul AI
                </span>
              </div>
              
              <h1 className="text-display mb-8">
                <span className="text-islamic-gradient">Islamic artificial intelligence</span>
                <br />
                <span className="text-islamic-green-900">that serves the Muslim community</span>
                <br />
                <span className="text-islamic-green-700">with authentic, scholar-verified knowledge and creative tools.</span>
              </h1>
              
              <p className="text-body-large text-islamic-green-700 mb-12 max-w-4xl mx-auto leading-relaxed">
                Built on the foundation of Islamic wisdom, Budul AI is the definitive platform serving 1.8 billion Muslims worldwide 
                with AI-powered tools for authentic Islamic knowledge, creative content, and spiritual guidance.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
                <Link href="/chat">
                  <button className="btn-islamic-primary text-lg px-8 py-4 group">
                    Try Budul GPT
                    <Play className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                </Link>
                <Link href="/docs/api">
                  <button className="btn-islamic-outline text-lg px-8 py-4">
                    Explore API
                  </button>
                </Link>
                <Link href="/studio">
                  <button className="btn-islamic-secondary text-lg px-8 py-4">
                    Create Islamic Videos
                  </button>
                </Link>
              </div>
              
              <div className="text-islamic-green-600 font-amiri text-lg italic">
                "Your Grandfather's Wisdom, Tomorrow's Technology"
              </div>
              
              <div className="mt-12 flex items-center justify-center space-x-8 text-sm text-islamic-green-600">
                <div className="flex items-center space-x-1">
                  <Star className="h-4 w-4 text-islamic-gold-500 fill-current" />
                  <span>Scholar Verified</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Globe className="h-4 w-4" />
                  <span>50+ Languages</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Users className="h-4 w-4" />
                  <span>1.8B Muslims Served</span>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Product Grid Section */}
      <section id="products" className="py-20 bg-white/80 backdrop-blur-sm">
        <div className="container-islamic">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center mb-16"
          >
            <h2 className="text-headline mb-6 text-islamic-gradient">
              Islamic AI Products
            </h2>
            <p className="text-body-large text-islamic-green-700 max-w-3xl mx-auto">
              Complete suite of Islamic AI tools for individuals, developers, and organizations worldwide
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* 🤖 Budul GPT - Islamic Conversational AI */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
            >
              <div className="feature-card-islamic group">
                <div className="feature-icon-islamic mb-6">
                  <span className="text-3xl">🤖</span>
                </div>
                <h3 className="text-title mb-4 text-islamic-green-900">Budul GPT</h3>
                <p className="text-body text-islamic-green-700 mb-6">
                  Islamic Conversational AI with authentic scholar-verified knowledge and real-time citations
                </p>
                <div className="space-y-2 text-body-small text-islamic-green-600 mb-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Hadith & Quran citations</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Multi-madhab support</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>50+ languages</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Scholar verification</span>
                  </div>
                </div>
                <Link href="/chat">
                  <button className="btn-islamic-primary w-full group-hover:scale-105 transition-transform">
                    Try Budul GPT
                  </button>
                </Link>
              </div>
            </motion.div>

            {/* ⚡ Budul API - Islamic AI for Developers */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
            >
              <div className="feature-card-islamic group">
                <div className="feature-icon-islamic mb-6">
                  <span className="text-3xl">⚡</span>
                </div>
                <h3 className="text-title mb-4 text-islamic-green-900">Budul API</h3>
                <p className="text-body text-islamic-green-700 mb-6">
                  Islamic AI for Developers with comprehensive API access to Islamic knowledge and AI models
                </p>
                <div className="space-y-2 text-body-small text-islamic-green-600 mb-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>RESTful API endpoints</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Islamic knowledge base</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Enterprise scale</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>99.9% uptime SLA</span>
                  </div>
                </div>
                <Link href="/docs/api">
                  <button className="btn-islamic-outline w-full group-hover:scale-105 transition-transform">
                    View Documentation
                  </button>
                </Link>
              </div>
            </motion.div>

            {/* 🎬 Budul Studio - Islamic Video Generation */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
            >
              <div className="feature-card-islamic group">
                <div className="feature-icon-islamic mb-6">
                  <span className="text-3xl">🎬</span>
                </div>
                <h3 className="text-title mb-4 text-islamic-green-900">Budul Studio</h3>
                <p className="text-body text-islamic-green-700 mb-6">
                  Islamic Video Generation with AI-powered content creation and calligraphy integration
                </p>
                <div className="space-y-2 text-body-small text-islamic-green-600 mb-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Text-to-video AI</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Arabic calligraphy</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Geometric patterns</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Halal audio synthesis</span>
                  </div>
                </div>
                <Link href="/studio">
                  <button className="btn-islamic-secondary w-full group-hover:scale-105 transition-transform">
                    Create Videos
                  </button>
                </Link>
              </div>
            </motion.div>

            {/* 🎨 Budul Vision - Islamic Image Creation */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              <div className="feature-card-islamic group">
                <div className="feature-icon-islamic mb-6">
                  <span className="text-3xl">🎨</span>
                </div>
                <h3 className="text-title mb-4 text-islamic-green-900">Budul Vision</h3>
                <p className="text-body text-islamic-green-700 mb-6">
                  Islamic Image Creation with culturally sensitive AI art and calligraphy generation
                </p>
                <div className="space-y-2 text-body-small text-islamic-green-600 mb-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Islamic art generation</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Arabic calligraphy AI</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>Cultural authenticity</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-islamic-gold-500 rounded-full"></div>
                    <span>High resolution export</span>
                  </div>
                </div>
                <Link href="/vision">
                  <button className="btn-islamic-outline w-full group-hover:scale-105 transition-transform">
                    Generate Images
                  </button>
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-20">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              Built for the <span className="bg-gradient-to-r from-emerald-600 to-amber-600 bg-clip-text text-transparent">Global Muslim Community</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Authentic Islamic knowledge meets cutting-edge AI technology
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-600 to-emerald-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Scholar Verified</h3>
              <p className="text-gray-600">
                Every response is backed by authentic Islamic sources and verified by qualified scholars
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Globe className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Global Reach</h3>
              <p className="text-gray-600">
                Supporting Arabic, English, Urdu, Turkish, and more languages for 1.8 billion Muslims
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.7 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-purple-700 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Zap className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-4">Lightning Fast</h3>
              <p className="text-gray-600">
                Sub-second responses with enterprise-grade infrastructure and 99.9% uptime
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-6 py-20 bg-gradient-to-r from-emerald-600 to-amber-600">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid md:grid-cols-4 gap-8 text-center text-white"
          >
            <div>
              <div className="text-4xl font-bold mb-2">1.8B+</div>
              <div className="text-emerald-100">Muslims Served</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">1M+</div>
              <div className="text-emerald-100">Islamic Texts</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">50+</div>
              <div className="text-emerald-100">Countries</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">99.9%</div>
              <div className="text-emerald-100">Uptime</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Start Your <span className="bg-gradient-to-r from-emerald-600 to-amber-600 bg-clip-text text-transparent">Islamic AI Journey</span>
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Join thousands of Muslims worldwide using Budul AI for authentic Islamic guidance
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/register">
                <Button size="lg" className="bg-gradient-to-r from-emerald-600 to-amber-600 hover:from-emerald-700 hover:to-amber-700 text-lg px-8 py-4">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
              <Link href="/contact">
                <Button variant="outline" size="lg" className="text-lg px-8 py-4">
                  Contact Sales
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white px-6 py-16">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-amber-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">ب</span>
                </div>
                <span className="text-2xl font-bold">Budul AI</span>
              </div>
              <p className="text-gray-300 mb-4">
                Islamic Intelligence for the Modern World
              </p>
              <p className="text-sm text-gray-400">
                Named after our founder's grandfather, carrying forward authentic Islamic wisdom through AI.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Products</h3>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="/chat" className="hover:text-white transition-colors">Budul GPT</Link></li>
                <li><Link href="/docs/api" className="hover:text-white transition-colors">Budul API</Link></li>
                <li><Link href="/studio" className="hover:text-white transition-colors">Budul Studio</Link></li>
                <li><Link href="/vision" className="hover:text-white transition-colors">Budul Vision</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="/docs" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="/community" className="hover:text-white transition-colors">Community</Link></li>
                <li><Link href="/support" className="hover:text-white transition-colors">Support</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-300">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Budul AI. Built with Islamic values for the global Muslim community.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}