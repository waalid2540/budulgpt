'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Search, MapPin, Calendar, DollarSign, Star, Hotel, Bell, Heart, ExternalLink, Loader2, Plane, Package, ArrowRight, Mail, MessageCircle, Smartphone, CheckCircle } from 'lucide-react'

type SearchType = 'hotels' | 'flights' | 'packages'

interface UmrahDeal {
  hotel_name?: string
  flight_airline?: string
  hotel_rating?: number
  price: number
  currency: string
  location: string
  distance_from_haram?: number
  amenities?: string[]
  booking_url: string
  provider: string
  departure_city?: string
  arrival_city?: string
  flight_class?: string
  stops?: number
  deal_type: 'hotel' | 'flight' | 'package'
}

export default function UmrahDealsPage() {
  const [searchType, setSearchType] = useState<SearchType>('packages')

  // Common fields
  const [destination, setDestination] = useState('Both')
  const [budgetMax, setBudgetMax] = useState(2000)
  const [checkInDate, setCheckInDate] = useState('')
  const [checkOutDate, setCheckOutDate] = useState('')
  const [durationNights, setDurationNights] = useState(7)

  // Hotel-specific fields
  const [hotelRating, setHotelRating] = useState(3)
  const [distanceFromHaram, setDistanceFromHaram] = useState(2)

  // Flight-specific fields
  const [departureCity, setDepartureCity] = useState('')
  const [flightClass, setFlightClass] = useState('economy')
  const [directFlightsOnly, setDirectFlightsOnly] = useState(false)

  const [deals, setDeals] = useState<UmrahDeal[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [searchPerformed, setSearchPerformed] = useState(false)

  // Alert setup state (now at top level)
  const [searchName, setSearchName] = useState('')
  const [userEmail, setUserEmail] = useState('')
  const [userPhone, setUserPhone] = useState('')
  const [alertEmail, setAlertEmail] = useState(true)
  const [alertWhatsApp, setAlertWhatsApp] = useState(false)
  const [alertSMS, setAlertSMS] = useState(false)
  const [alertsConfigured, setAlertsConfigured] = useState(false)

  const handleSearch = async () => {
    setIsSearching(true)
    setSearchPerformed(true)

    try {
      const response = await fetch('/api/v1/umrah-deals/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_type: searchType,
          destination,
          budget_max: budgetMax,
          check_in_date: checkInDate,
          check_out_date: checkOutDate,
          hotel_rating: hotelRating,
          distance_from_haram: distanceFromHaram,
          duration_nights: durationNights,
          departure_city: departureCity,
          flight_class: flightClass,
          direct_flights_only: directFlightsOnly
        })
      })

      const data = await response.json()
      setDeals(data.deals || [])
    } catch (error) {
      console.error('Search error:', error)
      loadMockDeals()
    } finally {
      setIsSearching(false)
    }
  }

  const loadMockDeals = () => {
    const mockDeals: UmrahDeal[] = []

    if (searchType === 'hotels' || searchType === 'packages') {
      mockDeals.push(
        {
          hotel_name: 'Makkah Clock Royal Tower',
          hotel_rating: 5,
          price: searchType === 'packages' ? 1850 : 450,
          currency: 'USD',
          location: 'Adjacent to Masjid al-Haram',
          distance_from_haram: 0.1,
          amenities: ['WiFi', 'Breakfast', 'Haram View', 'Pool', 'Spa'],
          booking_url: 'https://booking.com',
          provider: 'Booking.com',
          deal_type: searchType as 'hotel' | 'package'
        },
        {
          hotel_name: 'Swissotel Makkah',
          hotel_rating: 5,
          price: searchType === 'packages' ? 1680 : 380,
          currency: 'USD',
          location: '200m from Masjid al-Haram',
          distance_from_haram: 0.2,
          amenities: ['WiFi', 'Breakfast', 'Spa', 'Restaurant'],
          booking_url: 'https://expedia.com',
          provider: 'Expedia',
          deal_type: searchType as 'hotel' | 'package'
        },
        {
          hotel_name: 'Dar Al Eiman Royal',
          hotel_rating: 4,
          price: searchType === 'packages' ? 1480 : 280,
          currency: 'USD',
          location: '500m from Masjid al-Haram',
          distance_from_haram: 0.5,
          amenities: ['WiFi', 'Breakfast', 'Shuttle'],
          booking_url: 'https://hotels.com',
          provider: 'Hotels.com',
          deal_type: searchType as 'hotel' | 'package'
        }
      )
    }

    if (searchType === 'flights' || searchType === 'packages') {
      mockDeals.push(
        {
          flight_airline: 'Saudi Airlines',
          price: searchType === 'packages' ? 1850 : 850,
          currency: 'USD',
          location: 'Jeddah (JED)',
          departure_city: departureCity || 'New York (JFK)',
          arrival_city: 'Jeddah (JED)',
          flight_class: flightClass,
          stops: 0,
          booking_url: 'https://saudia.com',
          provider: 'Saudi Airlines',
          deal_type: searchType === 'flights' ? 'flight' : 'package'
        },
        {
          flight_airline: 'Emirates',
          price: searchType === 'packages' ? 1680 : 920,
          currency: 'USD',
          location: 'Jeddah (JED)',
          departure_city: departureCity || 'New York (JFK)',
          arrival_city: 'Jeddah (JED)',
          flight_class: flightClass,
          stops: 1,
          booking_url: 'https://emirates.com',
          provider: 'Emirates',
          deal_type: searchType === 'flights' ? 'flight' : 'package'
        },
        {
          flight_airline: 'Qatar Airways',
          price: searchType === 'packages' ? 1750 : 890,
          currency: 'USD',
          location: 'Jeddah (JED)',
          departure_city: departureCity || 'New York (JFK)',
          arrival_city: 'Jeddah (JED)',
          flight_class: flightClass,
          stops: 1,
          booking_url: 'https://qatarairways.com',
          provider: 'Qatar Airways',
          deal_type: searchType === 'flights' ? 'flight' : 'package'
        }
      )
    }

    setDeals(mockDeals)
  }

  const handleSaveSearch = async () => {
    if (!searchName || !userEmail) {
      alert('Please enter a search name and your email address')
      return
    }

    try {
      const response = await fetch('/api/v1/umrah-deals/save-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          search_criteria: {
            search_type: searchType,
            destination,
            budget_max: budgetMax,
            check_in_date: checkInDate,
            check_out_date: checkOutDate,
            hotel_rating: hotelRating,
            distance_from_haram: distanceFromHaram,
            duration_nights: durationNights,
            departure_city: departureCity,
            flight_class: flightClass
          },
          search_name: searchName,
          alert_enabled: true,
          alert_email: alertEmail,
          alert_whatsapp: alertWhatsApp,
          alert_sms: alertSMS,
          user_email: userEmail,
          user_phone: userPhone
        })
      })

      const data = await response.json()
      if (data.success) {
        alert('✅ Search saved! You will receive alerts when prices drop.')
        setShowSaveModal(false)
        setSearchName('')
      }
    } catch (error) {
      console.error('Save search error:', error)
      alert('Failed to save search. Please try again.')
    }
  }

  const checkAlertsConfigured = () => {
    return userEmail.trim() !== '' && (alertEmail || alertWhatsApp || alertSMS)
  }

  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-madina-green-400/20 to-madina-green-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-madina-gold-400/20 to-madina-gold-500/20 rounded-full blur-3xl animate-pulse"></div>
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-madina-green-100 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-madina-green-500 to-madina-green-600 rounded-xl flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">م</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                  MadinaGPT
                </h1>
              </div>
            </Link>
            <div className="flex items-center space-x-4">
              <Link
                href="/umrah-deals/dashboard"
                className="flex items-center space-x-2 text-slate-700 hover:text-madina-green-600 font-medium transition-colors"
              >
                <Bell className="w-4 h-4" />
                <span>My Alerts</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative pt-24 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-6 border border-madina-green-200 shadow-lg">
              <span className="text-2xl">🕋</span>
              <span className="text-madina-green-700 font-semibold">AI-Powered Umrah Deal Finder</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                Find Best Umrah Deals
              </span>
            </h1>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              Search hotels, flights, and packages. Get instant price alerts via Email, WhatsApp, or SMS!
            </p>
          </div>

          {/* PRICE ALERTS SETUP SECTION - PROMINENT */}
          <div className="mb-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-3xl p-8 shadow-2xl border-4 border-white/50">
            <div className="max-w-4xl mx-auto">
              <div className="flex items-center justify-center space-x-3 mb-6">
                <div className="w-16 h-16 bg-white rounded-2xl flex items-center justify-center">
                  <Bell className="w-8 h-8 text-blue-600" />
                </div>
                <div className="text-center">
                  <h2 className="text-3xl md:text-4xl font-bold text-white mb-2">
                    🔔 Set Up Price Alerts
                  </h2>
                  <p className="text-blue-100 text-lg">
                    Enter your contact info below and we'll notify you when prices drop!
                  </p>
                </div>
              </div>

              <div className="bg-white/95 backdrop-blur-xl rounded-2xl p-6 mb-4">
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Email Input */}
                  <div>
                    <label className="block text-sm font-bold text-slate-800 mb-3 flex items-center space-x-2">
                      <Mail className="w-5 h-5 text-madina-green-500" />
                      <span>Email Address *</span>
                      {userEmail && alertEmail && <CheckCircle className="w-5 h-5 text-green-500" />}
                    </label>
                    <input
                      type="email"
                      value={userEmail}
                      onChange={(e) => setUserEmail(e.target.value)}
                      placeholder="your.email@example.com"
                      className="w-full px-4 py-4 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none text-lg font-semibold"
                    />
                    <div className="flex items-center space-x-2 mt-2">
                      <input
                        type="checkbox"
                        id="alertEmailTop"
                        checked={alertEmail}
                        onChange={(e) => setAlertEmail(e.target.checked)}
                        className="w-5 h-5 text-madina-green-500 border-slate-300 rounded focus:ring-madina-green-500"
                      />
                      <label htmlFor="alertEmailTop" className="text-sm font-medium text-slate-700 cursor-pointer">
                        Send me email alerts
                      </label>
                    </div>
                  </div>

                  {/* Phone Input */}
                  <div>
                    <label className="block text-sm font-bold text-slate-800 mb-3 flex items-center space-x-2">
                      <Smartphone className="w-5 h-5 text-green-500" />
                      <span>Phone Number (for WhatsApp/SMS)</span>
                      {userPhone && (alertWhatsApp || alertSMS) && <CheckCircle className="w-5 h-5 text-green-500" />}
                    </label>
                    <input
                      type="tel"
                      value={userPhone}
                      onChange={(e) => setUserPhone(e.target.value)}
                      placeholder="+1 (555) 123-4567"
                      className="w-full px-4 py-4 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none text-lg font-semibold"
                    />
                    <div className="flex items-center space-x-4 mt-2">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="alertWhatsAppTop"
                          checked={alertWhatsApp}
                          onChange={(e) => setAlertWhatsApp(e.target.checked)}
                          className="w-5 h-5 text-green-500 border-slate-300 rounded focus:ring-green-500"
                        />
                        <label htmlFor="alertWhatsAppTop" className="text-sm font-medium text-slate-700 cursor-pointer flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4 text-green-500" />
                          <span>WhatsApp</span>
                        </label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="alertSMSTop"
                          checked={alertSMS}
                          onChange={(e) => setAlertSMS(e.target.checked)}
                          className="w-5 h-5 text-blue-500 border-slate-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="alertSMSTop" className="text-sm font-medium text-slate-700 cursor-pointer flex items-center space-x-1">
                          <Smartphone className="w-4 h-4 text-blue-500" />
                          <span>SMS</span>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Alert Status */}
              {checkAlertsConfigured() ? (
                <div className="bg-green-500 text-white px-6 py-4 rounded-xl flex items-center space-x-3">
                  <CheckCircle className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <div className="font-bold text-lg">✅ Alerts Configured!</div>
                    <div className="text-sm text-green-100">
                      You'll receive notifications via: {alertEmail && 'Email'}{alertWhatsApp && ' • WhatsApp'}{alertSMS && ' • SMS'}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-yellow-500 text-white px-6 py-4 rounded-xl flex items-center space-x-3">
                  <Bell className="w-6 h-6 flex-shrink-0" />
                  <div>
                    <div className="font-bold text-lg">⚠️ Complete Your Alert Setup</div>
                    <div className="text-sm text-yellow-100">
                      Enter your email and select at least one notification method above
                    </div>
                  </div>
                </div>
              )}

              {/* How it Works */}
              <div className="mt-6 bg-white/20 backdrop-blur-xl rounded-xl p-4 text-white">
                <h3 className="font-bold mb-2 flex items-center space-x-2">
                  <span>💡</span>
                  <span>How Price Alerts Work:</span>
                </h3>
                <ul className="space-y-1 text-sm text-blue-100 ml-6">
                  <li>• AI checks prices every 6 hours automatically</li>
                  <li>• Get notified when prices drop by 10% or more</li>
                  <li>• Receive alerts for new deals matching your criteria</li>
                  <li>• Never miss limited-time offers</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Search Type Tabs */}
          <div className="bg-white/60 backdrop-blur-xl rounded-2xl p-2 border border-white/50 shadow-xl mb-8 max-w-2xl mx-auto">
            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => setSearchType('packages')}
                className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-xl font-semibold transition-all duration-300 ${
                  searchType === 'packages'
                    ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white shadow-lg'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Package className="w-5 h-5" />
                <span>Packages</span>
              </button>
              <button
                onClick={() => setSearchType('hotels')}
                className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-xl font-semibold transition-all duration-300 ${
                  searchType === 'hotels'
                    ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white shadow-lg'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Hotel className="w-5 h-5" />
                <span>Hotels</span>
              </button>
              <button
                onClick={() => setSearchType('flights')}
                className={`flex items-center justify-center space-x-2 px-6 py-4 rounded-xl font-semibold transition-all duration-300 ${
                  searchType === 'flights'
                    ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white shadow-lg'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Plane className="w-5 h-5" />
                <span>Flights</span>
              </button>
            </div>
          </div>

          {/* Search Form */}
          <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 shadow-xl mb-12">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Destination */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-madina-green-500" />
                  <span>Destination</span>
                </label>
                <select
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-madina-green-500 focus:outline-none bg-white"
                >
                  <option value="Makkah">Makkah</option>
                  <option value="Madinah">Madinah</option>
                  <option value="Both">Makkah & Madinah</option>
                </select>
              </div>

              {/* Check-in Date */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-madina-green-500" />
                  <span>Check-in Date</span>
                </label>
                <input
                  type="date"
                  value={checkInDate}
                  onChange={(e) => setCheckInDate(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-madina-green-500 focus:outline-none bg-white"
                />
              </div>

              {/* Check-out Date */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center space-x-2">
                  <Calendar className="w-4 h-4 text-madina-green-500" />
                  <span>Check-out Date</span>
                </label>
                <input
                  type="date"
                  value={checkOutDate}
                  onChange={(e) => setCheckOutDate(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-madina-green-500 focus:outline-none bg-white"
                />
              </div>

              {/* Budget */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <DollarSign className="w-4 h-4 text-madina-green-500" />
                    <span>Max Budget</span>
                  </div>
                  <span className="text-madina-green-600 font-bold">${budgetMax}</span>
                </label>
                <input
                  type="range"
                  min={searchType === 'packages' ? 500 : searchType === 'flights' ? 400 : 100}
                  max={searchType === 'packages' ? 5000 : searchType === 'flights' ? 3000 : 2000}
                  step="50"
                  value={budgetMax}
                  onChange={(e) => setBudgetMax(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-madina-green-500"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>${searchType === 'packages' ? '500' : searchType === 'flights' ? '400' : '100'}</span>
                  <span>${searchType === 'packages' ? '5000' : searchType === 'flights' ? '3000' : '2000'}</span>
                </div>
              </div>

              {/* Duration */}
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
                  <span>Duration</span>
                  <span className="text-madina-green-600 font-bold">{durationNights} nights</span>
                </label>
                <input
                  type="range"
                  min="3"
                  max="30"
                  step="1"
                  value={durationNights}
                  onChange={(e) => setDurationNights(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-madina-green-500"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>3 nights</span>
                  <span>30 nights</span>
                </div>
              </div>

              {/* Hotel-specific fields */}
              {(searchType === 'hotels' || searchType === 'packages') && (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Star className="w-4 h-4 text-madina-green-500" />
                        <span>Hotel Rating</span>
                      </div>
                      <span className="text-madina-green-600 font-bold">{hotelRating}+ stars</span>
                    </label>
                    <input
                      type="range"
                      min="3"
                      max="5"
                      step="1"
                      value={hotelRating}
                      onChange={(e) => setHotelRating(parseInt(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-madina-green-500"
                    />
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                      <span>3 stars</span>
                      <span>5 stars</span>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center justify-between">
                      <span>Distance from Haram</span>
                      <span className="text-madina-green-600 font-bold">{distanceFromHaram} km</span>
                    </label>
                    <input
                      type="range"
                      min="0.1"
                      max="5"
                      step="0.1"
                      value={distanceFromHaram}
                      onChange={(e) => setDistanceFromHaram(parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-madina-green-500"
                    />
                    <div className="flex justify-between text-xs text-slate-500 mt-1">
                      <span>0.1 km</span>
                      <span>5 km</span>
                    </div>
                  </div>
                </>
              )}

              {/* Flight-specific fields */}
              {(searchType === 'flights' || searchType === 'packages') && (
                <>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-3 flex items-center space-x-2">
                      <Plane className="w-4 h-4 text-madina-green-500" />
                      <span>Departure City</span>
                    </label>
                    <input
                      type="text"
                      value={departureCity}
                      onChange={(e) => setDepartureCity(e.target.value)}
                      placeholder="e.g., New York, London, Toronto"
                      className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-madina-green-500 focus:outline-none bg-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-3">
                      Flight Class
                    </label>
                    <select
                      value={flightClass}
                      onChange={(e) => setFlightClass(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-madina-green-500 focus:outline-none bg-white"
                    >
                      <option value="economy">Economy</option>
                      <option value="premium_economy">Premium Economy</option>
                      <option value="business">Business</option>
                      <option value="first">First Class</option>
                    </select>
                  </div>

                  <div className="flex items-center space-x-3 pt-8">
                    <input
                      type="checkbox"
                      id="directFlights"
                      checked={directFlightsOnly}
                      onChange={(e) => setDirectFlightsOnly(e.target.checked)}
                      className="w-5 h-5 text-madina-green-500 border-slate-300 rounded focus:ring-madina-green-500"
                    />
                    <label htmlFor="directFlights" className="text-sm font-semibold text-slate-700 cursor-pointer">
                      Direct flights only
                    </label>
                  </div>
                </>
              )}
            </div>

            {/* Search Button */}
            <div className="mt-8 flex flex-col sm:flex-row gap-4">
              <button
                onClick={handleSearch}
                disabled={isSearching}
                className="flex-1 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSearching ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-6 h-6" />
                    <span>Search Deals</span>
                  </>
                )}
              </button>

              {searchPerformed && deals.length > 0 && checkAlertsConfigured() && (
                <button
                  onClick={() => setShowSaveModal(true)}
                  className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 flex items-center justify-center space-x-3"
                >
                  <Bell className="w-6 h-6" />
                  <span>Save Search & Enable Alerts</span>
                </button>
              )}
            </div>
          </div>

          {/* Results */}
          {searchPerformed && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-3xl font-bold text-slate-800">
                  {deals.length} {searchType} found
                </h2>
                {deals.length > 0 && checkAlertsConfigured() && (
                  <button
                    onClick={() => setShowSaveModal(true)}
                    className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-semibold bg-blue-50 px-6 py-3 rounded-xl hover:bg-blue-100 transition-colors"
                  >
                    <Bell className="w-5 h-5" />
                    <span>Save & Monitor Prices</span>
                  </button>
                )}
              </div>

              {deals.length === 0 ? (
                <div className="text-center py-20 bg-white/40 backdrop-blur-xl rounded-3xl">
                  <div className="w-20 h-20 bg-gradient-to-br from-madina-green-100 to-madina-green-200 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Search className="w-10 h-10 text-madina-green-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-slate-800 mb-4">No deals found</h3>
                  <p className="text-slate-600 mb-6">Try adjusting your search criteria</p>
                </div>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {deals.map((deal, index) => (
                    <div
                      key={index}
                      className="bg-white/60 backdrop-blur-xl rounded-2xl p-6 border border-white/50 hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                    >
                      {/* Deal Header */}
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-slate-800 mb-2">
                            {deal.hotel_name || deal.flight_airline}
                          </h3>
                          {deal.hotel_rating && (
                            <div className="flex items-center space-x-1 mb-2">
                              {[...Array(Math.floor(deal.hotel_rating))].map((_, i) => (
                                <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                              ))}
                            </div>
                          )}
                          <p className="text-sm text-slate-600">{deal.location}</p>
                        </div>
                        <div className="flex-shrink-0 ml-4">
                          <div className="bg-gradient-to-br from-madina-green-500 to-madina-green-600 text-white px-4 py-2 rounded-xl text-center">
                            <div className="text-2xl font-bold">${deal.price}</div>
                            <div className="text-xs">
                              {searchType === 'packages' ? 'total' : searchType === 'flights' ? 'roundtrip' : 'per night'}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Deal Details */}
                      <div className="space-y-2 mb-4">
                        {deal.distance_from_haram !== undefined && (
                          <div className="flex items-center space-x-2 text-sm text-slate-600">
                            <MapPin className="w-4 h-4 text-madina-green-500" />
                            <span>{deal.distance_from_haram} km from Haram</span>
                          </div>
                        )}

                        {deal.departure_city && (
                          <div className="flex items-center space-x-2 text-sm text-slate-600">
                            <Plane className="w-4 h-4 text-madina-green-500" />
                            <span>{deal.departure_city} → {deal.arrival_city}</span>
                          </div>
                        )}

                        {deal.stops !== undefined && (
                          <div className="text-sm text-slate-600">
                            {deal.stops === 0 ? '✓ Direct flight' : `${deal.stops} stop(s)`}
                          </div>
                        )}

                        {deal.flight_class && (
                          <div className="text-sm text-slate-600 capitalize">
                            {deal.flight_class.replace('_', ' ')} class
                          </div>
                        )}

                        {deal.amenities && deal.amenities.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {deal.amenities.slice(0, 3).map((amenity, i) => (
                              <span
                                key={i}
                                className="bg-madina-green-50 text-madina-green-700 px-3 py-1 rounded-lg text-xs font-medium"
                              >
                                {amenity}
                              </span>
                            ))}
                            {deal.amenities.length > 3 && (
                              <span className="text-xs text-slate-500">
                                +{deal.amenities.length - 3} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Provider & CTA */}
                      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                        <span className="text-sm text-slate-500">via {deal.provider}</span>
                        <a
                          href={deal.booking_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-2 bg-madina-green-500 hover:bg-madina-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                        >
                          <span>Book Now</span>
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Save Search Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full p-8 shadow-2xl transform transition-all">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-3xl font-bold text-slate-800 flex items-center space-x-3">
                <Bell className="w-8 h-8 text-blue-500" />
                <span>Save Search & Enable Alerts</span>
              </h3>
              <button
                onClick={() => setShowSaveModal(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-4 mb-6">
              <p className="text-sm text-slate-700">
                <strong>✅ Your alerts are ready!</strong>
              </p>
              <p className="text-sm text-slate-600 mt-2">
                We'll monitor prices and notify you via: <strong>{alertEmail && 'Email'}{alertWhatsApp && ' • WhatsApp'}{alertSMS && ' • SMS'}</strong>
              </p>
            </div>

            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">
                  Give This Search a Name
                </label>
                <input
                  type="text"
                  value={searchName}
                  onChange={(e) => setSearchName(e.target.value)}
                  placeholder="e.g., Ramadan Umrah 2025"
                  className="w-full px-4 py-3 rounded-xl border-2 border-slate-200 focus:border-blue-500 focus:outline-none"
                />
              </div>

              <div className="bg-slate-50 rounded-xl p-4">
                <h4 className="font-semibold text-slate-800 mb-2">📧 Your Alert Contacts:</h4>
                <div className="space-y-2 text-sm text-slate-600">
                  {alertEmail && <div className="flex items-center space-x-2"><Mail className="w-4 h-4 text-madina-green-500" /><span>Email: {userEmail}</span></div>}
                  {alertWhatsApp && <div className="flex items-center space-x-2"><MessageCircle className="w-4 h-4 text-green-500" /><span>WhatsApp: {userPhone}</span></div>}
                  {alertSMS && <div className="flex items-center space-x-2"><Smartphone className="w-4 h-4 text-blue-500" /><span>SMS: {userPhone}</span></div>}
                </div>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowSaveModal(false)}
                className="flex-1 px-6 py-3 border-2 border-slate-200 text-slate-700 rounded-xl font-semibold hover:bg-slate-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveSearch}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl font-semibold hover:shadow-xl transition-all duration-300 flex items-center justify-center space-x-2"
              >
                <Bell className="w-5 h-5" />
                <span>Save & Start Monitoring</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
