'use client'

import { Character } from '@/lib/api'

interface CharacterGridCardProps {
  character: Character
  onClick: (e?: React.MouseEvent) => void
  isSelected: boolean
}

export default function CharacterGridCard({ character, onClick, isSelected }: CharacterGridCardProps) {
  return (
    <div
      onClick={onClick}
      className={`group relative bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-6 border cursor-pointer transition-all hover:scale-[1.02] overflow-hidden ${
        isSelected
          ? 'border-purple-500 shadow-lg shadow-purple-500/20'
          : 'border-neutral-800 hover:border-neutral-700'
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative z-10">
        <div className="flex items-center gap-4 mb-4">
          <div className="relative w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 border-2 border-neutral-700">
            <img
              src={character.image}
              alt={character.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold text-white group-hover:text-purple-400 transition-colors truncate">
              {character.name}
            </h3>
          </div>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Status:</span>
            <span className="ml-2 text-neutral-400">{character.status}</span>
          </div>
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Species:</span>
            <span className="ml-2 text-neutral-400">{character.species}</span>
          </div>
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-pink-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Episodes:</span>
            <span className="ml-2 text-purple-400 font-semibold">{character.episode?.length || 0}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

