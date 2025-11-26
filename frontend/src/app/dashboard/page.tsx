'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  Heart,
  BookOpen,
  DollarSign,
  MapPin,
  ShoppingBag,
  GraduationCap,
  Sparkles,
  TrendingUp,
  Users,
  Activity,
  ArrowRight,
  Calendar,
  Clock
} from 'lucide-react'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    totalUsage: 0,
    activeUsers: 0,
    thisMonth: 0,
    plan: 'Basic'
  })

  useEffect(() => {
    // In production, fetch real stats from API
    // For now, using mock data
    setStats({
      totalUsage: 247,
      activeUsers: 12,
      thisMonth: 89,
      plan: 'Basic'
    })
  }, [])

  const quickStats = [
    {
      name: 'Total Usage',
      value: stats.totalUsage,
      change: '+12%',
      icon: Activity,
      color: 'from-blue-500 to-blue-600'
    },
    {
      name: 'Active Users',
      value: stats.activeUsers,
      change: '+3',
      icon: Users,
      color: 'from-purple-500 to-purple-600'
    },
    {
      name: 'This Month',
      value: stats.thisMonth,
      change: '+24%',
      icon: TrendingUp,
      color: 'from-green-500 to-green-600'
    }
  ]

  const modules = [
    {
      name: 'Du\'a & Dhikr Studio',
      description: 'Generate beautiful du\'as with AI',
      icon: Heart,
      gradient: 'from-madina-gold-400 to-madina-gold-500',
      href: '/dashboard/duas',
      usage: '8/10 this month',
      color: 'bg-yellow-50 text-yellow-700'
    },
    {
      name: 'Kids Story Studio',
      description: 'Create Islamic stories for children',
      icon: BookOpen,
      gradient: 'from-purple-500 to-pink-600',
      href: '/dashboard/stories',
      usage: '3/5 this month',
      color: 'bg-purple-50 text-purple-700'
    },
    {
      name: 'Grant Finder',
      description: 'Find funding opportunities',
      icon: DollarSign,
      gradient: 'from-green-500 to-emerald-600',
      href: '/dashboard/grants',
      usage: 'View only',
      color: 'bg-green-50 text-green-700'
    },
    {
      name: 'Marketplace',
      description: 'List services and products',
      icon: ShoppingBag,
      gradient: 'from-orange-500 to-red-600',
      href: '/dashboard/marketplace',
      usage: 'Upgrade to create',
      color: 'bg-orange-50 text-orange-700'
    },
    {
      name: 'Learning Hub',
      description: 'Access Islamic courses',
      icon: GraduationCap,
      gradient: 'from-indigo-500 to-purple-600',
      href: '/dashboard/learning',
      usage: 'Free courses only',
      color: 'bg-indigo-50 text-indigo-700'
    },
    {
      name: 'Social Media Studio',
      description: 'Generate social content',
      icon: Sparkles,
      gradient: 'from-pink-500 to-rose-600',
      href: '/dashboard/social',
      usage: 'Upgrade to unlock',
      color: 'bg-pink-50 text-pink-700'
    },
    {
      name: 'Umrah & Hajj Alerts',
      description: 'Find travel deals',
      icon: MapPin,
      gradient: 'from-blue-500 to-indigo-600',
      href: '/dashboard/umrah',
      usage: '2/5 searches',
      color: 'bg-blue-50 text-blue-700'
    }
  ]

  const recentActivity = [
    {
      action: 'Generated du\'a',
      module: 'Du\'a Studio',
      time: '2 hours ago',
      icon: Heart
    },
    {
      action: 'Searched for grants',
      module: 'Grant Finder',
      time: '5 hours ago',
      icon: DollarSign
    },
    {
      action: 'Created story',
      module: 'Story Studio',
      time: 'Yesterday',
      icon: BookOpen
    }
  ]

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-madina-green-500 to-madina-green-600 rounded-3xl p-8 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/10 rounded-full -ml-24 -mb-24"></div>

        <div className="relative">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">Welcome back! 👋</h1>
              <p className="text-madina-green-50">
                You're on the <span className="font-bold">{stats.plan} Plan</span> • 20% of proceeds support selected masajid
              </p>
            </div>
            <Link
              href="/pricing"
              className="px-6 py-3 bg-white text-madina-green-600 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
            >
              <span>Upgrade Plan</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid md:grid-cols-3 gap-6">
        {quickStats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <div key={index} className="bg-white rounded-2xl p-6 border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center text-white`}>
                  <Icon className="w-6 h-6" />
                </div>
                <span className="text-green-600 text-sm font-semibold">{stat.change}</span>
              </div>
              <h3 className="text-2xl font-bold text-slate-800 mb-1">{stat.value}</h3>
              <p className="text-slate-600">{stat.name}</p>
            </div>
          )
        })}
      </div>

      {/* Modules Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-800">Your Modules</h2>
          <Link href="/pricing" className="text-madina-green-600 hover:text-madina-green-700 font-medium text-sm">
            View All Features →
          </Link>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {modules.map((module, index) => {
            const Icon = module.icon
            return (
              <Link
                key={index}
                href={module.href}
                className="group bg-white rounded-2xl p-6 border border-slate-200 hover:border-madina-green-300 hover:shadow-xl transition-all duration-300"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${module.gradient} rounded-xl flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                  <Icon className="w-7 h-7" />
                </div>
                <h3 className="text-lg font-bold text-slate-800 mb-2 group-hover:text-madina-green-600 transition-colors">
                  {module.name}
                </h3>
                <p className="text-slate-600 text-sm mb-4">
                  {module.description}
                </p>
                <div className={`inline-flex items-center px-3 py-1 ${module.color} rounded-full text-xs font-medium`}>
                  {module.usage}
                </div>
              </Link>
            )
          })}
        </div>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-slate-800">Recent Activity</h3>
            <Clock className="w-5 h-5 text-slate-400" />
          </div>

          <div className="space-y-4">
            {recentActivity.map((activity, index) => {
              const Icon = activity.icon
              return (
                <div key={index} className="flex items-center space-x-4 p-3 hover:bg-slate-50 rounded-xl transition-colors">
                  <div className="w-10 h-10 bg-madina-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Icon className="w-5 h-5 text-madina-green-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-800">{activity.action}</p>
                    <p className="text-sm text-slate-500">{activity.module}</p>
                  </div>
                  <span className="text-xs text-slate-400">{activity.time}</span>
                </div>
              )
            })}
          </div>

          <Link
            href="/dashboard/activity"
            className="block text-center mt-6 text-madina-green-600 hover:text-madina-green-700 font-medium text-sm"
          >
            View All Activity →
          </Link>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-slate-800">Quick Actions</h3>
            <Sparkles className="w-5 h-5 text-slate-400" />
          </div>

          <div className="space-y-3">
            <Link
              href="/dashboard/duas"
              className="block p-4 bg-gradient-to-r from-madina-gold-50 to-madina-gold-100 rounded-xl hover:shadow-md transition-all group"
            >
              <div className="flex items-center space-x-3">
                <Heart className="w-5 h-5 text-madina-gold-600" />
                <span className="font-semibold text-slate-800 group-hover:text-madina-gold-700">Generate New Du'a</span>
              </div>
            </Link>

            <Link
              href="/dashboard/stories"
              className="block p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-xl hover:shadow-md transition-all group"
            >
              <div className="flex items-center space-x-3">
                <BookOpen className="w-5 h-5 text-purple-600" />
                <span className="font-semibold text-slate-800 group-hover:text-purple-700">Create Story</span>
              </div>
            </Link>

            <Link
              href="/dashboard/grants"
              className="block p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-xl hover:shadow-md transition-all group"
            >
              <div className="flex items-center space-x-3">
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="font-semibold text-slate-800 group-hover:text-green-700">Search Grants</span>
              </div>
            </Link>

            <Link
              href="/dashboard/umrah"
              className="block p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl hover:shadow-md transition-all group"
            >
              <div className="flex items-center space-x-3">
                <MapPin className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-slate-800 group-hover:text-blue-700">Find Umrah Deals</span>
              </div>
            </Link>
          </div>
        </div>
      </div>

      {/* Upgrade Banner (for Basic plan) */}
      {stats.plan === 'Basic' && (
        <div className="bg-gradient-to-r from-madina-gold-400 to-madina-gold-500 rounded-3xl p-8 text-white">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h3 className="text-2xl font-bold mb-2">Unlock All Features</h3>
              <p className="text-madina-gold-50">
                Upgrade to Pro or Enterprise to access unlimited AI-powered tools and support masajid worldwide
              </p>
            </div>
            <Link
              href="/pricing"
              className="px-6 py-3 bg-white text-madina-gold-600 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
            >
              View Plans
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
