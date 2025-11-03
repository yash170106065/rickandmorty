import { notFound } from 'next/navigation'
import Link from 'next/link'
import { api } from '@/lib/api'
import CharacterCard from '@/components/CharacterCard'
import NotesSection from '@/components/NotesSection'

interface CharacterPageProps {
  params: { id: string }
}

export default async function CharacterPage({ params }: CharacterPageProps) {
  const characterId = parseInt(params.id)

  if (isNaN(characterId)) {
    notFound()
  }

  let character
  let notes
  try {
    ;[character, notes] = await Promise.all([
      api.characters.getById(characterId),
      api.characters.getNotes(characterId),
    ])
  } catch (err) {
    notFound()
  }

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <Link
          href="/"
          className="text-neutral-400 hover:text-neutral-100 mb-4 inline-block"
        >
          ← Back to Home
        </Link>

        <div className="mb-6">
          <CharacterCard character={character} />
        </div>

        <div>
          <NotesSection characterId={characterId} initialNotes={notes} />
        </div>
      </div>
    </main>
  )
}

