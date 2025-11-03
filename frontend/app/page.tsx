'use client'

import React from 'react'
import { useRouter } from 'next/navigation'

export default function LandingPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-neutral-900 to-black">
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl md:text-7xl font-bold mb-6 leading-tight">
            <span className="gradient-text">Rick & Morty</span>
            <br />
            <span className="text-white">Universe Explorer</span>
          </h1>
          <p className="text-xl md:text-2xl text-neutral-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            Discover every dimension, character, and episode with AI-powered insights, 
            semantic search, and intelligent content generation
          </p>
          <button
            onClick={() => router.push('/dashboard')}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 px-10 py-5 rounded-xl font-bold text-xl transition-all glow-effect hover:scale-105 shadow-lg shadow-purple-500/30"
          >
            Start Exploring →
          </button>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
          <div className="bg-gradient-to-br from-neutral-900/80 to-black rounded-2xl p-6 border border-neutral-800 hover:border-blue-500/50 transition-all hover:scale-105 hover:shadow-lg hover:shadow-blue-500/20">
            <div className="text-5xl mb-4">📍</div>
            <h3 className="text-2xl font-bold mb-2 text-white">Locations</h3>
            <p className="text-neutral-400 mb-4 leading-relaxed">
              Explore every dimension and planet in the Rick & Morty multiverse
            </p>
            <ul className="text-sm text-neutral-500 space-y-1">
              <li>• 100+ unique locations</li>
              <li>• Dimension details</li>
              <li>• Resident information</li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-neutral-900/80 to-black rounded-2xl p-6 border border-neutral-800 hover:border-purple-500/50 transition-all hover:scale-105 hover:shadow-lg hover:shadow-purple-500/20">
            <div className="text-5xl mb-4">🎬</div>
            <h3 className="text-2xl font-bold mb-2 text-white">Episodes</h3>
            <p className="text-neutral-400 mb-4 leading-relaxed">
              Journey through every adventure and episode in the series
            </p>
            <ul className="text-sm text-neutral-500 space-y-1">
              <li>• Complete episode library</li>
              <li>• Character appearances</li>
              <li>• Story summaries</li>
            </ul>
          </div>

          <div className="bg-gradient-to-br from-neutral-900/80 to-black rounded-2xl p-6 border border-neutral-800 hover:border-pink-500/50 transition-all hover:scale-105 hover:shadow-lg hover:shadow-pink-500/20">
            <div className="text-5xl mb-4">👽</div>
            <h3 className="text-2xl font-bold mb-2 text-white">Characters</h3>
            <p className="text-neutral-400 mb-4 leading-relaxed">
              Meet every character across the multiverse with detailed profiles
            </p>
            <ul className="text-sm text-neutral-500 space-y-1">
              <li>• 800+ characters</li>
              <li>• Full character data</li>
              <li>• Episode appearances</li>
            </ul>
          </div>
        </div>

        {/* AI Features Section */}
        <div className="bg-gradient-to-br from-blue-900/20 via-purple-900/20 to-pink-900/20 rounded-2xl p-8 border border-neutral-800">
          <div className="text-center mb-6">
            <div className="text-4xl mb-3">✨</div>
            <h2 className="text-3xl font-bold gradient-text mb-3">AI-Powered Features</h2>
            <p className="text-neutral-300 text-lg">Advanced intelligence for deeper exploration</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
            <div className="bg-black/40 rounded-xl p-5 border border-neutral-800">
              <div className="flex items-start gap-4">
                <div className="text-3xl">🔍</div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-2">Semantic Search</h4>
                  <p className="text-neutral-400 text-sm">
                    Find characters using natural language queries. Search by traits, descriptions, or concepts.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-black/40 rounded-xl p-5 border border-neutral-800">
              <div className="flex items-start gap-4">
                <div className="text-3xl">🤖</div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-2">AI Generation</h4>
                  <p className="text-neutral-400 text-sm">
                    Generate summaries, dialogues, and insights with quality scoring and factuality checks.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-black/40 rounded-xl p-5 border border-neutral-800">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📝</div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-2">Smart Notes</h4>
                  <p className="text-neutral-400 text-sm">
                    Add and organize notes for characters, locations, and episodes. Keep track of your discoveries.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-black/40 rounded-xl p-5 border border-neutral-800">
              <div className="flex items-start gap-4">
                <div className="text-3xl">📊</div>
                <div>
                  <h4 className="text-lg font-semibold text-white mb-2">Quality Scoring</h4>
                  <p className="text-neutral-400 text-sm">
                    Every AI-generated content is evaluated for factuality, completeness, and creativity.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
