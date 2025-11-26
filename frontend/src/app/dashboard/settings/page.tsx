'use client'

import { useEffect, useState } from 'react'
import { Building, CreditCard, Bell, Shield, Trash2, Save, AlertCircle, Check } from 'lucide-react'
import Link from 'next/link'

export default function SettingsPage() {
  const [organization, setOrganization] = useState<any>(null)
  const [user, setUser] = useState<any>(null)
  const [activeTab, setActiveTab] = useState<'organization' | 'billing' | 'notifications' | 'security'>('organization')
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const [orgForm, setOrgForm] = useState({
    name: '',
    type: '',
    country: '',
    city: ''
  })

  useEffect(() => {
    const storedOrg = localStorage.getItem('organization')
    const storedUser = localStorage.getItem('user')

    if (storedOrg) {
      const org = JSON.parse(storedOrg)
      setOrganization(org)
      setOrgForm({
        name: org.name || '',
        type: org.type || '',
        country: org.country || '',
        city: org.city || ''
      })
    }
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const handleUpdateOrg = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/organizations/${organization.id}`,
        {
          method: 'PATCH',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(orgForm)
        }
      )

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('organization', JSON.stringify(data))
        setOrganization(data)
        setSuccess('Organization updated successfully')
      } else {
        throw new Error('Failed to update organization')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update organization')
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'organization', label: 'Organization', icon: Building },
    { id: 'billing', label: 'Billing & Plan', icon: CreditCard },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Settings</h1>
        <p className="text-slate-600">Manage your organization settings and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-200 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center space-x-2 px-6 py-3 font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'text-madina-green-600 border-b-2 border-madina-green-600'
                  : 'text-slate-600 hover:text-slate-800'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {/* Organization Tab */}
      {activeTab === 'organization' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Organization Information</h2>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-start space-x-3">
              <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-green-700">{success}</p>
            </div>
          )}

          <form onSubmit={handleUpdateOrg} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Organization Name
                </label>
                <input
                  type="text"
                  value={orgForm.name}
                  onChange={(e) => setOrgForm({ ...orgForm, name: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Organization Type
                </label>
                <select
                  value={orgForm.type}
                  onChange={(e) => setOrgForm({ ...orgForm, type: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  required
                >
                  <option value="">Select type...</option>
                  <option value="masjid">Masjid</option>
                  <option value="islamic_center">Islamic Center</option>
                  <option value="school">Islamic School</option>
                  <option value="nonprofit">Non-Profit Organization</option>
                  <option value="charity">Charity</option>
                  <option value="community">Community Group</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Country
                </label>
                <input
                  type="text"
                  value={orgForm.country}
                  onChange={(e) => setOrgForm({ ...orgForm, country: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  City
                </label>
                <input
                  type="text"
                  value={orgForm.city}
                  onChange={(e) => setOrgForm({ ...orgForm, city: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={saving}
              className="flex items-center space-x-2 px-6 py-3 bg-madina-green-500 text-white rounded-xl font-semibold hover:bg-madina-green-600 transition-colors disabled:opacity-50"
            >
              <Save className="w-5 h-5" />
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </form>
        </div>
      )}

      {/* Billing Tab */}
      {activeTab === 'billing' && (
        <div className="space-y-6">
          {/* Current Plan */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-6">Current Plan</h2>

            <div className="flex items-center justify-between p-6 bg-gradient-to-r from-madina-green-50 to-madina-gold-50 rounded-xl border border-madina-green-200">
              <div>
                <h3 className="text-2xl font-bold text-slate-800 mb-2">
                  {organization?.plan ? organization.plan.charAt(0).toUpperCase() + organization.plan.slice(1) : 'Basic'} Plan
                </h3>
                <p className="text-slate-600">
                  {organization?.plan === 'basic' && 'Free forever with limited features'}
                  {organization?.plan === 'pro' && '$29/month - Full access to all features'}
                  {organization?.plan === 'enterprise' && '$99/month - Unlimited everything'}
                </p>
                <div className="mt-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    organization?.subscription_status === 'active' || organization?.subscription_status === 'trial'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {organization?.subscription_status ?
                      organization.subscription_status.charAt(0).toUpperCase() + organization.subscription_status.slice(1)
                      : 'Active'
                    }
                  </span>
                </div>
              </div>
              <Link
                href="/pricing"
                className="px-6 py-3 bg-madina-green-500 text-white rounded-xl font-semibold hover:bg-madina-green-600 transition-colors"
              >
                {organization?.plan === 'basic' ? 'Upgrade Plan' : 'Change Plan'}
              </Link>
            </div>
          </div>

          {/* Usage Stats */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-6">This Month&apos;s Usage</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="p-4 bg-slate-50 rounded-xl">
                <h4 className="text-sm font-semibold text-slate-600 mb-1">Du&apos;a Studio</h4>
                <p className="text-2xl font-bold text-slate-800">0 / 10</p>
                <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                  <div className="bg-madina-gold-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-xl">
                <h4 className="text-sm font-semibold text-slate-600 mb-1">Story Studio</h4>
                <p className="text-2xl font-bold text-slate-800">0 / 5</p>
                <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
              <div className="p-4 bg-slate-50 rounded-xl">
                <h4 className="text-sm font-semibold text-slate-600 mb-1">Umrah Searches</h4>
                <p className="text-2xl font-bold text-slate-800">0 / 5</p>
                <div className="w-full bg-slate-200 rounded-full h-2 mt-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <div className="bg-white rounded-2xl p-6 border border-slate-200">
          <h2 className="text-xl font-bold text-slate-800 mb-6">Notification Preferences</h2>
          <div className="space-y-4">
            {[
              { label: 'Email notifications for new grants', key: 'grant_alerts' },
              { label: 'Price alerts for saved Umrah searches', key: 'umrah_alerts' },
              { label: 'Weekly usage summary', key: 'usage_summary' },
              { label: 'Team member invitations', key: 'team_invites' },
              { label: 'Product updates and new features', key: 'product_updates' }
            ].map((item) => (
              <label key={item.key} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl cursor-pointer hover:bg-slate-100 transition-colors">
                <span className="text-slate-700 font-medium">{item.label}</span>
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-5 h-5 text-madina-green-600 border-slate-300 rounded focus:ring-madina-green-500"
                />
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200">
            <h2 className="text-xl font-bold text-slate-800 mb-6">Change Password</h2>
            <form className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Current Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  New Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-3 bg-madina-green-500 text-white rounded-xl font-semibold hover:bg-madina-green-600 transition-colors"
              >
                Update Password
              </button>
            </form>
          </div>

          {/* Danger Zone */}
          <div className="bg-red-50 rounded-2xl p-6 border border-red-200">
            <h2 className="text-xl font-bold text-red-800 mb-2">Danger Zone</h2>
            <p className="text-sm text-red-600 mb-4">
              Once you delete your organization, there is no going back. Please be certain.
            </p>
            <button className="flex items-center space-x-2 px-6 py-3 bg-red-600 text-white rounded-xl font-semibold hover:bg-red-700 transition-colors">
              <Trash2 className="w-5 h-5" />
              <span>Delete Organization</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
