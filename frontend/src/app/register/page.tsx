'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Building, Mail, Lock, User, Eye, EyeOff, ArrowRight, AlertCircle, CheckCircle2 } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    // User info
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',

    // Organization info
    org_name: '',
    org_type: 'masjid',
    org_country: '',
    org_city: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState({ score: 0, message: '' })

  const checkPasswordStrength = (password: string) => {
    let score = 0
    let message = 'Weak'

    if (password.length >= 8) score++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[^a-zA-Z0-9]/.test(password)) score++

    if (score === 1) message = 'Weak'
    else if (score === 2) message = 'Fair'
    else if (score === 3) message = 'Good'
    else if (score === 4) message = 'Strong'

    setPasswordStrength({ score, message })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (formData.password !== formData.confirm_password) {
      setError('Passwords do not match')
      return
    }

    if (passwordStrength.score < 2) {
      setError('Please use a stronger password')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          full_name: formData.full_name,
          email: formData.email,
          password: formData.password,
          organization_name: formData.org_name,
          organization_type: formData.org_type,
          organization_country: formData.org_country,
          organization_city: formData.org_city
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed')
      }

      // Store token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user', JSON.stringify(data.user))
      localStorage.setItem('organization', JSON.stringify(data.organization))

      // Redirect to dashboard
      router.push('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })

    if (name === 'password') {
      checkPasswordStrength(value)
    }
  }

  const nextStep = () => {
    if (step === 1) {
      // Validate step 1
      if (!formData.full_name || !formData.email || !formData.password || !formData.confirm_password) {
        setError('Please fill in all fields')
        return
      }
      if (formData.password !== formData.confirm_password) {
        setError('Passwords do not match')
        return
      }
      if (passwordStrength.score < 2) {
        setError('Please use a stronger password')
        return
      }
      setError('')
      setStep(2)
    }
  }

  const prevStep = () => {
    setError('')
    setStep(1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-madina-green-50 via-white to-madina-gold-50 flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-3 mb-6">
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

          <h2 className="text-3xl font-bold text-slate-800 mb-2">Create Account</h2>
          <p className="text-slate-600">Start your 14-day free trial on the Basic plan</p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            <div className={`flex items-center space-x-2 ${step >= 1 ? 'text-madina-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 1 ? 'bg-madina-green-500 text-white' : 'bg-slate-200'}`}>
                {step > 1 ? <CheckCircle2 className="w-5 h-5" /> : '1'}
              </div>
              <span className="text-sm font-medium hidden sm:inline">Account</span>
            </div>
            <div className="w-12 h-0.5 bg-slate-300"></div>
            <div className={`flex items-center space-x-2 ${step >= 2 ? 'text-madina-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${step >= 2 ? 'bg-madina-green-500 text-white' : 'bg-slate-200'}`}>
                2
              </div>
              <span className="text-sm font-medium hidden sm:inline">Organization</span>
            </div>
          </div>
        </div>

        {/* Registration Form */}
        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-xl p-8 border border-madina-green-100">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {step === 1 && (
              <>
                {/* Full Name */}
                <div>
                  <label htmlFor="full_name" className="block text-sm font-semibold text-slate-700 mb-2">
                    Full Name
                  </label>
                  <div className="relative">
                    <User className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="text"
                      id="full_name"
                      name="full_name"
                      value={formData.full_name}
                      onChange={handleChange}
                      required
                      className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                      placeholder="John Doe"
                    />
                  </div>
                </div>

                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-slate-700 mb-2">
                    Email Address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>

                {/* Password */}
                <div>
                  <label htmlFor="password" className="block text-sm font-semibold text-slate-700 mb-2">
                    Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      required
                      className="w-full pl-12 pr-12 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    >
                      {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                    </button>
                  </div>
                  {formData.password && (
                    <div className="mt-2">
                      <div className="flex items-center space-x-2">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all duration-300 ${
                              passwordStrength.score === 1 ? 'bg-red-500 w-1/4' :
                              passwordStrength.score === 2 ? 'bg-orange-500 w-2/4' :
                              passwordStrength.score === 3 ? 'bg-yellow-500 w-3/4' :
                              passwordStrength.score === 4 ? 'bg-green-500 w-full' : 'w-0'
                            }`}
                          ></div>
                        </div>
                        <span className="text-xs text-slate-600">{passwordStrength.message}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        Use 8+ characters with uppercase, lowercase, numbers, and symbols
                      </p>
                    </div>
                  )}
                </div>

                {/* Confirm Password */}
                <div>
                  <label htmlFor="confirm_password" className="block text-sm font-semibold text-slate-700 mb-2">
                    Confirm Password
                  </label>
                  <div className="relative">
                    <Lock className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      id="confirm_password"
                      name="confirm_password"
                      value={formData.confirm_password}
                      onChange={handleChange}
                      required
                      className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <button
                  type="button"
                  onClick={nextStep}
                  className="w-full bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 flex items-center justify-center space-x-2"
                >
                  <span>Continue</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </>
            )}

            {step === 2 && (
              <>
                {/* Organization Name */}
                <div>
                  <label htmlFor="org_name" className="block text-sm font-semibold text-slate-700 mb-2">
                    Organization Name
                  </label>
                  <div className="relative">
                    <Building className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                    <input
                      type="text"
                      id="org_name"
                      name="org_name"
                      value={formData.org_name}
                      onChange={handleChange}
                      required
                      className="w-full pl-12 pr-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                      placeholder="Al-Noor Masjid"
                    />
                  </div>
                </div>

                {/* Organization Type */}
                <div>
                  <label htmlFor="org_type" className="block text-sm font-semibold text-slate-700 mb-2">
                    Organization Type
                  </label>
                  <select
                    id="org_type"
                    name="org_type"
                    value={formData.org_type}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                  >
                    <option value="masjid">Masjid/Mosque</option>
                    <option value="organization">Islamic Organization</option>
                    <option value="school">Islamic School</option>
                    <option value="business">Islamic Business</option>
                  </select>
                </div>

                {/* Country */}
                <div>
                  <label htmlFor="org_country" className="block text-sm font-semibold text-slate-700 mb-2">
                    Country
                  </label>
                  <input
                    type="text"
                    id="org_country"
                    name="org_country"
                    value={formData.org_country}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                    placeholder="United States"
                  />
                </div>

                {/* City */}
                <div>
                  <label htmlFor="org_city" className="block text-sm font-semibold text-slate-700 mb-2">
                    City
                  </label>
                  <input
                    type="text"
                    id="org_city"
                    name="org_city"
                    value={formData.org_city}
                    onChange={handleChange}
                    required
                    className="w-full px-4 py-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-madina-green-500 focus:border-transparent transition-all"
                    placeholder="New York"
                  />
                </div>

                {/* Terms */}
                <div className="flex items-start space-x-2">
                  <input
                    type="checkbox"
                    id="terms"
                    required
                    className="w-4 h-4 text-madina-green-600 border-slate-300 rounded focus:ring-madina-green-500 mt-1"
                  />
                  <label htmlFor="terms" className="text-sm text-slate-600">
                    I agree to the{' '}
                    <Link href="/terms" className="text-madina-green-600 hover:underline">
                      Terms of Service
                    </Link>{' '}
                    and{' '}
                    <Link href="/privacy" className="text-madina-green-600 hover:underline">
                      Privacy Policy
                    </Link>
                  </label>
                </div>

                <div className="flex space-x-4">
                  <button
                    type="button"
                    onClick={prevStep}
                    className="flex-1 border-2 border-slate-300 text-slate-700 py-3 rounded-xl font-semibold hover:bg-slate-50 transition-all duration-200"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-2"
                  >
                    {loading ? (
                      <span>Creating...</span>
                    ) : (
                      <>
                        <span>Create Account</span>
                        <ArrowRight className="w-5 h-5" />
                      </>
                    )}
                  </button>
                </div>
              </>
            )}
          </form>

          {step === 1 && (
            <>
              {/* Divider */}
              <div className="mt-8 mb-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-slate-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-slate-500">Already have an account?</span>
                  </div>
                </div>
              </div>

              {/* Login Link */}
              <Link
                href="/login"
                className="block w-full text-center py-3 border-2 border-madina-green-500 text-madina-green-600 rounded-xl font-semibold hover:bg-madina-green-50 transition-all duration-200"
              >
                Sign In
              </Link>
            </>
          )}
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link href="/" className="text-sm text-slate-600 hover:text-madina-green-600 transition-colors">
            ← Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
}
