'use client'

import Link from 'next/link'
import { Heart, Sparkles, DollarSign, Users, BookOpen, Home } from 'lucide-react'

export default function DonatePage() {
  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-madina-green-400/20 to-madina-green-500/20 rounded-full blur-3xl animate-pulse"></div>
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

      {/* Main Content */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-8 border border-madina-gold-200 shadow-madina-lg">
              <span className="text-2xl">🕌</span>
              <span className="text-madina-gold-700 font-semibold">100% Goes to Masjid Madina</span>
              <Sparkles className="w-4 h-4 text-madina-gold-400" />
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 bg-clip-text text-transparent">
                Donate to Masjid Madina
              </span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Support your community masjid and earn continuous rewards. Every donation helps maintain operations,
              fund educational programs, and support those in need.
            </p>
          </div>

          {/* Impact Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 hover:border-madina-gold-200 shadow-madina hover:shadow-madina-xl transition-all">
              <div className="w-12 h-12 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center mb-4">
                <Home className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Masjid Operations</h3>
              <p className="text-slate-600 text-sm">
                Keep the lights on, maintain the facility, and ensure a welcoming space for all Muslims
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 hover:border-madina-gold-200 shadow-madina hover:shadow-madina-xl transition-all">
              <div className="w-12 h-12 bg-gradient-to-br from-madina-gold-400 to-madina-gold-500 rounded-xl flex items-center justify-center mb-4">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Education & Youth</h3>
              <p className="text-slate-600 text-sm">
                Fund Quran classes, Islamic education programs, and youth activities
              </p>
            </div>

            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 hover:border-madina-gold-200 shadow-madina hover:shadow-madina-xl transition-all">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-bold text-slate-800 mb-2">Community Support</h3>
              <p className="text-slate-600 text-sm">
                Provide assistance to families in need and support community outreach efforts
              </p>
            </div>
          </div>

          {/* Donation Options */}
          <div className="max-w-3xl mx-auto">
            <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-10 border-2 border-madina-gold-200 shadow-madina-xl">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-slate-800 mb-4">Make Your Donation</h2>
                <p className="text-slate-600">Choose your preferred donation method below</p>
              </div>

              {/* PayPal Button */}
              <div className="space-y-4">
                <button className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white py-5 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3">
                  <DollarSign className="w-6 h-6" />
                  <span>Donate via PayPal</span>
                </button>

                {/* LaunchGood Button */}
                <button className="w-full bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white py-5 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3">
                  <Heart className="w-6 h-6" />
                  <span>Donate via LaunchGood</span>
                </button>

                <p className="text-center text-sm text-slate-500 mt-4">
                  Coming soon - Payment integrations in progress
                </p>
              </div>

              {/* Additional Info */}
              <div className="mt-10 p-6 bg-madina-green-50 rounded-2xl border border-madina-green-100">
                <h4 className="font-semibold text-madina-green-800 mb-3 flex items-center space-x-2">
                  <Heart className="w-5 h-5 text-red-500" />
                  <span>About Masjid Madina</span>
                </h4>
                <p className="text-sm text-madina-green-700 leading-relaxed mb-4">
                  Masjid Madina serves as a center for worship, education, and community support.
                  Your donations help us continue our mission of serving the Muslim community and spreading Islamic knowledge.
                </p>
                <div className="space-y-2 text-sm text-madina-green-700">
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                    <span>5 daily prayers and Jumu'ah services</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                    <span>Weekend Islamic school for children</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                    <span>Monthly community events and programs</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                    <span>Support for families in need</span>
                  </div>
                </div>
              </div>

              {/* Sadaqah Jariyah Reminder */}
              <div className="mt-6 p-6 bg-madina-gold-50 rounded-2xl border border-madina-gold-100">
                <p className="text-sm text-madina-gold-800 italic text-center">
                  "When a person dies, all their deeds end except three: a continuing charity, beneficial knowledge, or a righteous child who prays for them."
                </p>
                <p className="text-xs text-madina-gold-700 text-center mt-2">- Prophet Muhammad (peace be upon him)</p>
              </div>
            </div>
          </div>

          {/* Footer CTA */}
          <div className="mt-16 text-center">
            <p className="text-slate-600 mb-4">
              Want to contribute monthly? <Link href="/subscribe" className="text-madina-green-600 hover:underline font-semibold">Subscribe to MadinaGPT</Link>
            </p>
            <p className="text-sm text-slate-500">
              100% tax-deductible • Secure payment • Instant receipt
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
