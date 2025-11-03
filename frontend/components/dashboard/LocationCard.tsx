'use client'

import { Location } from '@/lib/api'

interface LocationCardProps {
  location: Location
  onClick: (e?: React.MouseEvent) => void
  isSelected: boolean
}

export default function LocationCard({ location, onClick, isSelected }: LocationCardProps) {
  return (
    <div
      onClick={onClick}
      className={`group relative bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-6 border cursor-pointer transition-all hover:scale-[1.02] overflow-hidden ${
        isSelected
          ? 'border-blue-500 shadow-lg shadow-blue-500/20'
          : 'border-neutral-800 hover:border-neutral-700'
      }`}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-2xl font-bold text-white group-hover:text-blue-400 transition-colors">
            {location.name}
          </h3>
          <span className="text-3xl opacity-50 group-hover:opacity-100 transition-opacity">📍</span>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Type:</span>
            <span className="ml-2 text-neutral-400">{location.type}</span>
          </div>
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Dimension:</span>
            <span className="ml-2 text-neutral-400">{location.dimension}</span>
          </div>
          <div className="flex items-center text-neutral-400">
            <span className="w-2 h-2 bg-pink-500 rounded-full mr-2" />
            <span className="font-medium text-neutral-300">Residents:</span>
            <span className="ml-2 text-blue-400 font-semibold">{location.resident_count}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

