'use client'

import { useState } from 'react'
import { ShoppingBag, Lock } from 'lucide-react'
import Link from 'next/link'

export default function MarketplacePage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Marketplace</h1>
        <p className="text-slate-600">List and discover Islamic services and products</p>
      </div>

      {/* Upgrade Required */}
      <div className="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-12 border border-orange-200 text-center">
        <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
          <ShoppingBag className="w-10 h-10 text-orange-500" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-3">Marketplace Coming Soon</h2>
        <p className="text-slate-600 mb-6 max-w-2xl mx-auto">
          The Marketplace will allow you to list services, products, and connect with other Islamic organizations.
          Pro plan members can create 1 listing, and Enterprise members get unlimited featured listings.
        </p>

        <div className="flex items-center justify-center space-x-4">
          <div className="flex items-center space-x-2 px-4 py-2 bg-white rounded-xl border border-orange-200">
            <Lock className="w-4 h-4 text-orange-500" />
            <span className="text-sm font-medium text-slate-700">Pro Plan Required</span>
          </div>
        </div>

        <div className="mt-8">
          <Link
            href="/pricing"
            className="inline-block px-8 py-3 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Upgrade to Pro
          </Link>
        </div>

        {/* Features Preview */}
        <div className="mt-12 grid md:grid-cols-3 gap-6 text-left">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-orange-100">
            <h3 className="font-bold text-slate-800 mb-2">📦 List Services</h3>
            <p className="text-sm text-slate-600">
              Offer Islamic education, consulting, event planning, and more
            </p>
          </div>
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-orange-100">
            <h3 className="font-bold text-slate-800 mb-2">🛍️ Sell Products</h3>
            <p className="text-sm text-slate-600">
              Islamic books, prayer items, modest fashion, and halal products
            </p>
          </div>
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-orange-100">
            <h3 className="font-bold text-slate-800 mb-2">⭐ Get Featured</h3>
            <p className="text-sm text-slate-600">
              Enterprise members get featured placement and unlimited listings
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
