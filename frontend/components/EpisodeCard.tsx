'use client'

import Link from 'next/link'
import { Episode } from '@/lib/api'

interface EpisodeCardProps {
  episode: Episode
}

export default function EpisodeCard({ episode }: EpisodeCardProps) {
  return (
    <Link href={`/episodes/${episode.id}`}>
      <div className="group relative bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-6 border border-neutral-800 cursor-pointer card-hover overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        <div className="relative z-10">
          <div className="flex items-start justify-between mb-4">
            <h3 className="text-2xl font-bold text-white group-hover:text-purple-400 transition-colors flex-1">
              {episode.name}
            </h3>
            <span className="text-3xl opacity-50 group-hover:opacity-100 transition-opacity ml-4">🎬</span>
          </div>
          <div className="space-y-2 text-sm">
            <div className="flex items-center text-neutral-400">
              <span className="w-2 h-2 bg-purple-500 rounded-full mr-2" />
              <span className="font-medium text-neutral-300">Episode:</span>
              <span className="ml-2 text-purple-400 font-semibold">{episode.episode}</span>
            </div>
            <div className="flex items-center text-neutral-400">
              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
              <span className="font-medium text-neutral-300">Air Date:</span>
              <span className="ml-2 text-neutral-400">{episode.air_date}</span>
            </div>
            <div className="flex items-center text-neutral-400">
              <span className="w-2 h-2 bg-pink-500 rounded-full mr-2" />
              <span className="font-medium text-neutral-300">Characters:</span>
              <span className="ml-2 text-pink-400 font-semibold">{episode.character_count}</span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  )
}

