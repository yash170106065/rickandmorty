'use client'

import Link from 'next/link'
import { UnifiedSearchResult } from '@/lib/api'

interface SearchResultsListProps {
  results: UnifiedSearchResult[]
}

export default function SearchResultsList({
  results,
}: SearchResultsListProps) {
  if (results.length === 0) {
    return (
      <div className="text-neutral-400 text-center py-8">
        No results found
      </div>
    )
  }

  const getRoute = (entityType: string, entityId: string) => {
    if (entityType === 'character') {
      return `/dashboard/characters?characterId=${entityId}`
    } else if (entityType === 'location') {
      return `/dashboard/locations?locationId=${entityId}`
    } else if (entityType === 'episode') {
      return `/dashboard/episodes?episodeId=${entityId}`
    }
    return '#'
  }

  const getTypeBadgeColor = (entityType: string) => {
    if (entityType === 'character') {
      return 'bg-blue-600/20 text-blue-400 border-blue-600/50'
    } else if (entityType === 'location') {
      return 'bg-purple-600/20 text-purple-400 border-purple-600/50'
    } else if (entityType === 'episode') {
      return 'bg-pink-600/20 text-pink-400 border-pink-600/50'
    }
    return 'bg-neutral-700 text-neutral-400 border-neutral-600'
  }

  return (
    <div className="space-y-4">
      {results.map((result, index) => (
        <Link
          key={`${result.entity_type}-${result.entity_id}-${index}`}
          href={getRoute(result.entity_type, result.entity_id)}
          className="block bg-gradient-to-br from-neutral-800 to-neutral-900 hover:from-neutral-700 hover:to-neutral-800 rounded-xl p-6 transition-all border border-neutral-700 hover:border-neutral-600 shadow-lg hover:shadow-xl"
        >
          <div className="flex gap-4 items-start">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="font-semibold text-xl text-white truncate">
                  {result.name}
                </h3>
                <span
                  className={`px-2 py-1 rounded-lg text-xs font-semibold border capitalize flex-shrink-0 ${getTypeBadgeColor(
                    result.entity_type
                  )}`}
                >
                  {result.entity_type}
                </span>
              </div>
              <p className="text-sm text-neutral-400 line-clamp-2">
                {result.snippet}
              </p>
            </div>
            <div className="flex items-center flex-shrink-0">
              <div className="text-right">
                <p className="text-xs text-neutral-500 mb-1">Similarity</p>
                <p className="text-2xl font-bold text-green-400">
                  {(result.similarity * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  )
}
