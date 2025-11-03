'use client'

import { useState, useEffect } from 'react'
import { Location, Character, Episode } from '@/lib/api'

type EntityItem = Location | Character | Episode

interface DashboardSidebarProps {
  width: number
  onWidthChange: (width: number) => void
  selectedView: 'locations' | 'characters' | 'episodes' | null
  onViewChange: (view: 'locations' | 'characters' | 'episodes' | null) => void
  onItemSelect: (item: EntityItem | null) => void
}

export default function DashboardSidebar({
  width,
  onWidthChange,
  selectedView,
  onViewChange,
  onItemSelect,
}: DashboardSidebarProps) {
  const [isResizing, setIsResizing] = useState(false)

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsResizing(true)
  }

  useEffect(() => {
    if (!isResizing) return

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = Math.max(200, Math.min(400, e.clientX))
      onWidthChange(newWidth)
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isResizing, onWidthChange])

  return (
    <div
      className="bg-gradient-to-b from-neutral-900 to-black border-r border-neutral-800 h-full relative overflow-hidden"
      style={{ width: `${width}px` }}
    >
      {/* Resize Handle */}
      <div
        className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
        onMouseDown={handleMouseDown}
      />

      {/* Sidebar Content */}
      <div className="h-full flex flex-col p-4">
        <div className="mb-6">
          <h2 className="text-xl font-bold gradient-text">Explore</h2>
          <p className="text-xs text-neutral-500 mt-1">Navigate the universe</p>
        </div>

        <nav className="space-y-2 flex-1">
          <button
            onClick={() => {
              onViewChange('locations')
              onItemSelect(null)
            }}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all ${
              selectedView === 'locations'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'bg-neutral-800/50 hover:bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="text-lg">📍</span>
              <span className="font-medium text-sm">Locations</span>
            </div>
          </button>

          <button
            onClick={() => {
              onViewChange('characters')
              onItemSelect(null)
            }}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all ${
              selectedView === 'characters'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'bg-neutral-800/50 hover:bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="text-lg">👽</span>
              <span className="font-medium text-sm">Characters</span>
            </div>
          </button>

          <button
            onClick={() => {
              onViewChange('episodes')
              onItemSelect(null)
            }}
            className={`w-full text-left px-3 py-2.5 rounded-lg transition-all ${
              selectedView === 'episodes'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/20'
                : 'bg-neutral-800/50 hover:bg-neutral-800 text-neutral-300 hover:text-white'
            }`}
          >
            <div className="flex items-center gap-2.5">
              <span className="text-lg">🎬</span>
              <span className="font-medium text-sm">Episodes</span>
            </div>
          </button>
        </nav>
      </div>
    </div>
  )
}

