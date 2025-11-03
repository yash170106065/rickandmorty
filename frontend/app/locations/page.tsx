import Link from 'next/link'
import { api, Location } from '@/lib/api'
import LocationCard from '@/components/LocationCard'

export default async function LocationsPage() {
  let locations: Location[] = []
  let error: string | null = null

  try {
    locations = await api.locations.getAll()
  } catch (err) {
    error = err instanceof Error ? err.message : 'Failed to load locations'
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
            <span className="gradient-text">Locations</span>
          </h1>
          <p className="text-xl text-neutral-400">Explore all locations across the multiverse</p>
        </div>

        {error ? (
          <div className="bg-red-900/20 border border-red-700 rounded-lg p-4">
            <p className="text-red-400">Error: {error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {locations.map((location) => (
              <LocationCard key={location.id} location={location} />
            ))}
          </div>
        )}
      </div>
    </main>
  )
}

