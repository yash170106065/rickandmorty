import { notFound } from 'next/navigation'
import Link from 'next/link'
import { api, Resident } from '@/lib/api'
import ResidentList from '@/components/ResidentList'
import SummaryPanel from '@/components/SummaryPanel'

interface LocationPageProps {
  params: { id: string }
}

export default async function LocationPage({ params }: LocationPageProps) {
  const locationId = parseInt(params.id)

  if (isNaN(locationId)) {
    notFound()
  }

  let location
  try {
    location = await api.locations.getById(locationId)
  } catch (err) {
    notFound()
  }

  // Convert full character objects to resident objects for the component
  const residents: Resident[] = location.residents.map((char) => ({
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
          href="/locations"
          className="text-neutral-400 hover:text-neutral-100 mb-4 inline-block"
        >
          ← Back to Locations
        </Link>

        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">{location.name}</h1>
          <div className="text-neutral-400 space-y-1">
            <p>
              <span className="font-medium">Type:</span> {location.type}
            </p>
            <p>
              <span className="font-medium">Dimension:</span> {location.dimension}
            </p>
            <p>
              <span className="font-medium">Residents:</span>{' '}
              {location.residents.length}
            </p>
          </div>
        </div>

        <div className="mb-8">
          <SummaryPanel locationId={locationId} />
        </div>

        <div>
          <h2 className="text-2xl font-semibold mb-4">Residents</h2>
          <ResidentList residents={residents} />
        </div>
      </div>
    </main>
  )
}

