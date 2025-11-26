'use client'

import { useState } from 'react'
import { Sparkles, Facebook, Instagram, Twitter, Linkedin, Lock, Zap, Hash, Calendar } from 'lucide-react'
import Link from 'next/link'

export default function SocialStudioPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Social Media Studio</h1>
        <p className="text-slate-600">Generate engaging Islamic content for social media</p>
      </div>

      {/* Upgrade Required */}
      <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-2xl p-12 border border-pink-200 text-center">
        <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
          <Sparkles className="w-10 h-10 text-pink-500" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-3">Social Media Studio Coming Soon</h2>
        <p className="text-slate-600 mb-6 max-w-2xl mx-auto">
          The Social Media Studio will help you create engaging Islamic content for all your social platforms.
          Generate posts, captions, and hashtags with AI assistance.
        </p>

        <div className="flex items-center justify-center space-x-4 mb-8">
          <div className="flex items-center space-x-2 px-4 py-2 bg-white rounded-xl border border-pink-200">
            <Lock className="w-4 h-4 text-pink-500" />
            <span className="text-sm font-medium text-slate-700">Pro Plan Required</span>
          </div>
        </div>

        {/* Platform Icons */}
        <div className="flex items-center justify-center space-x-6 mb-12">
          <div className="w-14 h-14 bg-blue-100 rounded-xl flex items-center justify-center">
            <Facebook className="w-7 h-7 text-blue-600" />
          </div>
          <div className="w-14 h-14 bg-pink-100 rounded-xl flex items-center justify-center">
            <Instagram className="w-7 h-7 text-pink-600" />
          </div>
          <div className="w-14 h-14 bg-sky-100 rounded-xl flex items-center justify-center">
            <Twitter className="w-7 h-7 text-sky-600" />
          </div>
          <div className="w-14 h-14 bg-indigo-100 rounded-xl flex items-center justify-center">
            <Linkedin className="w-7 h-7 text-indigo-600" />
          </div>
        </div>

        {/* Features Preview */}
        <div className="grid md:grid-cols-3 gap-6 text-left">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-pink-100">
            <div className="flex items-center space-x-3 mb-3">
              <Zap className="w-6 h-6 text-pink-500" />
              <h3 className="font-bold text-slate-800">AI Generation</h3>
            </div>
            <p className="text-sm text-slate-600">
              Generate engaging posts tailored to each platform with AI assistance
            </p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-pink-100">
            <div className="flex items-center space-x-3 mb-3">
              <Hash className="w-6 h-6 text-pink-500" />
              <h3 className="font-bold text-slate-800">Smart Hashtags</h3>
            </div>
            <p className="text-sm text-slate-600">
              Get relevant Islamic hashtags to increase your reach and engagement
            </p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-pink-100">
            <div className="flex items-center space-x-3 mb-3">
              <Calendar className="w-6 h-6 text-pink-500" />
              <h3 className="font-bold text-slate-800">Content Calendar</h3>
            </div>
            <p className="text-sm text-slate-600">
              Plan posts for Ramadan, Eid, Jummah, and other Islamic occasions
            </p>
          </div>
        </div>

        {/* Content Types Preview */}
        <div className="mt-12">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Content Types</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { emoji: '🕌', title: 'Masjid Updates', desc: 'Prayer times, events' },
              { emoji: '📿', title: 'Daily Dhikr', desc: 'Morning/evening reminders' },
              { emoji: '📖', title: 'Quran Quotes', desc: 'Verses with translation' },
              { emoji: '💚', title: 'Inspirational', desc: 'Motivational Islamic content' },
              { emoji: '🌙', title: 'Ramadan Posts', desc: 'Special month content' },
              { emoji: '🎉', title: 'Eid Greetings', desc: 'Holiday messages' },
              { emoji: '👨‍👩‍👧‍👦', title: 'Family Tips', desc: 'Islamic parenting advice' },
              { emoji: '📚', title: 'Knowledge', desc: 'Hadith and Islamic facts' }
            ].map((type, index) => (
              <div key={index} className="bg-white rounded-xl p-4 border border-pink-100">
                <div className="text-3xl mb-2">{type.emoji}</div>
                <h4 className="font-bold text-slate-800 text-sm mb-1">{type.title}</h4>
                <p className="text-xs text-slate-600">{type.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Sample Posts */}
        <div className="mt-12">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Sample Generated Posts</h3>
          <div className="grid md:grid-cols-2 gap-6 text-left">
            <div className="bg-white rounded-xl p-6 border border-pink-100 shadow-sm">
              <div className="flex items-center space-x-2 mb-3">
                <Instagram className="w-5 h-5 text-pink-600" />
                <span className="text-sm font-semibold text-slate-700">Instagram Post</span>
              </div>
              <p className="text-slate-700 mb-3 italic">
                &quot;Start your day with gratitude 🌅 Remember: &apos;And He found you lost and guided [you]&apos; (Quran 93:7)
                Let&apos;s make today count! 💚&quot;
              </p>
              <div className="flex flex-wrap gap-1">
                {['#IslamicQuotes', '#MorningMotivation', '#Alhamdulillah', '#MuslimCommunity'].map(tag => (
                  <span key={tag} className="text-xs text-blue-600">{tag}</span>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 border border-pink-100 shadow-sm">
              <div className="flex items-center space-x-2 mb-3">
                <Facebook className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-semibold text-slate-700">Facebook Post</span>
              </div>
              <p className="text-slate-700 mb-3">
                🕌 This Jummah, let&apos;s reflect on the importance of community. Join us for prayers at 1:30 PM.
                The Prophet ﷺ said: &quot;The believers in their mutual kindness, compassion, and sympathy are just like one body.&quot;
              </p>
              <div className="flex flex-wrap gap-1">
                {['#JummahMubarak', '#IslamicCommunity', '#FridayPrayer'].map(tag => (
                  <span key={tag} className="text-xs text-blue-600">{tag}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <Link
            href="/pricing"
            className="inline-block px-8 py-3 bg-gradient-to-r from-pink-500 to-rose-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Upgrade to Pro
          </Link>
        </div>
      </div>
    </div>
  )
}
