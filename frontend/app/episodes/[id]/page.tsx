import { notFound } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import ResidentList from '@/components/ResidentList'
import EpisodeSummaryPanel from '@/components/EpisodeSummaryPanel'

interface EpisodePageProps {
  params: { id: string }
}

export default async function EpisodePage({ params }: EpisodePageProps) {
  const episodeId = parseInt(params.id)

  if (isNaN(episodeId)) {
    notFound()
  }

  let episode
  try {
    episode = await api.episodes.getById(episodeId)
  } catch (err) {
    notFound()
  }

  // Convert characters to residents for the component
  const residents = episode.characters.map((char) => ({
    id: char.id,
    name: char.name,
    status: char.status,
    species: char.species,
    image: char.image,
  }))

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto">
        <Link
          href="/episodes"
          className="text-neutral-400 hover:text-neutral-100 mb-4 inline-block"
        >
          ← Back to Episodes
        </Link>

        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">{episode.name}</h1>
          <div className="text-neutral-400 space-y-1">
            <p>
              <span className="font-medium">Episode:</span> {episode.episode}
            </p>
            <p>
              <span className="font-medium">Air Date:</span> {episode.air_date}
            </p>
            <p>
              <span className="font-medium">Characters:</span>{' '}
              {episode.characters.length}
            </p>
          </div>
        </div>

        <div className="mb-8">
          <EpisodeSummaryPanel episodeId={episodeId} />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Characters</h2>
          <ResidentList residents={residents} />
        </div>
      </div>
    </main>
  )
}

