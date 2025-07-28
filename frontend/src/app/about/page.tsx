'use client'

import { motion } from 'framer-motion'
import { Heart, Users, Globe, Award, BookOpen, Star, Mosque, Lightbulb } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-islamic-gradient bg-islamic-pattern">
      {/* Hero Section - Family Legacy */}
      <section className="py-20 lg:py-32">
        <div className="container-islamic">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-islamic"
            >
              <div className="mb-8">
                <span className="inline-block px-4 py-2 bg-islamic-green-100 text-islamic-green-800 rounded-full text-sm font-semibold">
                  🕌 Built on the Foundation of Islamic Wisdom
                </span>
              </div>
              
              <h1 className="text-display mb-8">
                <span className="text-islamic-gradient">Named After</span>
                <br />
                <span className="text-islamic-green-900">My Grandfather</span>
              </h1>
              
              <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 shadow-islamic-xl border border-islamic-green-100 mb-12">
                <div className="flex items-center justify-center mb-6">
                  <div className="w-20 h-20 bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-full flex items-center justify-center shadow-islamic-lg">
                    <span className="text-white font-bold text-3xl arabic">ب</span>
                  </div>
                </div>
                
                <blockquote className="text-body-large text-islamic-green-800 italic leading-relaxed">
                  "Budul AI is named after my grandfather, whose Islamic knowledge and wisdom guided our large family for generations. 
                  Today, we're bringing that same authentic Islamic guidance to 1.8 billion Muslims worldwide through the power of artificial intelligence."
                </blockquote>
                
                <div className="mt-8 p-6 bg-islamic-gold-50 rounded-2xl border-l-4 border-islamic-gold-400">
                  <p className="text-body text-islamic-green-800 leading-relaxed">
                    "As an imam, scholar, and technology entrepreneur with 20+ successful platforms, I'm uniquely positioned to ensure 
                    Budul AI maintains the highest standards of Islamic authenticity while leveraging cutting-edge AI technology."
                  </p>
                  <div className="mt-4 flex items-center justify-center space-x-2">
                    <div className="w-2 h-2 bg-islamic-gold-500 rounded-full"></div>
                    <span className="text-sm font-medium text-islamic-green-700">Founder & Chief Islamic Officer</span>
                    <div className="w-2 h-2 bg-islamic-gold-500 rounded-full"></div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-20 bg-white/80 backdrop-blur-sm">
        <div className="container-islamic">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
            >
              <h2 className="text-headline mb-6 text-islamic-gradient">Our Sacred Mission</h2>
              <div className="space-y-6">
                <div className="card-islamic p-6">
                  <div className="flex items-start space-x-4">
                    <div className="feature-icon-islamic">
                      <Mosque className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-title mb-3 text-islamic-green-900">Preserving Authentic Islamic Knowledge</h3>
                      <p className="text-body text-islamic-green-700">
                        Every response is grounded in authentic Islamic sources - the Quran, authentic Hadith, and scholarly consensus. 
                        We ensure that AI serves Islam, not the other way around.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="card-islamic p-6">
                  <div className="flex items-start space-x-4">
                    <div className="feature-icon-islamic">
                      <Globe className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-title mb-3 text-islamic-green-900">Serving 1.8 Billion Muslims</h3>
                      <p className="text-body text-islamic-green-700">
                        From Morocco to Malaysia, from Nigeria to Indonesia - Budul AI speaks to Muslims in their languages, 
                        understands their cultures, and respects their diverse interpretations within Islamic orthodoxy.
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="card-islamic p-6">
                  <div className="flex items-start space-x-4">
                    <div className="feature-icon-islamic">
                      <Lightbulb className="h-6 w-6" />
                    </div>
                    <div>
                      <h3 className="text-title mb-3 text-islamic-green-900">Innovation with Islamic Values</h3>
                      <p className="text-body text-islamic-green-700">
                        We believe technology should amplify faith, not diminish it. Budul AI represents the marriage of 
                        grandfather's wisdom with tomorrow's technology.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="relative"
            >
              <div className="bg-gradient-to-br from-islamic-green-600 to-islamic-gold-600 rounded-3xl p-8 text-white shadow-islamic-xl">
                <h3 className="text-title mb-6">The Vision</h3>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Star className="h-5 w-5 text-islamic-gold-200" />
                    <span>Become the definitive Islamic AI platform</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Star className="h-5 w-5 text-islamic-gold-200" />
                    <span>Reach $1M+ monthly revenue serving the Ummah</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Star className="h-5 w-5 text-islamic-gold-200" />
                    <span>Maintain 100% Islamic authenticity at scale</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Star className="h-5 w-5 text-islamic-gold-200" />
                    <span>Bridge traditional Islamic scholarship with AI</span>
                  </div>
                </div>
                
                <div className="mt-8 p-4 bg-white/20 rounded-2xl">
                  <p className="text-sm italic">
                    "Just as my grandfather's knowledge guided our family, Budul AI will guide the global Muslim community 
                    into the digital age while staying true to our Islamic roots."
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Technology & Scholarship */}
      <section className="py-20">
        <div className="container-islamic">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-center mb-16"
          >
            <h2 className="text-headline mb-6 text-islamic-gradient">Where Scholarship Meets Technology</h2>
            <p className="text-body-large text-islamic-green-700 max-w-4xl mx-auto">
              Budul AI is built by a unique combination of Islamic scholarship and technology expertise, 
              ensuring both authenticity and innovation.
            </p>
          </motion.div>

          <div className="grid lg:grid-cols-3 gap-8 mb-16">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-center"
            >
              <div className="feature-icon-islamic mx-auto mb-6">
                <BookOpen className="h-8 w-8" />
              </div>
              <h3 className="text-title mb-4 text-islamic-green-900">Islamic Scholarship</h3>
              <ul className="text-body text-islamic-green-700 space-y-2">
                <li>• Imam and Islamic scholar credentials</li>
                <li>• Deep knowledge of Quran and Hadith</li>
                <li>• Understanding of Islamic jurisprudence</li>
                <li>• Respect for madhab differences</li>
                <li>• Cultural sensitivity across Muslim world</li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-center"
            >
              <div className="feature-icon-islamic mx-auto mb-6">
                <Award className="h-8 w-8" />
              </div>
              <h3 className="text-title mb-4 text-islamic-green-900">Technology Expertise</h3>
              <ul className="text-body text-islamic-green-700 space-y-2">
                <li>• 20+ successful tech platforms</li>
                <li>• AI and machine learning expertise</li>
                <li>• Enterprise software development</li>
                <li>• Scalable system architecture</li>
                <li>• Product management excellence</li>
              </ul>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="text-center"
            >
              <div className="feature-icon-islamic mx-auto mb-6">
                <Heart className="h-8 w-8" />
              </div>
              <h3 className="text-title mb-4 text-islamic-green-900">Community Focus</h3>
              <ul className="text-body text-islamic-green-700 space-y-2">
                <li>• Built by Muslims, for Muslims</li>
                <li>• Global Islamic community understanding</li>
                <li>• Family legacy of Islamic guidance</li>
                <li>• Commitment to authentic scholarship</li>
                <li>• Long-term community service vision</li>
              </ul>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Statistics */}
      <section className="py-20 bg-gradient-to-r from-islamic-green-600 to-islamic-gold-600">
        <div className="container-islamic">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="grid md:grid-cols-4 gap-8 text-center text-white"
          >
            <div>
              <div className="text-5xl font-bold mb-2">1.8B+</div>
              <div className="text-islamic-green-100">Muslims Worldwide</div>
              <div className="text-sm opacity-75 mt-1">Our Target Community</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">20+</div>
              <div className="text-islamic-green-100">Tech Platforms</div>
              <div className="text-sm opacity-75 mt-1">Founder's Experience</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">100%</div>
              <div className="text-islamic-green-100">Islamic Authenticity</div>
              <div className="text-sm opacity-75 mt-1">Scholar Verified</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">$1M+</div>
              <div className="text-islamic-green-100">Revenue Goal</div>
              <div className="text-sm opacity-75 mt-1">Monthly Target</div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-20">
        <div className="container-islamic">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
            >
              <h2 className="text-headline mb-6">
                Join the <span className="text-islamic-gradient">Islamic AI Revolution</span>
              </h2>
              <p className="text-body-large text-islamic-green-700 mb-8">
                Be part of building the future of Islamic technology, rooted in authentic scholarship and powered by cutting-edge AI.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link href="/chat">
                  <button className="btn-islamic-primary text-lg px-8 py-4">
                    Experience Budul GPT
                  </button>
                </Link>
                <Link href="/contact">
                  <button className="btn-islamic-outline text-lg px-8 py-4">
                    Partner With Us
                  </button>
                </Link>
              </div>
              
              <div className="mt-12 p-6 bg-islamic-gold-50 rounded-2xl border border-islamic-gold-200">
                <p className="text-body text-islamic-green-800 italic leading-relaxed">
                  "In a world where technology often distances us from our faith, Budul AI brings us closer to authentic Islamic wisdom. 
                  This is not just a business - it's a sacred mission to serve the Ummah."
                </p>
                <div className="mt-4 text-sm font-medium text-islamic-green-700">
                  — Founder, Budul AI
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>
    </div>
  )
}