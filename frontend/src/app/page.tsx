'use client'

import Link from 'next/link'
import {
  ArrowRight,
  CheckCircle,
  Sparkles,
  Heart,
  BookOpen,
  DollarSign,
  MapPin,
  ShoppingBag,
  GraduationCap,
  Users,
  Globe,
  Zap,
  Shield,
  TrendingUp,
  Star,
  Building2,
  ChevronRight,
  BarChart3,
  Lock,
  Workflow
} from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">و</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                Global Waqaf Tech
              </span>
            </Link>

            {/* Navigation Links */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-slate-600 hover:text-madina-green-600 font-medium transition-colors">
                Features
              </Link>
              <Link href="#pricing" className="text-slate-600 hover:text-madina-green-600 font-medium transition-colors">
                Pricing
              </Link>
              <Link href="#impact" className="text-slate-600 hover:text-madina-green-600 font-medium transition-colors">
                Impact
              </Link>
              <Link href="/login" className="text-slate-600 hover:text-madina-green-600 font-medium transition-colors">
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-6 py-2.5 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
              >
                Start Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 px-4 py-2 bg-madina-green-50 border border-madina-green-200 rounded-full mb-8">
              <Sparkles className="w-4 h-4 text-madina-green-600" />
              <span className="text-sm font-semibold text-madina-green-700">
                Trusted by 1,000+ Islamic Organizations Worldwide
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-slate-900 mb-6 leading-tight">
              The Operating System for
              <br />
              <span className="bg-gradient-to-r from-madina-green-600 via-madina-green-500 to-madina-gold-500 bg-clip-text text-transparent">
                Islamic Organizations
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-slate-600 mb-12 max-w-3xl mx-auto leading-relaxed">
              Transform your masjid, Islamic center, or nonprofit with AI-powered tools for content creation,
              fundraising, education, and community engagement. All in one platform.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link
                href="/register"
                className="group px-8 py-4 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
              >
                <span>Start Free Trial</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="#features"
                className="px-8 py-4 bg-white border-2 border-slate-200 text-slate-700 rounded-xl font-semibold text-lg hover:border-madina-green-500 hover:text-madina-green-600 transition-all duration-200 flex items-center space-x-2"
              >
                <span>See How It Works</span>
                <ChevronRight className="w-5 h-5" />
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="mt-16 flex flex-wrap items-center justify-center gap-8 text-sm text-slate-600">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>14-day free trial</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid md:grid-cols-4 gap-8 mt-20">
            {[
              { number: '1,000+', label: 'Organizations', icon: Building2 },
              { number: '50,000+', label: 'Active Users', icon: Users },
              { number: '100K+', label: 'Content Generated', icon: Sparkles },
              { number: '$2M+', label: 'Grants Discovered', icon: DollarSign }
            ].map((stat, index) => (
              <div key={index} className="text-center p-6 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                <stat.icon className="w-8 h-8 text-madina-green-500 mx-auto mb-3" />
                <div className="text-3xl font-bold text-slate-900 mb-1">{stat.number}</div>
                <div className="text-slate-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Everything You Need to Thrive
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Seven powerful modules purpose-built for Islamic organizations
            </p>
          </div>

          {/* Feature Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: Heart,
                title: 'Dua & Dhikr Studio',
                description: 'Generate beautiful Islamic supplications with AI. Perfect for daily posts, prayer guides, and spiritual content.',
                color: 'from-madina-gold-400 to-madina-gold-500'
              },
              {
                icon: BookOpen,
                title: 'Kids Story Studio',
                description: 'Create engaging Islamic stories for children with moral lessons, perfect for classes and family time.',
                color: 'from-purple-500 to-pink-600'
              },
              {
                icon: DollarSign,
                title: 'Grant Finder',
                description: 'Discover funding opportunities with AI-powered search. Track applications and generate winning proposals.',
                color: 'from-green-500 to-emerald-600'
              },
              {
                icon: MapPin,
                title: 'Umrah & Hajj Alerts',
                description: 'Find the best travel deals for sacred journeys. Real-time search powered by advanced AI.',
                color: 'from-blue-500 to-indigo-600'
              },
              {
                icon: ShoppingBag,
                title: 'Marketplace',
                description: 'Connect with Islamic services and products. List your offerings and discover trusted providers.',
                color: 'from-orange-500 to-red-600'
              },
              {
                icon: GraduationCap,
                title: 'Learning Hub',
                description: 'Access Islamic courses and create your own. Track student progress and build your curriculum.',
                color: 'from-indigo-500 to-purple-600'
              },
              {
                icon: Sparkles,
                title: 'Social Media Studio',
                description: 'Generate engaging posts for all platforms. AI-powered captions, hashtags, and content calendar.',
                color: 'from-pink-500 to-rose-600'
              }
            ].map((feature, index) => (
              <div
                key={index}
                className="group p-8 bg-white rounded-2xl border border-slate-200 hover:border-madina-green-300 hover:shadow-2xl transition-all duration-300"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3 group-hover:text-madina-green-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Built for Islamic Organizations
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Not just another SaaS platform—designed specifically for the Muslim community
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Shield,
                title: 'Shariah-Compliant',
                description: 'Every feature designed with Islamic values and principles at the core.'
              },
              {
                icon: Zap,
                title: 'AI-Powered',
                description: 'Cutting-edge artificial intelligence to save time and boost productivity.'
              },
              {
                icon: Globe,
                title: 'Global Impact',
                description: '20% of all proceeds support selected masajid worldwide—your success helps others.'
              },
              {
                icon: Users,
                title: 'Team Collaboration',
                description: 'Invite unlimited team members. Everyone works together seamlessly.'
              },
              {
                icon: BarChart3,
                title: 'Analytics & Insights',
                description: 'Track usage, engagement, and impact with detailed reports and analytics.'
              },
              {
                icon: Lock,
                title: 'Enterprise Security',
                description: 'Bank-level encryption and security. Your data is always protected.'
              }
            ].map((benefit, index) => (
              <div key={index} className="p-8 bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-lg transition-shadow">
                <div className="w-12 h-12 bg-madina-green-100 rounded-xl flex items-center justify-center mb-6">
                  <benefit.icon className="w-6 h-6 text-madina-green-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-3">{benefit.title}</h3>
                <p className="text-slate-600 leading-relaxed">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Choose the plan that fits your organization. Start free, upgrade anytime.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: 'Basic',
                price: 'Free',
                period: 'Forever',
                description: 'Perfect for small masajid',
                features: [
                  'Dua Studio: 10/month',
                  'Story Studio: 5/month',
                  'Grant Finder: View only',
                  'Umrah Finder: 5 searches',
                  'Learning Hub: Free courses',
                  'Basic support'
                ],
                cta: 'Start Free',
                popular: false
              },
              {
                name: 'Pro',
                price: '$29',
                period: 'per month',
                description: 'For growing organizations',
                features: [
                  'Everything Unlimited',
                  'AI-powered features',
                  'Marketplace: 1 listing',
                  'Social Studio: 50 posts/month',
                  'Priority support',
                  'Advanced analytics'
                ],
                cta: 'Start 14-Day Trial',
                popular: true
              },
              {
                name: 'Enterprise',
                price: '$99',
                period: 'per month',
                description: 'For large organizations',
                features: [
                  'Everything Unlimited',
                  'Full AI suite',
                  'Marketplace: Unlimited',
                  'Create your own courses',
                  'Dedicated support',
                  'Custom integrations'
                ],
                cta: 'Contact Sales',
                popular: false
              }
            ].map((plan, index) => (
              <div
                key={index}
                className={`relative p-8 bg-white rounded-3xl border-2 transition-all duration-300 hover:scale-105 ${
                  plan.popular
                    ? 'border-madina-green-500 shadow-2xl'
                    : 'border-slate-200 shadow-lg hover:border-madina-green-300'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-6 py-1.5 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-slate-900 mb-2">{plan.name}</h3>
                  <p className="text-slate-600 mb-6">{plan.description}</p>
                  <div className="mb-2">
                    <span className="text-5xl font-bold text-slate-900">{plan.price}</span>
                    {plan.period && <span className="text-slate-600 ml-2">{plan.period}</span>}
                  </div>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-madina-green-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href="/register"
                  className={`block w-full py-4 rounded-xl font-semibold text-center transition-all duration-200 ${
                    plan.popular
                      ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white hover:shadow-lg transform hover:scale-105'
                      : 'bg-slate-100 text-slate-900 hover:bg-slate-200'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>

          <p className="text-center text-slate-600 mt-12">
            All plans include 20% of proceeds supporting selected masajid worldwide
          </p>
        </div>
      </section>

      {/* Impact Section */}
      <section id="impact" className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-madina-green-50 to-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-4">
              Your Success, Our Mission
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Every subscription helps build a stronger global Muslim community
            </p>
          </div>

          <div className="bg-white rounded-3xl p-12 border border-madina-green-200 shadow-xl">
            <div className="grid md:grid-cols-3 gap-12 text-center">
              <div>
                <div className="text-5xl font-bold text-madina-green-600 mb-2">20%</div>
                <div className="text-slate-600">of all revenue supports masajid worldwide</div>
              </div>
              <div>
                <div className="text-5xl font-bold text-madina-green-600 mb-2">1,000+</div>
                <div className="text-slate-600">organizations empowered globally</div>
              </div>
              <div>
                <div className="text-5xl font-bold text-madina-green-600 mb-2">$2M+</div>
                <div className="text-slate-600">in grants discovered for communities</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-madina-green-500 to-madina-green-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Organization?
          </h2>
          <p className="text-xl text-madina-green-50 mb-12">
            Join 1,000+ Islamic organizations already growing with Global Waqaf Tech
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6">
            <Link
              href="/register"
              className="px-8 py-4 bg-white text-madina-green-600 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-200"
            >
              Start Free Trial
            </Link>
            <Link
              href="/pricing"
              className="px-8 py-4 bg-madina-green-700 text-white rounded-xl font-semibold text-lg hover:bg-madina-green-800 transition-all duration-200"
            >
              View Pricing
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 sm:px-6 lg:px-8 bg-slate-900 text-slate-300">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-xl">و</span>
                </div>
                <span className="text-xl font-bold text-white">Global Waqaf Tech</span>
              </div>
              <p className="text-sm">Empowering Islamic organizations with cutting-edge technology.</p>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/register" className="hover:text-white transition-colors">Sign Up</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#impact" className="hover:text-white transition-colors">Our Impact</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-800 text-center text-sm">
            <p>&copy; 2025 Global Waqaf Tech. All rights reserved. 20% of proceeds support selected masajid worldwide.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
