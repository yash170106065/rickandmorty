'use client'

import { useState } from 'react'
import { GeneratedContent, api } from '@/lib/api'

interface EpisodeSummaryPanelProps {
  episodeId: number
}

export default function EpisodeSummaryPanel({
  episodeId,
}: EpisodeSummaryPanelProps) {
  const [summary, setSummary] = useState<GeneratedContent | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const content = await api.generation.generateEpisodeSummary(episodeId)
      setSummary(content)
    } catch (err) {
      setError('Failed to generate summary. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-neutral-800 rounded-xl p-6 border border-neutral-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-semibold">AI Episode Summary</h3>
        <button
          onClick={handleGenerate}
          disabled={isLoading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded-lg transition-colors"
        >
          {isLoading ? 'Generating...' : 'Generate Summary'}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 mb-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      {summary && (
        <div className="space-y-4">
          <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-4">
            <p className="text-neutral-300 whitespace-pre-wrap leading-relaxed">
              {summary.output_text}
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-4">
              <p className="text-neutral-400 text-sm mb-1">Factual Accuracy</p>
              {summary.factual_score >= 0 ? (
                <p className="text-2xl font-bold text-green-400">
                  {(summary.factual_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-2xl font-bold text-neutral-500">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500 mt-1">
                Measures grounding in real data
              </p>
            </div>
            <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-4">
              <p className="text-neutral-400 text-sm mb-1">Completeness</p>
              {summary.completeness_score >= 0 ? (
                <p className="text-2xl font-bold text-blue-400">
                  {(summary.completeness_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-2xl font-bold text-neutral-500">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500 mt-1">
                Measures coverage of information
              </p>
            </div>
            <div className="bg-neutral-900 border border-neutral-700 rounded-lg p-4">
              <p className="text-neutral-400 text-sm mb-1">Creativity</p>
              {summary.creativity_score >= 0 ? (
                <p className="text-2xl font-bold text-purple-400">
                  {(summary.creativity_score * 100).toFixed(0)}%
                </p>
              ) : (
                <p className="text-2xl font-bold text-neutral-500">
                  <span className="inline-block animate-pulse">Processing...</span>
                </p>
              )}
              <p className="text-xs text-neutral-500 mt-1">
                Measures narrative quality
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

