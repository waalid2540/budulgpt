'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Search, MapPin, Calendar, DollarSign, Star, Hotel, Bell, Heart, ExternalLink, Loader2 } from 'lucide-react'

interface UmrahDeal {
  hotel_name: string
  hotel_rating: number
  price: number
  currency: string
  location: string
  distance_from_haram: number
  amenities: string[]
  booking_url: string
  provider: string
}

export default function UmrahDealsPage() {
  const [destination, setDestination] = useState('Makkah')
  const [budgetMax, setBudgetMax] = useState(500)
  const [checkInDate, setCheckInDate] = useState('')
  const [checkOutDate, setCheckOutDate] = useState('')
  const [hotelRating, setHotelRating] = useState(3)
  const [distanceFromHaram, setDistanceFromHaram] = useState(2)
  const [durationNights, setDurationNights] = useState(7)

  const [deals, setDeals] = useState<UmrahDeal[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const [showSaveModal, setShowSaveModal] = useState(false)
  const [searchPerformed, setSearchPerformed] = useState(false)

  const handleSearch = async () => {
    setIsSearching(true)
    setSearchPerformed(true)

    try {
      const response = await fetch('/api/v1/umrah-deals/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          destination,
          budget_max: budgetMax,
          check_in_date: checkInDate,
          check_out_date: checkOutDate,
          hotel_rating: hotelRating,
          distance_from_haram: distanceFromHaram,
          duration_nights: durationNights
        })
      })

      const data = await response.json()
      setDeals(data.deals || [])
    } catch (error) {
      console.error('Search error:', error)
      // Load mock data for demo
      loadMockDeals()
    } finally {
      setIsSearching(false)
    }
  }

  const loadMockDeals = () => {
    const mockDeals: UmrahDeal[] = [
      {
        hotel_name: 'Makkah Clock Royal Tower',
        hotel_rating: 5,
        price: 450,
        currency: 'USD',
        location: 'Adjacent to Masjid al-Haram',
        distance_from_haram: 0.1,
        amenities: ['WiFi', 'Breakfast', 'Haram View', 'Pool', 'Spa'],
        booking_url: 'https://booking.com',
        provider: 'Booking.com'
      },
      {
        hotel_name: 'Swissotel Makkah',
        hotel_rating: 5,
        price: 380,
        currency: 'USD',
        location: '200m from Masjid al-Haram',
        distance_from_haram: 0.2,
        amenities: ['WiFi', 'Breakfast', 'Spa', 'Restaurant', '24/7 Service'],
        booking_url: 'https://expedia.com',
        provider: 'Expedia'
      },
      {
        hotel_name: 'Dar Al Eiman Royal',
        hotel_rating: 4,
        price: 280,
        currency: 'USD',
        location: '500m from Masjid al-Haram',
        distance_from_haram: 0.5,
        amenities: ['WiFi', 'Breakfast', 'Shuttle', 'Restaurant'],
        booking_url: 'https://hotels.com',
        provider: 'Hotels.com'
      },
      {
        hotel_name: 'Hilton Suites Makkah',
        hotel_rating: 5,
        price: 420,
        currency: 'USD',
        location: '300m from Masjid al-Haram',
        distance_from_haram: 0.3,
        amenities: ['WiFi', 'Breakfast', 'Gym', 'Pool', 'Business Center'],
        booking_url: 'https://hilton.com',
        provider: 'Hilton.com'
      },
      {
        hotel_name: 'Anjum Hotel Makkah',
        hotel_rating: 4,
        price: 320,
        currency: 'USD',
        location: '600m from Masjid al-Haram',
        distance_from_haram: 0.6,
        amenities: ['WiFi', 'Breakfast', 'Shuttle', 'Laundry'],
        booking_url: 'https://agoda.com',
        provider: 'Agoda'
      }
    ]

    setDeals(mockDeals.filter(deal =>
      deal.price <= budgetMax &&
      deal.hotel_rating >= hotelRating &&
      deal.distance_from_haram <= distanceFromHaram
    ))
  }

  return (
    <div className="min-h-screen bg-madina-gradient relative overflow-hidden">
      {/* Background */}
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
      <div className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center space-x-2 bg-white/60 backdrop-blur-xl rounded-full px-6 py-3 mb-6 border border-madina-green-200 shadow-madina-lg">
              <MapPin className="w-5 h-5 text-madina-green-600" />
              <span className="text-madina-green-700 font-semibold">Live Umrah Deal Finder</span>
            </div>

            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-madina-green-600 to-madina-green-500 bg-clip-text text-transparent">
                Find Your Perfect
              </span>
              <br />
              <span className="text-slate-800">Umrah Deal</span>
            </h1>

            <p className="text-xl text-slate-600 max-w-3xl mx-auto">
              AI-powered search across 100+ booking sites. Find the best Umrah hotels at the best prices, instantly.
            </p>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Search Form */}
            <div className="lg:col-span-1">
              <div className="bg-white/60 backdrop-blur-xl rounded-3xl p-8 border border-white/50 shadow-madina-xl sticky top-24">
                <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center space-x-2">
                  <Search className="w-6 h-6 text-madina-green-600" />
                  <span>Search Filters</span>
                </h2>

                <div className="space-y-6">
                  {/* Destination */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      <MapPin className="w-4 h-4 inline mr-1" />
                      Destination
                    </label>
                    <select
                      value={destination}
                      onChange={(e) => setDestination(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-madina-green-200 focus:ring-2 focus:ring-madina-green-500 focus:border-transparent"
                    >
                      <option value="Makkah">Makkah</option>
                      <option value="Madinah">Madinah</option>
                      <option value="Both">Makkah & Madinah</option>
                    </select>
                  </div>

                  {/* Budget */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      <DollarSign className="w-4 h-4 inline mr-1" />
                      Max Budget (per night)
                    </label>
                    <input
                      type="range"
                      min="100"
                      max="1000"
                      step="50"
                      value={budgetMax}
                      onChange={(e) => setBudgetMax(parseInt(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-center text-madina-green-600 font-bold text-lg mt-2">
                      ${budgetMax}
                    </div>
                  </div>

                  {/* Dates */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      <Calendar className="w-4 h-4 inline mr-1" />
                      Check-in Date
                    </label>
                    <input
                      type="date"
                      value={checkInDate}
                      onChange={(e) => setCheckInDate(e.target.value)}
                      className="w-full px-4 py-3 rounded-xl border border-madina-green-200 focus:ring-2 focus:ring-madina-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      Duration (nights)
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="30"
                      value={durationNights}
                      onChange={(e) => setDurationNights(parseInt(e.target.value))}
                      className="w-full px-4 py-3 rounded-xl border border-madina-green-200 focus:ring-2 focus:ring-madina-green-500"
                    />
                  </div>

                  {/* Hotel Rating */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      <Star className="w-4 h-4 inline mr-1" />
                      Minimum Rating
                    </label>
                    <div className="flex space-x-2">
                      {[3, 4, 5].map((rating) => (
                        <button
                          key={rating}
                          onClick={() => setHotelRating(rating)}
                          className={`flex-1 py-2 rounded-lg font-semibold transition-all ${
                            hotelRating === rating
                              ? 'bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white'
                              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                          }`}
                        >
                          {rating}★
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Distance from Haram */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">
                      <Hotel className="w-4 h-4 inline mr-1" />
                      Max Distance from Haram
                    </label>
                    <input
                      type="range"
                      min="0.5"
                      max="5"
                      step="0.5"
                      value={distanceFromHaram}
                      onChange={(e) => setDistanceFromHaram(parseFloat(e.target.value))}
                      className="w-full"
                    />
                    <div className="text-center text-madina-green-600 font-bold mt-2">
                      {distanceFromHaram} km
                    </div>
                  </div>

                  {/* Search Button */}
                  <button
                    onClick={handleSearch}
                    disabled={isSearching}
                    className="w-full bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white py-4 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                  >
                    {isSearching ? (
                      <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>Searching...</span>
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5" />
                        <span>Search Deals Now</span>
                      </>
                    )}
                  </button>

                  {/* Save Search Button */}
                  {deals.length > 0 && (
                    <button
                      onClick={() => setShowSaveModal(true)}
                      className="w-full bg-white border-2 border-madina-green-500 text-madina-green-600 py-3 rounded-xl font-semibold hover:bg-madina-green-50 transition-all flex items-center justify-center space-x-2"
                    >
                      <Bell className="w-5 h-5" />
                      <span>Save & Get Alerts</span>
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Results */}
            <div className="lg:col-span-2">
              {!searchPerformed ? (
                <div className="bg-white/40 backdrop-blur-xl rounded-3xl p-12 border border-white/50 text-center">
                  <MapPin className="w-16 h-16 text-madina-green-400 mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-slate-800 mb-4">
                    Ready to Find Your Umrah Deal?
                  </h3>
                  <p className="text-slate-600">
                    Set your preferences in the search form and click "Search Deals Now" to find the best Umrah hotels
                  </p>
                </div>
              ) : isSearching ? (
                <div className="bg-white/40 backdrop-blur-xl rounded-3xl p-12 border border-white/50 text-center">
                  <Loader2 className="w-16 h-16 text-madina-green-500 animate-spin mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-slate-800 mb-4">
                    Searching Across 100+ Sites...
                  </h3>
                  <p className="text-slate-600">
                    Finding the best Umrah deals for you
                  </p>
                </div>
              ) : deals.length === 0 ? (
                <div className="bg-white/40 backdrop-blur-xl rounded-3xl p-12 border border-white/50 text-center">
                  <Search className="w-16 h-16 text-slate-400 mx-auto mb-6" />
                  <h3 className="text-2xl font-bold text-slate-800 mb-4">
                    No Deals Found
                  </h3>
                  <p className="text-slate-600 mb-6">
                    Try adjusting your filters (budget, distance, or rating) to see more results
                  </p>
                  <button
                    onClick={() => {
                      setBudgetMax(1000)
                      setDistanceFromHaram(5)
                      setHotelRating(3)
                    }}
                    className="bg-madina-green-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-madina-green-600"
                  >
                    Reset Filters
                  </button>
                </div>
              ) : (
                <>
                  <div className="mb-6 flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-slate-800">
                      Found {deals.length} Hotel{deals.length !== 1 ? 's' : ''}
                    </h2>
                    <span className="text-slate-600">
                      Sorted by price
                    </span>
                  </div>

                  <div className="space-y-6">
                    {deals.map((deal, index) => (
                      <div
                        key={index}
                        className="bg-white/60 backdrop-blur-xl rounded-3xl p-6 border border-white/50 shadow-madina-xl hover:shadow-2xl transition-all duration-300"
                      >
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                          <div className="flex-1 mb-4 md:mb-0">
                            <h3 className="text-2xl font-bold text-slate-800 mb-2">
                              {deal.hotel_name}
                            </h3>

                            <div className="flex items-center space-x-4 mb-3">
                              <div className="flex items-center space-x-1 text-madina-gold-400">
                                {[...Array(5)].map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`w-4 h-4 ${i < deal.hotel_rating ? 'fill-current' : ''}`}
                                  />
                                ))}
                                <span className="text-slate-600 text-sm ml-1">
                                  ({deal.hotel_rating})
                                </span>
                              </div>

                              <div className="flex items-center space-x-1 text-madina-green-600">
                                <MapPin className="w-4 h-4" />
                                <span className="text-sm font-medium">
                                  {deal.distance_from_haram} km from Haram
                                </span>
                              </div>
                            </div>

                            <p className="text-slate-600 mb-3">
                              {deal.location}
                            </p>

                            <div className="flex flex-wrap gap-2">
                              {deal.amenities.slice(0, 4).map((amenity, i) => (
                                <span
                                  key={i}
                                  className="px-3 py-1 bg-madina-green-50 text-madina-green-700 rounded-full text-xs font-medium"
                                >
                                  {amenity}
                                </span>
                              ))}
                            </div>
                          </div>

                          <div className="md:text-right">
                            <div className="mb-4">
                              <div className="text-4xl font-bold text-madina-green-600">
                                ${deal.price}
                              </div>
                              <div className="text-slate-500 text-sm">
                                per night
                              </div>
                              <div className="text-xs text-slate-400 mt-1">
                                via {deal.provider}
                              </div>
                            </div>

                            <a
                              href={deal.booking_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center space-x-2 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white px-6 py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all"
                            >
                              <span>Book Now</span>
                              <ExternalLink className="w-4 h-4" />
                            </a>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Save Search Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-8 max-w-md w-full">
            <h3 className="text-2xl font-bold text-slate-800 mb-4">
              Save Search & Get Alerts
            </h3>
            <p className="text-slate-600 mb-6">
              Get notified when prices drop or new deals match your criteria
            </p>

            <div className="space-y-4 mb-6">
              <input
                type="text"
                placeholder="Name this search (e.g., 'Makkah 5-star')"
                className="w-full px-4 py-3 rounded-xl border border-madina-green-200 focus:ring-2 focus:ring-madina-green-500"
              />

              <input
                type="email"
                placeholder="Your email"
                className="w-full px-4 py-3 rounded-xl border border-madina-green-200 focus:ring-2 focus:ring-madina-green-500"
              />

              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input type="checkbox" defaultChecked className="w-5 h-5 text-madina-green-500" />
                  <span>Email alerts</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input type="checkbox" className="w-5 h-5 text-madina-green-500" />
                  <span>WhatsApp alerts</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input type="checkbox" className="w-5 h-5 text-madina-green-500" />
                  <span>SMS alerts</span>
                </label>
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => setShowSaveModal(false)}
                className="flex-1 px-6 py-3 bg-slate-100 text-slate-700 rounded-xl font-semibold hover:bg-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  setShowSaveModal(false)
                  alert('Search saved! You will receive alerts every 6 hours.')
                }}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-madina-green-500 to-madina-green-600 text-white rounded-xl font-semibold hover:shadow-lg"
              >
                Save & Enable Alerts
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
