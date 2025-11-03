import Link from 'next/link'
import { api, Episode } from '@/lib/api'
import EpisodeCard from '@/components/EpisodeCard'

export default async function EpisodesPage() {
  let episodes: Episode[] = []
  let error: string | null = null

  try {
    episodes = await api.episodes.getAll()
  } catch (err) {
    error = err instanceof Error ? err.message : 'Failed to load episodes'
  }

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12">
          <Link
            href="/"
            className="text-neutral-400 hover:text-white mb-4 inline-flex items-center transition-colors group"
          >
            <span className="group-hover:-translate-x-1 transition-transform">←</span>
            <span className="ml-2">Back to Home</span>
          </Link>
          <h1 className="text-5xl md:text-6xl font-bold mb-4">
            <span className="gradient-text">Episodes</span>
          </h1>
          <p className="text-xl text-neutral-400">Discover every adventure across dimensions</p>
        </div>

        {error ? (
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
            <p className="text-red-400">Error: {error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {episodes.map((episode) => (
              <EpisodeCard key={episode.id} episode={episode} />
            ))}
          </div>
        )}
      </div>
    </main>
  )
}

