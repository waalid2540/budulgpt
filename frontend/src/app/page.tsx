'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ArrowRight, MessageCircle, Heart, BookOpen, MapPin, DollarSign, Sparkles, Star } from 'lucide-react'

export default function HomePage() {
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const features = [
    {
      icon: <MessageCircle className="w-8 h-8" />,
      title: "Madina GPT",
      description: "Islamic Q&A powered by authentic knowledge",
      gradient: "from-madina-green-500 to-madina-green-600",
      link: "/chat"
    },
    {
      icon: <Heart className="w-8 h-8" />,
      title: "Du'ā Generator",
      description: "Generate beautiful duas with meanings",
      gradient: "from-madina-gold-400 to-madina-gold-500",
      link: "/duas"
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Kids Stories",
      description: "Islamic stories with moral lessons",
      gradient: "from-purple-500 to-pink-600",
      link: "/stories"
    },
    {
      icon: <MapPin className="w-8 h-8" />,
      title: "Umrah Alert",
      description: "Coming soon - AI Umrah planning",
      gradient: "from-blue-500 to-indigo-600",
      link: "#"
    }
  ]

  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-madina-green-400/20 to-madina-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-madina-green-300/10 to-madina-green-500/10 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/80 backdrop-blur-xl border-b border-madina-green-100 shadow-madina-lg'
          : 'bg-transparent'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-madina">
                <span className="text-white font-bold text-xl">م</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                  MadinaGPT
                </h1>
                <p className="text-xs text-madina-green-600 font-medium">Faith • Knowledge • Guidance</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-slate-700 hover:text-madina-green-600 font-medium transition-colors">
                Features
              </Link>
              <Link href="/about" className="text-slate-700 hover:text-madina-green-600 font-medium transition-colors">
                About
              </Link>
              <Link href="/subscribe" className="text-slate-700 hover:text-madina-green-600 font-medium transition-colors">
                Subscribe
              </Link>
            </div>

            {/* CTA Buttons */}
            <div className="flex items-center space-x-4">
              <Link
                href="/donate"
                className="hidden sm:inline-block bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white px-6 py-2 rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Donate
              </Link>
              <Link
                href="/subscribe"
                className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-6 py-2 rounded-xl font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Subscribe
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
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-8 border border-madina-green-200 shadow-madina-lg">
              <span className="text-2xl">🕌</span>
              <span className="text-madina-green-700 font-semibold">Supporting Masjid Madina</span>
              <Sparkles className="w-4 h-4 text-madina-gold-400" />
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-madina-green-600 via-madina-green-500 to-madina-green-600 bg-clip-text text-transparent">
                MadinaGPT
              </span>
              <br />
              <span className="text-slate-800">Faith • Knowledge • Guidance</span>
            </h1>

            {/* Subtitle */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 leading-relaxed max-w-3xl mx-auto">
              Your Islamic AI companion for authentic knowledge, duas, and stories.
              <br />
              <span className="font-bold text-madina-green-600">50% of proceeds support Masjid Madina</span> community programs and da'wah efforts.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link
                href="/subscribe"
                className="group bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-10 py-5 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center space-x-3"
              >
                <DollarSign className="w-6 h-6" />
                <span>Subscribe $9.99/month</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <Link
                href="/donate"
                className="group bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white px-10 py-5 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center space-x-3"
              >
                <Heart className="w-6 h-6" />
                <span>Donate to Masjid Madina</span>
              </Link>
            </div>

            {/* Social Proof */}
            <div className="flex items-center justify-center space-x-8 text-sm text-slate-600">
              <div className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-madina-gold-400 fill-current" />
                <span className="font-medium">Authentic Content</span>
              </div>
              <div className="flex items-center space-x-2">
                <Heart className="w-5 h-5 text-red-500" />
                <span className="font-medium">Supporting Masjid</span>
              </div>
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-madina-green-500" />
                <span className="font-medium">Family Friendly</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                Islamic AI Tools
              </span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Powered by AI, guided by faith - everything you need for Islamic knowledge and guidance
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group relative bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 hover:border-madina-green-200 shadow-madina-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-500"
              >
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 rounded-3xl transition-opacity duration-500`}></div>

                {/* Icon */}
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.gradient} rounded-2xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform duration-300`}>
                  {feature.icon}
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-slate-800 mb-4 group-hover:text-madina-green-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-600 mb-6 leading-relaxed">
                  {feature.description}
                </p>

                {/* CTA Button */}
                {feature.link !== '#' ? (
                  <Link
                    href={feature.link}
                    className={`w-full bg-gradient-to-r ${feature.gradient} text-white py-3 rounded-xl font-semibold text-center block hover:shadow-lg transform hover:scale-105 transition-all duration-200`}
                  >
                    Explore Now
                  </Link>
                ) : (
                  <button
                    disabled
                    className="w-full bg-slate-300 text-slate-600 py-3 rounded-xl font-semibold text-center block cursor-not-allowed"
                  >
                    Coming Soon
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 rounded-3xl p-12 text-white relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute top-0 left-0 w-32 h-32 border border-white rounded-full"></div>
              <div className="absolute top-20 right-20 w-24 h-24 border border-white rounded-full"></div>
              <div className="absolute bottom-10 left-20 w-40 h-40 border border-white rounded-full"></div>
            </div>

            <div className="relative text-center mb-12">
              <h2 className="text-4xl font-bold mb-4">Supporting Masjid Madina</h2>
              <p className="text-madina-green-50 text-lg max-w-3xl mx-auto">
                50% of all subscription proceeds directly fund Masjid Madina's operations, community programs, and da'wah efforts
              </p>
            </div>

            <div className="relative grid md:grid-cols-3 gap-8 text-center">
              <div>
                <div className="text-5xl font-bold mb-2">50%</div>
                <div className="text-madina-green-100 font-medium">Goes to Masjid Madina</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">$9.99</div>
                <div className="text-madina-green-100 font-medium">Per Month Subscription</div>
              </div>
              <div>
                <div className="text-5xl font-bold mb-2">100%</div>
                <div className="text-madina-green-100 font-medium">Transparent & Halal</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Start Your <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">Islamic AI Journey</span>
          </h2>
          <p className="text-xl text-slate-600 mb-12">
            Join MadinaGPT today and support Masjid Madina's mission while accessing authentic Islamic AI tools
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/subscribe"
              className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3"
            >
              <span>Subscribe Now - $9.99/mo</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/donate"
              className="bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 text-white px-8 py-4 rounded-2xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
            >
              Donate to Masjid
            </Link>
          </div>

          {/* Quote */}
          <div className="mt-16 p-8 bg-white/40 backdrop-blur-xl rounded-3xl border border-madina-green-200">
            <p className="text-lg italic text-slate-700 mb-4 font-medium">
              "Your support helps Masjid Madina continue serving the community"
            </p>
            <div className="flex items-center justify-center space-x-2">
              <div className="w-2 h-2 bg-madina-green-400 rounded-full"></div>
              <span className="text-sm text-madina-green-600 font-semibold">MadinaGPT Team</span>
              <div className="w-2 h-2 bg-madina-green-400 rounded-full"></div>
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
                <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">م</span>
                </div>
                <div>
                  <h3 className="text-2xl font-bold">MadinaGPT</h3>
                  <p className="text-slate-400 text-sm">Faith • Knowledge • Guidance</p>
                </div>
              </div>
              <p className="text-slate-300 leading-relaxed">
                Islamic AI platform supporting Masjid Madina. 50% of proceeds fund community programs.
              </p>
            </div>

            {/* Features */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/chat" className="hover:text-madina-green-400 transition-colors">Madina GPT</Link></li>
                <li><Link href="/duas" className="hover:text-madina-green-400 transition-colors">Du'ā Generator</Link></li>
                <li><Link href="/stories" className="hover:text-madina-green-400 transition-colors">Kids Stories</Link></li>
                <li><Link href="#" className="hover:text-madina-green-400 transition-colors">Umrah Alert (Soon)</Link></li>
              </ul>
            </div>

            {/* Support */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/subscribe" className="hover:text-madina-green-400 transition-colors">Subscribe</Link></li>
                <li><Link href="/donate" className="hover:text-madina-green-400 transition-colors">Donate</Link></li>
                <li><Link href="/about" className="hover:text-madina-green-400 transition-colors">About Us</Link></li>
                <li><Link href="/contact" className="hover:text-madina-green-400 transition-colors">Contact</Link></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-slate-300">
                <li><Link href="/privacy" className="hover:text-madina-green-400 transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-madina-green-400 transition-colors">Terms</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-800 pt-8 text-center text-slate-400">
            <p>&copy; 2024 MadinaGPT. Supporting Masjid Madina with Faith, Knowledge, and Guidance.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
