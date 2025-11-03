'use client'

import { Character } from '@/lib/api'

interface CharacterCardProps {
  character: Character
}

export default function CharacterCard({ character }: CharacterCardProps) {
  return (
    <div className="bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-8 border border-neutral-800 glow-effect">
      <div className="flex flex-col md:flex-row gap-8">
        <div className="relative w-full md:w-64 h-64 rounded-2xl overflow-hidden flex-shrink-0 border-2 border-neutral-700">
          <img
            src={character.image}
            alt={character.name}
            className="w-full h-full object-cover"
          />
        </div>
        <div className="flex-1">
          <h2 className="text-4xl font-bold mb-6 gradient-text">{character.name}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
              <p className="text-neutral-400 text-sm mb-1">Status</p>
              <p className="font-semibold text-xl text-white">{character.status}</p>
            </div>
            <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
              <p className="text-neutral-400 text-sm mb-1">Species</p>
              <p className="font-semibold text-xl text-white">{character.species}</p>
            </div>
            <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
              <p className="text-neutral-400 text-sm mb-1">Type</p>
              <p className="font-semibold text-xl text-white">{character.type || 'Unknown'}</p>
            </div>
            <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
              <p className="text-neutral-400 text-sm mb-1">Gender</p>
              <p className="font-semibold text-xl text-white">{character.gender}</p>
            </div>
            {character.origin?.name && (
              <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
                <p className="text-neutral-400 text-sm mb-1">Origin</p>
                <p className="font-semibold text-xl text-white">{character.origin.name}</p>
              </div>
            )}
            {character.location?.name && (
              <div className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
                <p className="text-neutral-400 text-sm mb-1">Location</p>
                <p className="font-semibold text-xl text-white">{character.location.name}</p>
              </div>
            )}
          </div>
          <div className="mt-6 bg-neutral-800/50 rounded-xl p-4 border border-neutral-700">
            <p className="text-neutral-400 text-sm mb-1">Episodes</p>
            <p className="font-semibold text-xl text-white">{character.episode.length}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

