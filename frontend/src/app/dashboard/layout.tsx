'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  Heart,
  BookOpen,
  DollarSign,
  MapPin,
  ShoppingBag,
  GraduationCap,
  Sparkles,
  Settings,
  Users,
  LogOut,
  Menu,
  X,
  Bell,
  Search
} from 'lucide-react'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const router = useRouter()
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [organization, setOrganization] = useState<any>(null)

  useEffect(() => {
    // Load user and organization from localStorage
    const storedUser = localStorage.getItem('user')
    const storedOrg = localStorage.getItem('organization')

    if (storedUser) setUser(JSON.parse(storedUser))
    if (storedOrg) setOrganization(JSON.parse(storedOrg))

    // Check if authenticated
    const token = localStorage.getItem('access_token')
    if (!token) {
      router.push('/login')
    }
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    localStorage.removeItem('organization')
    router.push('/')
  }

  const navigation = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      active: pathname === '/dashboard'
    },
    {
      name: 'Du\'a Studio',
      href: '/dashboard/duas',
      icon: Heart,
      active: pathname?.startsWith('/dashboard/duas')
    },
    {
      name: 'Story Studio',
      href: '/dashboard/stories',
      icon: BookOpen,
      active: pathname?.startsWith('/dashboard/stories')
    },
    {
      name: 'Grant Finder',
      href: '/dashboard/grants',
      icon: DollarSign,
      active: pathname?.startsWith('/dashboard/grants')
    },
    {
      name: 'Marketplace',
      href: '/dashboard/marketplace',
      icon: ShoppingBag,
      active: pathname?.startsWith('/dashboard/marketplace')
    },
    {
      name: 'Learning Hub',
      href: '/dashboard/learning',
      icon: GraduationCap,
      active: pathname?.startsWith('/dashboard/learning')
    },
    {
      name: 'Social Studio',
      href: '/dashboard/social',
      icon: Sparkles,
      active: pathname?.startsWith('/dashboard/social')
    },
    {
      name: 'Umrah & Hajj',
      href: '/dashboard/umrah',
      icon: MapPin,
      active: pathname?.startsWith('/dashboard/umrah')
    }
  ]

  const bottomNavigation = [
    {
      name: 'Team',
      href: '/dashboard/team',
      icon: Users,
      active: pathname?.startsWith('/dashboard/team')
    },
    {
      name: 'Settings',
      href: '/dashboard/settings',
      icon: Settings,
      active: pathname?.startsWith('/dashboard/settings')
    }
  ]

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 z-50 h-screen w-72 bg-white border-r border-slate-200 transform transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-slate-200">
            <Link href="/dashboard" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">و</span>
              </div>
              <div>
                <h1 className="text-lg font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                  Global Waqaf
                </h1>
                <p className="text-xs text-slate-500">Tech Platform</p>
              </div>
            </Link>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-slate-400 hover:text-slate-600"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Organization Info */}
          {organization && (
            <div className="px-6 py-4 bg-gradient-to-r from-madina-green-50 to-madina-gold-50 border-b border-slate-200">
              <p className="text-xs text-slate-500 mb-1">Organization</p>
              <h3 className="font-semibold text-slate-800 truncate">{organization.name}</h3>
              <div className="flex items-center space-x-2 mt-2">
                <span className="px-2 py-1 bg-madina-green-100 text-madina-green-700 text-xs font-medium rounded-full">
                  {organization.plan || 'Basic'}
                </span>
                <span className={`w-2 h-2 rounded-full ${organization.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
              </div>
            </div>
          )}

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto py-6 px-3">
            <div className="space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center space-x-3 px-3 py-3 rounded-xl transition-all ${
                      item.active
                        ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white shadow-lg'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                )
              })}
            </div>

            <div className="mt-8 pt-6 border-t border-slate-200 space-y-1">
              {bottomNavigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={`flex items-center space-x-3 px-3 py-3 rounded-xl transition-all ${
                      item.active
                        ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white shadow-lg'
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                )
              })}
            </div>
          </nav>

          {/* User Section */}
          {user && (
            <div className="px-6 py-4 border-t border-slate-200">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-madina-green-400 to-madina-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {user.full_name?.charAt(0) || user.email?.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-slate-800 truncate">{user.full_name}</p>
                    <p className="text-xs text-slate-500 truncate">{user.email}</p>
                  </div>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-red-50 text-red-600 rounded-xl hover:bg-red-100 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:pl-72">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-4 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Mobile menu button */}
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-slate-600 hover:text-slate-800"
            >
              <Menu className="w-6 h-6" />
            </button>

            {/* Search Bar */}
            <div className="hidden md:flex flex-1 max-w-lg">
              <div className="relative w-full">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search modules, features..."
                  className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-4">
              <button className="relative p-2 text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-xl transition-colors">
                <Bell className="w-6 h-6" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              <Link
                href="/pricing"
                className="hidden sm:inline-block px-4 py-2 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white rounded-xl font-medium hover:shadow-lg transition-all"
              >
                Upgrade Plan
              </Link>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}
