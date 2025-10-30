'use client'

import Link from 'next/link'
import { Heart, Users, BookOpen, Home, Sparkles, ArrowRight } from 'lucide-react'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-madina-green-400/20 to-madina-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-madina-green-100 shadow-madina-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-madina">
                <span className="text-white font-bold text-xl">م</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                  MadinaGPT
                </h1>
              </div>
            </Link>
            <Link href="/" className="text-slate-700 hover:text-madina-green-600 font-medium">
              Back to Home
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-8 border border-madina-green-200 shadow-madina-lg">
              <span className="text-2xl">🕌</span>
              <span className="text-madina-green-700 font-semibold">Supporting Masjid Madina</span>
              <Sparkles className="w-4 h-4 text-madina-gold-400" />
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                MadinaGPT
              </span>
              <br />
              <span className="text-slate-800">Faith, Knowledge, and Guidance</span>
            </h1>

            <p className="text-xl text-slate-600 leading-relaxed mb-12">
              MadinaGPT is an Islamic AI initiative that supports Masjid Madina through technology.
              <br />
              <span className="font-bold text-madina-green-600">50% of all subscription proceeds</span> directly fund
              masjid operations, community programs, and da'wah efforts.
            </p>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 shadow-madina-xl">
                <div className="w-16 h-16 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-2xl flex items-center justify-center mb-6">
                  <Heart className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-4">Our Mission</h2>
                <p className="text-slate-600 leading-relaxed">
                  MadinaGPT exists to serve the Muslim community by providing authentic Islamic AI tools while
                  supporting Masjid Madina's vital community services. We believe technology should strengthen faith
                  and support our masajid.
                </p>
              </div>

              <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 shadow-madina-xl">
                <div className="w-16 h-16 bg-gradient-to-br from-madina-gold-400 to-madina-gold-500 rounded-2xl flex items-center justify-center mb-6">
                  <Sparkles className="w-8 h-8 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-slate-800 mb-4">The 50% Model</h2>
                <p className="text-slate-600 leading-relaxed mb-4">
                  Every MadinaGPT subscription is split transparently:
                </p>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-madina-green-500 rounded-full"></div>
                    <span className="text-slate-700"><strong>$5.00</strong> → Masjid Madina operations & programs</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-madina-gold-400 rounded-full"></div>
                    <span className="text-slate-700"><strong>$4.99</strong> → Development & server costs</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-3xl p-10 text-white shadow-madina-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl"></div>
              <div className="absolute bottom-0 left-0 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>

              <div className="relative">
                <h3 className="text-3xl font-bold mb-6">About Masjid Madina</h3>
                <p className="text-madina-green-50 leading-relaxed mb-8">
                  Masjid Madina serves as a beacon of faith and community support. Your subscriptions help us continue
                  providing essential services to the Muslim community.
                </p>

                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <Home className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">5 Daily Prayers & Jumu'ah</h4>
                      <p className="text-sm text-madina-green-100">A welcoming space for worship and congregation</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <BookOpen className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Islamic Education</h4>
                      <p className="text-sm text-madina-green-100">Weekend school, Quran classes, and youth programs</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <Users className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Community Support</h4>
                      <p className="text-sm text-madina-green-100">Assistance for families, converts, and those in need</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-1">
                      <Heart className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Da'wah & Outreach</h4>
                      <p className="text-sm text-madina-green-100">Spreading Islamic knowledge to the wider community</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-white/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                What We Offer
              </span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Premium Islamic AI tools designed for your spiritual journey
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-madina">
              <div className="w-12 h-12 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center mb-4 text-white text-2xl">
                💬
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Madina GPT</h3>
              <p className="text-slate-600 text-sm">
                Ask Islamic questions and receive authentic, scholar-verified answers
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-madina">
              <div className="w-12 h-12 bg-gradient-to-br from-madina-gold-400 to-madina-gold-500 rounded-xl flex items-center justify-center mb-4 text-white text-2xl">
                🤲
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Du'ā Generator</h3>
              <p className="text-slate-600 text-sm">
                Generate beautiful duas with Arabic, transliteration, and English meanings
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-madina">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mb-4 text-white text-2xl">
                📚
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Kids Stories</h3>
              <p className="text-slate-600 text-sm">
                Islamic stories with moral lessons for children and families
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 shadow-madina">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center mb-4 text-white text-2xl">
                🕋
              </div>
              <h3 className="text-xl font-bold text-slate-800 mb-2">Umrah Alert</h3>
              <p className="text-slate-600 text-sm">
                Coming soon - AI-powered Umrah planning and guidance
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Stats */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 rounded-3xl p-12 text-white">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Transparent Impact</h2>
              <p className="text-madina-green-50 text-lg">Every subscription makes a real difference</p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-5xl font-bold mb-2">50%</div>
                <div className="text-madina-green-100 font-medium">Of Every Subscription</div>
                <div className="text-sm text-madina-green-200 mt-1">Goes to Masjid Madina</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">$9.99</div>
                <div className="text-madina-green-100 font-medium">Monthly Subscription</div>
                <div className="text-sm text-madina-green-200 mt-1">Transparent & Halal</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">100%</div>
                <div className="text-madina-green-100 font-medium">Authentic Islamic Content</div>
                <div className="text-sm text-madina-green-200 mt-1">Verified by Scholars</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Join <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">MadinaGPT</span> Today
          </h2>
          <p className="text-xl text-slate-600 mb-12">
            Support Masjid Madina while accessing premium Islamic AI tools for your spiritual journey
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/subscribe"
              className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3"
            >
              <span>Subscribe - $9.99/mo</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/donate"
              className="bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
            >
              Donate to Masjid
            </Link>
          </div>

          <div className="mt-16 p-8 bg-white/40 backdrop-blur-xl rounded-3xl border border-madina-green-200">
            <p className="text-lg italic text-slate-700 mb-4 font-medium">
              "MadinaGPT is an initiative supporting Masjid Madina. 50% of all proceeds fund community programs and da'wah efforts."
            </p>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-madina-green-400 rounded-full"></div>
              <span className="text-sm text-madina-green-600 font-semibold">MadinaGPT Team</span>
              <div className="w-2 h-2 bg-madina-green-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
