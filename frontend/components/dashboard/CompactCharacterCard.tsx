'use client'

import { Character } from '@/lib/api'

interface CompactCharacterCardProps {
  character: Character
}

export default function CompactCharacterCard({ character }: CompactCharacterCardProps) {
  return (
    <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-4 border border-neutral-800 h-full flex flex-col overflow-hidden">
      {/* Photo at top */}
      <div className="flex-shrink-0 mb-4">
        <div className="relative w-32 h-32 mx-auto rounded-lg overflow-hidden border-2 border-neutral-700">
          <img
            src={character.image}
            alt={character.name}
            className="w-full h-full object-cover"
          />
        </div>
        <h2 className="text-lg font-bold mt-3 text-center gradient-text">{character.name}</h2>
      </div>
      
      {/* Scrollable details section */}
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-3">
          <div>
            <span className="text-neutral-500 text-xs block mb-1">Status</span>
            <span className="text-white font-medium text-sm block">{character.status}</span>
          </div>
          <div>
            <span className="text-neutral-500 text-xs block mb-1">Species</span>
            <span className="text-white font-medium text-sm block">{character.species}</span>
          </div>
          <div>
            <span className="text-neutral-500 text-xs block mb-1">Type</span>
            <span className="text-white font-medium text-sm block">{character.type || 'Unknown'}</span>
          </div>
          <div>
            <span className="text-neutral-500 text-xs block mb-1">Gender</span>
            <span className="text-white font-medium text-sm block">{character.gender}</span>
          </div>
          {character.origin?.name && (
            <div>
              <span className="text-neutral-500 text-xs block mb-1">Origin</span>
              <span className="text-white font-medium text-sm block">{character.origin.name}</span>
            </div>
          )}
          {character.location?.name && (
            <div>
              <span className="text-neutral-500 text-xs block mb-1">Location</span>
              <span className="text-white font-medium text-sm block">{character.location.name}</span>
            </div>
          )}
          <div>
            <span className="text-neutral-500 text-xs block mb-1">Episodes</span>
            <span className="text-white font-medium text-sm block">{character.episode?.length || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

