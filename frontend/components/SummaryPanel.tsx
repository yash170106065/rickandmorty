'use client'

import { useState } from 'react'
import { GeneratedContent, api } from '@/lib/api'

interface SummaryPanelProps {
  locationId: number
}

export default function SummaryPanel({ locationId }: SummaryPanelProps) {
  const [summary, setSummary] = useState<GeneratedContent | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const content = await api.generation.generateLocationSummary(locationId)
      setSummary(content)
    } catch (err) {
      setError('Failed to generate summary. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-8 border border-neutral-800 glow-effect">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-3xl font-bold mb-2 gradient-text">AI Summary</h3>
          <p className="text-neutral-400 text-sm">Generate an intelligent summary with evaluation metrics</p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-xl font-semibold transition-all glow-effect disabled:glow-effect-0"
        >
          {isLoading ? (
            <span className="flex items-center">
              <span className="animate-spin mr-2">⚡</span>
              Generating...
            </span>
          ) : (
            'Generate Summary'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {summary && (
        <div className="space-y-4">
          <div className="bg-gradient-to-br from-neutral-900 to-black border border-neutral-800 rounded-2xl p-6 shadow-xl">
            <p className="text-neutral-200 whitespace-pre-wrap leading-relaxed text-lg">
              {summary.output_text}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gradient-to-br from-green-500/10 to-green-500/5 border border-green-500/20 rounded-xl p-6 glow-effect">
              <div className="flex items-center mb-3">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">✓</span>
                </div>
                <p className="text-neutral-400 text-sm font-medium">Factual Accuracy</p>
              </div>
              {summary.factual_score >= 0 ? (
                <p className="text-4xl font-bold text-green-400 mb-2">
                  {(summary.factual_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-4xl font-bold text-neutral-500 mb-2">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500">
                Grounded in real data
              </p>
            </div>
            <div className="bg-gradient-to-br from-blue-500/10 to-blue-500/5 border border-blue-500/20 rounded-xl p-6 glow-effect">
              <div className="flex items-center mb-3">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">📊</span>
                </div>
                <p className="text-neutral-400 text-sm font-medium">Completeness</p>
              </div>
              {summary.completeness_score >= 0 ? (
                <p className="text-4xl font-bold text-blue-400 mb-2">
                  {(summary.completeness_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-4xl font-bold text-neutral-500 mb-2">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500">
                Coverage of information
              </p>
            </div>
            <div className="bg-gradient-to-br from-purple-500/10 to-purple-500/5 border border-purple-500/20 rounded-xl p-6 glow-effect">
              <div className="flex items-center mb-3">
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-2xl">✨</span>
                </div>
                <p className="text-neutral-400 text-sm font-medium">Creativity</p>
              </div>
              {summary.creativity_score >= 0 ? (
                <p className="text-4xl font-bold text-purple-400 mb-2">
                  {(summary.creativity_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-4xl font-bold text-neutral-500 mb-2">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500">
                Narrative quality
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

