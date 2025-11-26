'use client'

import Link from 'next/link'
import { Check, Sparkles, Building, Rocket, ArrowRight } from 'lucide-react'

export default function PricingPage() {
  const plans = [
    {
      name: 'Basic',
      price: 'Free',
      period: 'Forever',
      description: 'Perfect for small masajid getting started',
      icon: <Sparkles className="w-8 h-8" />,
      gradient: 'from-slate-500 to-slate-600',
      features: [
        'Dua Studio: 10/month',
        'Story Studio: 5/month',
        'Grant Finder: View only',
        'Umrah Finder: 5 searches/month',
        'Learning Hub: Free courses only',
        'Basic support',
        '20% supports masajid'
      ],
      cta: 'Start Free',
      href: '/register',
      popular: false
    },
    {
      name: 'Pro',
      price: '$29',
      period: 'per month',
      description: 'For growing organizations with advanced needs',
      icon: <Building className="w-8 h-8" />,
      gradient: 'from-madina-green-500 to-madina-green-600',
      features: [
        'Dua Studio: 100/month',
        'Story Studio: 50/month',
        'Grant Finder: Unlimited + AI helpers',
        'Marketplace: 1 listing',
        'Umrah Finder: 50 searches + alerts',
        'Social Studio: 50 posts/month',
        'Learning Hub: All courses',
        'Priority support',
        '20% supports masajid'
      ],
      cta: 'Start Pro Trial',
      href: '/register',
      popular: true
    },
    {
      name: 'Enterprise',
      price: '$99',
      period: 'per month',
      description: 'For large organizations needing full power',
      icon: <Rocket className="w-8 h-8" />,
      gradient: 'from-madina-gold-400 to-madina-gold-500',
      features: [
        'Everything Unlimited',
        'Create your own courses',
        'Marketplace: Unlimited + featured',
        'Social Studio: Unlimited',
        'Grant Finder: Full AI suite',
        'Umrah Finder: Unlimited',
        'Advanced analytics',
        'Dedicated support',
        'Custom integrations',
        '20% supports masajid'
      ],
      cta: 'Start Enterprise Trial',
      href: '/register',
      popular: false
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-madina-green-50 via-white to-madina-gold-50">
      {/* Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <Link href="/" className="inline-flex items-center space-x-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-2xl">و</span>
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                Global Waqaf Tech
              </h1>
              <p className="text-xs text-slate-600">Digital Waqf Network</p>
            </div>
          </Link>

          <h2 className="text-4xl md:text-5xl font-bold text-slate-800 mb-4">
            Choose Your <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">Plan</span>
          </h2>
          <p className="text-xl text-slate-600 max-w-3xl mx-auto">
            Empower your Islamic organization with AI-powered tools.<br />
            <span className="font-bold text-madina-green-600">20% of all proceeds support selected masajid worldwide</span>
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-white/80 backdrop-blur-xl rounded-3xl p-8 border-2 ${
                plan.popular ? 'border-madina-green-500 shadow-2xl scale-105' : 'border-madina-green-100 shadow-xl'
              } transition-all duration-300 hover:scale-105`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-6 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </div>
                </div>
              )}

              {/* Icon */}
              <div className={`w-16 h-16 bg-gradient-to-br ${plan.gradient} rounded-2xl flex items-center justify-center text-white mb-6`}>
                {plan.icon}
              </div>

              {/* Plan Name */}
              <h3 className="text-2xl font-bold text-slate-800 mb-2">{plan.name}</h3>
              <p className="text-slate-600 mb-6">{plan.description}</p>

              {/* Price */}
              <div className="mb-8">
                <div className="flex items-baseline space-x-2">
                  <span className="text-5xl font-bold text-slate-800">{plan.price}</span>
                  {plan.period && <span className="text-slate-600">{plan.period}</span>}
                </div>
              </div>

              {/* Features */}
              <ul className="space-y-4 mb-8">
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start space-x-3">
                    <Check className={`w-5 h-5 text-madina-green-600 flex-shrink-0 mt-0.5`} />
                    <span className="text-slate-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button */}
              <Link
                href={plan.href}
                className={`block w-full bg-gradient-to-r ${plan.gradient} text-white py-4 rounded-xl font-semibold text-center hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center space-x-2`}
              >
                <span>{plan.cta}</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          ))}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-20 text-center">
          <h3 className="text-2xl font-bold text-slate-800 mb-6">All Plans Include:</h3>
          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-madina-green-100">
              <div className="text-3xl mb-2">🕌</div>
              <h4 className="font-semibold text-slate-800 mb-1">Waqf Support</h4>
              <p className="text-sm text-slate-600">20% goes to masajid</p>
            </div>
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-madina-green-100">
              <div className="text-3xl mb-2">🔒</div>
              <h4 className="font-semibold text-slate-800 mb-1">Secure & Private</h4>
              <p className="text-sm text-slate-600">Enterprise security</p>
            </div>
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-madina-green-100">
              <div className="text-3xl mb-2">📊</div>
              <h4 className="font-semibold text-slate-800 mb-1">Usage Analytics</h4>
              <p className="text-sm text-slate-600">Track everything</p>
            </div>
            <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-madina-green-100">
              <div className="text-3xl mb-2">🌍</div>
              <h4 className="font-semibold text-slate-800 mb-1">Global Access</h4>
              <p className="text-sm text-slate-600">Anywhere, anytime</p>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-16 text-center">
          <p className="text-slate-600 mb-4">Need a custom plan for your organization?</p>
          <Link
            href="/contact"
            className="inline-block text-madina-green-600 font-semibold hover:text-madina-green-700 transition-colors"
          >
            Contact us for Enterprise pricing →
          </Link>
        </div>

        {/* Back to Home */}
        <div className="mt-12 text-center">
          <Link href="/" className="text-sm text-slate-600 hover:text-madina-green-600 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
