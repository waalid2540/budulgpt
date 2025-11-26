'use client'

import { useState } from 'react'
import { GraduationCap, BookOpen, PlayCircle, CheckCircle, Clock, Users } from 'lucide-react'
import Link from 'next/link'

export default function LearningHubPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-800 mb-2">Learning Hub</h1>
        <p className="text-slate-600">Access Islamic courses and educational content</p>
      </div>

      {/* Coming Soon */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-12 border border-indigo-200 text-center">
        <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
          <GraduationCap className="w-10 h-10 text-indigo-500" />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 mb-3">Learning Hub Coming Soon</h2>
        <p className="text-slate-600 mb-6 max-w-2xl mx-auto">
          The Learning Hub will provide access to Islamic courses, lessons, and educational resources.
          Basic members get free courses, Pro members get all courses, and Enterprise members can create their own.
        </p>

        <div className="grid md:grid-cols-3 gap-6 text-left mt-8">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-indigo-100">
            <div className="flex items-center space-x-3 mb-3">
              <BookOpen className="w-6 h-6 text-indigo-500" />
              <h3 className="font-bold text-slate-800">Course Library</h3>
            </div>
            <p className="text-sm text-slate-600">
              Access courses on Quran, Hadith, Fiqh, Seerah, Arabic, and more
            </p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-indigo-100">
            <div className="flex items-center space-x-3 mb-3">
              <PlayCircle className="w-6 h-6 text-indigo-500" />
              <h3 className="font-bold text-slate-800">Video Lessons</h3>
            </div>
            <p className="text-sm text-slate-600">
              High-quality video content from qualified Islamic scholars
            </p>
          </div>

          <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-indigo-100">
            <div className="flex items-center space-x-3 mb-3">
              <CheckCircle className="w-6 h-6 text-indigo-500" />
              <h3 className="font-bold text-slate-800">Track Progress</h3>
            </div>
            <p className="text-sm text-slate-600">
              Monitor your learning journey with completion tracking
            </p>
          </div>
        </div>

        {/* Sample Courses Preview */}
        <div className="mt-12">
          <h3 className="text-xl font-bold text-slate-800 mb-6">Sample Courses</h3>
          <div className="grid md:grid-cols-2 gap-6 text-left">
            {[
              {
                title: 'Introduction to Tajweed',
                instructor: 'Sheikh Ahmad',
                lessons: 12,
                duration: '6 hours',
                level: 'Beginner',
                free: true
              },
              {
                title: 'Understanding Fiqh',
                instructor: 'Dr. Fatima',
                lessons: 20,
                duration: '10 hours',
                level: 'Intermediate',
                free: false
              },
              {
                title: 'Seerah of the Prophet ﷺ',
                instructor: 'Sheikh Omar',
                lessons: 30,
                duration: '15 hours',
                level: 'All Levels',
                free: true
              },
              {
                title: 'Arabic Grammar Essentials',
                instructor: 'Ustadh Ali',
                lessons: 15,
                duration: '8 hours',
                level: 'Beginner',
                free: false
              }
            ].map((course, index) => (
              <div key={index} className="bg-white rounded-xl p-6 border border-indigo-100 shadow-sm">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="font-bold text-slate-800">{course.title}</h4>
                  {course.free && (
                    <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                      Free
                    </span>
                  )}
                </div>
                <p className="text-sm text-slate-600 mb-4">by {course.instructor}</p>
                <div className="flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center space-x-1">
                    <PlayCircle className="w-4 h-4" />
                    <span>{course.lessons} lessons</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{course.duration}</span>
                  </div>
                  <span className="px-2 py-1 bg-indigo-50 text-indigo-700 rounded">
                    {course.level}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8">
          <Link
            href="/pricing"
            className="inline-block px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-200"
          >
            Upgrade for Full Access
          </Link>
        </div>
      </div>
    </div>
  )
}
