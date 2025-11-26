'use client'

import { useEffect, useState } from 'react'
import { Users, UserPlus, Mail, Shield, Trash2, AlertCircle, Check, Loader2 } from 'lucide-react'

interface TeamMember {
  id: string
  full_name: string
  email: string
  role: string
  is_active: boolean
  created_at: string
}

export default function TeamPage() {
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([])
  const [loading, setLoading] = useState(true)
  const [inviting, setInviting] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [currentUserRole, setCurrentUserRole] = useState('')

  const [inviteForm, setInviteForm] = useState({
    email: '',
    full_name: '',
    role: 'org_user'
  })

  useEffect(() => {
    fetchTeamMembers()
    const user = localStorage.getItem('user')
    if (user) {
      const userData = JSON.parse(user)
      setCurrentUserRole(userData.role)
    }
  }, [])

  const fetchTeamMembers = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTeamMembers(data)
      }
    } catch (err) {
      console.error('Failed to fetch team members:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setInviting(true)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/invite`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(inviteForm)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to invite team member')
      }

      setSuccess('Invitation sent successfully!')
      setShowInviteModal(false)
      setInviteForm({ email: '', full_name: '', role: 'org_user' })
      await fetchTeamMembers()
    } catch (err: any) {
      setError(err.message || 'Failed to send invitation')
    } finally {
      setInviting(false)
    }
  }

  const updateMemberRole = async (userId: string, newRole: string) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${userId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ role: newRole })
      })

      if (response.ok) {
        await fetchTeamMembers()
        setSuccess('Role updated successfully')
      }
    } catch (err) {
      setError('Failed to update role')
    }
  }

  const removeMember = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this team member?')) return

    try {
      const token = localStorage.getItem('access_token')
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      await fetchTeamMembers()
      setSuccess('Team member removed')
    } catch (err) {
      setError('Failed to remove team member')
    }
  }

  const getRoleBadge = (role: string) => {
    const styles = {
      super_admin: 'bg-purple-100 text-purple-700',
      org_admin: 'bg-blue-100 text-blue-700',
      org_user: 'bg-green-100 text-green-700'
    }
    return styles[role as keyof typeof styles] || 'bg-slate-100 text-slate-700'
  }

  const getRoleLabel = (role: string) => {
    const labels = {
      super_admin: 'Super Admin',
      org_admin: 'Organization Admin',
      org_user: 'Member'
    }
    return labels[role as keyof typeof labels] || role
  }

  const canManageTeam = currentUserRole === 'org_admin' || currentUserRole === 'super_admin'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 mb-2">Team Management</h1>
          <p className="text-slate-600">Manage your organization&apos;s team members and roles</p>
        </div>
        {canManageTeam && (
          <button
            onClick={() => setShowInviteModal(true)}
            className="flex items-center space-x-2 px-6 py-3 bg-madina-green-500 text-white rounded-xl font-semibold hover:bg-madina-green-600 transition-colors"
          >
            <UserPlus className="w-5 h-5" />
            <span>Invite Member</span>
          </button>
        )}
      </div>

      {/* Alerts */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-xl flex items-start space-x-3">
          <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-green-700">{success}</p>
        </div>
      )}

      {/* Team Members List */}
      <div className="bg-white rounded-2xl border border-slate-200">
        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-8 h-8 text-madina-green-500 animate-spin mx-auto mb-4" />
            <p className="text-slate-600">Loading team members...</p>
          </div>
        ) : teamMembers.length > 0 ? (
          <div className="divide-y divide-slate-200">
            {teamMembers.map((member) => (
              <div key={member.id} className="p-6 hover:bg-slate-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-madina-green-400 to-madina-green-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                      {member.full_name?.charAt(0) || member.email?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-800">{member.full_name}</h3>
                      <p className="text-sm text-slate-600">{member.email}</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadge(member.role)}`}>
                          {getRoleLabel(member.role)}
                        </span>
                        <span className={`w-2 h-2 rounded-full ${member.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        <span className="text-xs text-slate-500">
                          {member.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                    </div>
                  </div>

                  {canManageTeam && member.role !== 'super_admin' && (
                    <div className="flex items-center space-x-3">
                      <select
                        value={member.role}
                        onChange={(e) => updateMemberRole(member.id, e.target.value)}
                        className="px-4 py-2 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-madina-green-500"
                      >
                        <option value="org_user">Member</option>
                        <option value="org_admin">Admin</option>
                      </select>
                      <button
                        onClick={() => removeMember(member.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Remove member"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <Users className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-700 mb-2">No team members yet</h3>
            <p className="text-slate-600">Invite team members to collaborate on your organization</p>
          </div>
        )}
      </div>

      {/* Role Descriptions */}
      <div className="bg-gradient-to-r from-madina-green-50 to-madina-gold-50 rounded-2xl p-6 border border-madina-green-200">
        <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center space-x-2">
          <Shield className="w-5 h-5" />
          <span>Role Permissions</span>
        </h2>
        <div className="grid md:grid-cols-2 gap-4">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4">
            <h3 className="font-bold text-slate-800 mb-2">Organization Admin</h3>
            <ul className="text-sm text-slate-600 space-y-1">
              <li>• Full access to all features</li>
              <li>• Manage team members</li>
              <li>• Update organization settings</li>
              <li>• View billing and usage</li>
            </ul>
          </div>
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-4">
            <h3 className="font-bold text-slate-800 mb-2">Member</h3>
            <ul className="text-sm text-slate-600 space-y-1">
              <li>• Access to all modules</li>
              <li>• Generate content</li>
              <li>• Save and favorite items</li>
              <li>• View organization data</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold text-slate-800 mb-6">Invite Team Member</h2>

            <form onSubmit={handleInvite} className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={inviteForm.full_name}
                  onChange={(e) => setInviteForm({ ...inviteForm, full_name: e.target.value })}
                  required
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="email"
                    value={inviteForm.email}
                    onChange={(e) => setInviteForm({ ...inviteForm, email: e.target.value })}
                    required
                    className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                    placeholder="john@example.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Role
                </label>
                <select
                  value={inviteForm.role}
                  onChange={(e) => setInviteForm({ ...inviteForm, role: e.target.value })}
                  className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                >
                  <option value="org_user">Member</option>
                  <option value="org_admin">Admin</option>
                </select>
              </div>

              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 px-4 py-3 border-2 border-slate-300 text-slate-700 rounded-xl font-semibold hover:bg-slate-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={inviting}
                  className="flex-1 px-4 py-3 bg-madina-green-500 text-white rounded-xl font-semibold hover:bg-madina-green-600 transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {inviting ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Sending...</span>
                    </>
                  ) : (
                    <>
                      <Mail className="w-5 h-5" />
                      <span>Send Invite</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
