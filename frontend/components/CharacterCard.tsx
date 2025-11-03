'use client'

import { Character } from '@/lib/api'

interface CharacterCardProps {
  character: Character
}

export default function CharacterCard({ character }: CharacterCardProps) {
  return (
    <div className="bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-8 border border-neutral-800 glow-effect">
      <div className="flex flex-col md:flex-row gap-6">
        <div className="relative w-full md:w-64 h-64 rounded-lg overflow-hidden flex-shrink-0">
          <img
            src={character.image}
            alt={character.name}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="flex-1">
          <h2 className="text-3xl font-bold mb-4">{character.name}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-neutral-400 mb-1">Status</p>
              <p className="font-semibold">{character.status}</p>
            </div>
            <div>
              <p className="text-neutral-400 mb-1">Species</p>
              <p className="font-semibold">{character.species}</p>
            </div>
            <div>
              <p className="text-neutral-400 mb-1">Type</p>
              <p className="font-semibold">{character.type || 'Unknown'}</p>
            </div>
            <div>
              <p className="text-neutral-400 mb-1">Gender</p>
              <p className="font-semibold">{character.gender}</p>
            </div>
            {character.origin?.name && (
              <div>
                <p className="text-neutral-400 mb-1">Origin</p>
                <p className="font-semibold">{character.origin.name}</p>
              </div>
            )}
            {character.location?.name && (
              <div>
                <p className="text-neutral-400 mb-1">Location</p>
                <p className="font-semibold">{character.location.name}</p>
              </div>
            )}
          </div>
          <div className="mt-4">
            <p className="text-neutral-400 mb-1">Episodes</p>
            <p className="font-semibold">{character.episode.length}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

