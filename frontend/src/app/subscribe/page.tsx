'use client'

import Link from 'next/link'
import { ArrowRight, Check, Heart, Sparkles, DollarSign } from 'lucide-react'

export default function SubscribePage() {
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

      {/* Main Content */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-8 border border-madina-green-200 shadow-madina-lg">
              <span className="text-2xl">🕌</span>
              <span className="text-madina-green-700 font-semibold">50% Supports Masjid Madina</span>
              <Sparkles className="w-4 h-4 text-madina-gold-400" />
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                MadinaGPT Premium
              </span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Support Masjid Madina while accessing premium Islamic AI tools for your spiritual journey
            </p>
          </div>

          {/* Pricing Card */}
          <div className="max-w-2xl mx-auto">
            <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-10 border-2 border-madina-green-200 shadow-madina-xl relative overflow-hidden">
              {/* Background Pattern */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl"></div>

              {/* Badge */}
              <div className="absolute top-6 right-6">
                <div className="bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                  Best Value
                </div>
              </div>

              <div className="relative">
                {/* Price */}
                <div className="mb-8">
                  <div className="flex items-baseline justify-center mb-4">
                    <span className="text-6xl font-bold text-madina-green-600">$4.99</span>
                    <span className="text-2xl text-slate-600 ml-2">/month</span>
                  </div>
                  <div className="text-center mb-2">
                    <div className="inline-flex items-center space-x-2 bg-madina-green-50 px-4 py-2 rounded-full">
                      <Heart className="w-4 h-4 text-red-500" />
                      <span className="text-sm font-semibold text-madina-green-700">
                        $2.50 goes directly to Masjid Madina
                      </span>
                    </div>
                  </div>
                  <div className="text-center">
                    <span className="text-xs text-slate-500 font-medium">Unlimited Access to All Features</span>
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-4 mb-10">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-madina-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Unlimited Madina GPT Access</h3>
                      <p className="text-slate-600 text-sm">Ask unlimited Islamic questions with authentic answers</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-madina-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Du'ā Generator</h3>
                      <p className="text-slate-600 text-sm">Create beautiful duas with meanings and transliterations</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-madina-green-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Islamic Kids Stories</h3>
                      <p className="text-slate-600 text-sm">Generate moral stories for children from Islamic teachings</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-madina-gold-400 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Priority Support</h3>
                      <p className="text-slate-600 text-sm">Get faster responses and priority feature access</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-madina-gold-400 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Early Access</h3>
                      <p className="text-slate-600 text-sm">Be the first to access new features like Umrah Alert AI</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <Heart className="w-4 h-4 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-slate-800">Support Masjid Madina</h3>
                      <p className="text-slate-600 text-sm">50% of your subscription funds community programs and da'wah</p>
                    </div>
                  </div>
                </div>

                {/* CTA Button */}
                <div className="space-y-4">
                  <button className="w-full bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white py-5 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3 group">
                    <DollarSign className="w-6 h-6" />
                    <span>Subscribe via Stripe</span>
                    <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                  </button>
                  <p className="text-center text-sm text-slate-500">
                    Coming soon - Stripe integration in progress
                  </p>
                </div>

                {/* Impact Statement */}
                <div className="mt-8 p-6 bg-madina-green-50 rounded-2xl border border-madina-green-100">
                  <h4 className="font-semibold text-madina-green-800 mb-2 flex items-center space-x-2">
                    <Heart className="w-5 h-5 text-red-500" />
                    <span>Your Impact</span>
                  </h4>
                  <p className="text-sm text-madina-green-700 leading-relaxed">
                    Every month, <strong>$2.50 of your $4.99 subscription</strong> goes directly to Masjid Madina to support:
                  </p>
                  <ul className="mt-3 space-y-2 text-sm text-madina-green-700">
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                      <span>Daily masjid operations and maintenance</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                      <span>Community education and youth programs</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                      <span>Da'wah and outreach efforts</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-madina-green-500 rounded-full"></div>
                      <span>Charitable initiatives for those in need</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* FAQ or Additional Info */}
          <div className="mt-16 text-center">
            <p className="text-slate-600 mb-4">
              Have questions? <Link href="/contact" className="text-madina-green-600 hover:underline font-semibold">Contact us</Link>
            </p>
            <p className="text-sm text-slate-500">
              Cancel anytime • 100% transparent • Halal income
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
