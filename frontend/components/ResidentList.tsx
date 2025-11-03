'use client'

import Link from 'next/link'
import { Resident } from '@/lib/api'

interface ResidentListProps {
  residents: Resident[]
}

export default function ResidentList({ residents }: ResidentListProps) {
  if (residents.length === 0) {
    return (
      <div className="text-neutral-400 text-center py-8">
        No residents found
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {residents.map((resident) => (
        <Link
          key={resident.id}
          href={`/characters/${resident.id}`}
          className="bg-neutral-800 hover:bg-neutral-700 rounded-xl p-4 transition-colors border border-neutral-700"
        >
          <div className="relative w-full aspect-square mb-3 rounded-lg overflow-hidden">
            <img
              src={resident.image}
              alt={resident.name}
              className="w-full h-full object-cover"
            />
          </div>
          <h4 className="font-semibold mb-1">{resident.name}</h4>
          <div className="text-sm text-neutral-400 space-y-1">
            <p>
              <span className="font-medium">Status:</span> {resident.status}
            </p>
            <p>
              <span className="font-medium">Species:</span> {resident.species}
            </p>
          </div>
        </Link>
      ))}
    </div>
  )
}

