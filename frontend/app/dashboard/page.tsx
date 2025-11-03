'use client'

import React, { useState, useEffect } from 'react'
import { useRouter, usePathname, useSearchParams } from 'next/navigation'
import { api, Location, Character, Episode, Resident } from '@/lib/api'
import DashboardSidebar from '@/components/dashboard/DashboardSidebar'
import DashboardContent from '@/components/dashboard/DashboardContent'

type ViewType = 'locations' | 'characters' | 'episodes' | null
type EntityItem = Location | Character | Episode

interface DashboardPageProps {
  initialView?: ViewType
}

export default function DashboardPage({ initialView }: DashboardPageProps = {}) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()
  
  const [sidebarWidth, setSidebarWidth] = useState<number>(240)
  const [rightSidebarWidth, setRightSidebarWidth] = useState<number>(0)
  const DEFAULT_RIGHT_SIDEBAR_WIDTH = 280
  const [selectedView, setSelectedView] = useState<ViewType>(initialView || null)
  const [selectedItem, setSelectedItem] = useState<EntityItem | null>(null)
  const [isLoadingItem, setIsLoadingItem] = useState<boolean>(false)

  // Initialize view from URL path - this must happen FIRST
  useEffect(() => {
    if (initialView) {
      setSelectedView(initialView)
      return
    }
    
    if (pathname) {
      if (pathname.includes('/locations')) {
        setSelectedView('locations')
      } else if (pathname.includes('/characters')) {
        setSelectedView('characters')
      } else if (pathname.includes('/episodes')) {
        setSelectedView('episodes')
      } else if (pathname === '/dashboard') {
        setSelectedView(null)
      }
    }
  }, [pathname, initialView])

  // Load item from URL on mount or when query params change
  useEffect(() => {
    if (!selectedView) return // Wait for view to be set
    
    const locationId = searchParams.get('locationId')
    const characterId = searchParams.get('characterId')
    const episodeId = searchParams.get('episodeId')

    const loadItemFromUrl = async () => {
      try {
        // Check if we already have this item loaded
        const currentId = selectedView === 'locations' ? locationId :
                         selectedView === 'characters' ? characterId :
                         selectedView === 'episodes' ? episodeId : null
        
        // Skip if we already have the correct item loaded
        if (selectedItem?.id && currentId && selectedItem.id.toString() === currentId) {
          return
        }
        
        if (locationId && selectedView === 'locations') {
          // Show loading, then fetch location with residents in parallel
          setIsLoadingItem(true)
          setSelectedItem(null) // Clear previous item immediately
          
          const location = await api.locations.getById(parseInt(locationId))
          
          // Location already includes residents from the API
          setSelectedItem(location)
          setIsLoadingItem(false)
          // Sidebar width will be set by the useEffect based on residents availability
        } else if (characterId && selectedView === 'characters') {
          // Show loading, then fetch character with episodes (single API call like locations/episodes)
          setIsLoadingItem(true)
          setSelectedItem(null) // Clear previous item immediately
          
          try {
            // Single API call - character endpoint now includes episodes
            const character = await api.characters.getById(parseInt(characterId))
            
            // Character response now includes episodes array
            setSelectedItem(character)
            setIsLoadingItem(false)
            // Sidebar width will be set by the useEffect based on episodes availability
          } catch (charErr) {
            setIsLoadingItem(false)
            throw charErr
          }
        } else if (episodeId && selectedView === 'episodes') {
          // Show loading, then fetch episode with characters in parallel
          setIsLoadingItem(true)
          setSelectedItem(null) // Clear previous item immediately
          
          const episode = await api.episodes.getById(parseInt(episodeId))
          
          // Episode already includes characters from the API
          setSelectedItem(episode)
          setIsLoadingItem(false)
          // Sidebar width will be set by the useEffect based on characters availability
        } else if (!locationId && !characterId && !episodeId) {
          // Clear selection if no ID in URL
          setSelectedItem(null)
          setRightSidebarWidth(0)
          setIsLoadingItem(false)
        }
      } catch (err) {
        setIsLoadingItem(false)
        console.error('Failed to load item from URL:', err)
        alert(`Failed to load item: ${err instanceof Error ? err.message : 'Unknown error'}`)
      }
    }

    if (selectedView) {
      loadItemFromUrl()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, selectedView, pathname])

  // Auto-open/close sidebar based on nested data availability
  useEffect(() => {
    if (!selectedItem) {
      setRightSidebarWidth(0)
      return
    }
    
    if (selectedView === 'locations' && selectedItem.residents && selectedItem.residents.length > 0) {
      setRightSidebarWidth(DEFAULT_RIGHT_SIDEBAR_WIDTH)
    } else if (selectedView === 'characters') {
      // Open sidebar if character has episodes
      if (selectedItem.episodes && selectedItem.episodes.length > 0) {
        setRightSidebarWidth(DEFAULT_RIGHT_SIDEBAR_WIDTH)
      } else if (selectedItem.episode && selectedItem.episode.length > 0) {
        // Even if episodes array is empty but episode references exist, open sidebar
        setRightSidebarWidth(DEFAULT_RIGHT_SIDEBAR_WIDTH)
      } else {
        setRightSidebarWidth(0)
      }
    } else if (selectedView === 'episodes' && selectedItem.characters && selectedItem.characters.length > 0) {
      setRightSidebarWidth(DEFAULT_RIGHT_SIDEBAR_WIDTH)
    } else {
      setRightSidebarWidth(0)
    }
  }, [selectedView, selectedItem])

  return (
    <div className="h-[calc(100vh-73px)] flex bg-black overflow-hidden">
      <DashboardSidebar
        width={sidebarWidth}
        onWidthChange={setSidebarWidth}
        selectedView={selectedView}
        onViewChange={(view) => {
          setSelectedView(view)
          setSelectedItem(null)
          // Navigate to appropriate route
          if (view === 'locations') {
            router.push('/dashboard/locations')
          } else if (view === 'characters') {
            router.push('/dashboard/characters')
          } else if (view === 'episodes') {
            router.push('/dashboard/episodes')
          } else {
            router.push('/dashboard')
          }
        }}
        onItemSelect={setSelectedItem}
      />

      <div 
        className="flex-1 overflow-y-auto"
        style={{ width: `calc(100% - ${sidebarWidth}px - ${rightSidebarWidth}px)` }}
      >
        {isLoadingItem ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-6 animate-spin">⚡</div>
              <p className="text-neutral-400 text-xl">Loading...</p>
            </div>
          </div>
        ) : (
          <DashboardContent
            selectedView={selectedView}
            selectedItem={selectedItem}
            onItemSelect={setSelectedItem}
            rightSidebarWidth={rightSidebarWidth}
            onRightSidebarWidthChange={setRightSidebarWidth}
            onNavigateToItem={(view, itemId) => {
              if (view === 'locations') {
                router.push(`/dashboard/locations?locationId=${itemId}`)
              } else if (view === 'characters') {
                router.push(`/dashboard/characters?characterId=${itemId}`)
              } else if (view === 'episodes') {
                router.push(`/dashboard/episodes?episodeId=${itemId}`)
              }
            }}
          />
        )}
      </div>

      {selectedItem && rightSidebarWidth > 0 && (
        <div className="relative border-l border-neutral-800 bg-gradient-to-b from-neutral-900 to-black overflow-y-auto" style={{ width: `${rightSidebarWidth}px` }}>
          <div
            className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
            onMouseDown={(e) => {
              e.preventDefault()
              const startX = e.clientX
              const startWidth = rightSidebarWidth

              const onMouseMove = (e: MouseEvent) => {
                const diff = startX - e.clientX
                const newWidth = Math.max(220, Math.min(500, startWidth + diff))
                setRightSidebarWidth(newWidth)
              }

              const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove)
                document.removeEventListener('mouseup', onMouseUp)
              }

              document.addEventListener('mousemove', onMouseMove)
              document.addEventListener('mouseup', onMouseUp)
            }}
          />

          <div className="p-6">
            {selectedView === 'locations' && selectedItem?.residents && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-3xl font-bold gradient-text">Residents</h2>
                  <button
                    onClick={() => {
                      setRightSidebarWidth(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors text-2xl"
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-4">
                  {selectedItem.residents.map((resident: Resident) => (
                    <div
                      key={resident.id}
                      onClick={async () => {
                        // Navigate to characters tab with character ID
                        router.push(`/dashboard/characters?characterId=${resident.id}`)
                      }}
                      className="bg-neutral-800/50 hover:bg-neutral-700/50 rounded-xl p-4 border border-neutral-700 cursor-pointer transition-all hover:scale-[1.02] hover:border-blue-500/50"
                    >
                      <div className="flex items-center gap-4">
                        <img
                          src={resident.image}
                          alt={resident.name}
                          className="w-16 h-16 rounded-lg object-cover border-2 border-neutral-600"
                        />
                        <div className="flex-1">
                          <h3 className="font-bold text-lg text-white">{resident.name}</h3>
                          <p className="text-sm text-neutral-400">{resident.species}</p>
                          <p className="text-xs text-neutral-500 mt-1">{resident.status}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedView === 'episodes' && selectedItem?.characters && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-3xl font-bold gradient-text">Characters</h2>
                  <button
                    onClick={() => {
                      setRightSidebarWidth(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors text-2xl"
                  >
                    ✕
                  </button>
                </div>
                <div className="space-y-4">
                  {selectedItem.characters.map((character: Character) => (
                      <div
                        key={character.id}
                        onClick={async () => {
                          // Navigate to characters tab with character ID
                          router.push(`/dashboard/characters?characterId=${character.id}`)
                        }}
                        className="bg-neutral-800/50 hover:bg-neutral-700/50 rounded-xl p-4 border border-neutral-700 cursor-pointer transition-all hover:scale-[1.02] hover:border-purple-500/50"
                      >
                        <div className="flex items-center gap-4">
                          <img
                            src={character.image}
                            alt={character.name}
                            className="w-16 h-16 rounded-lg object-cover border-2 border-neutral-600"
                          />
                          <div className="flex-1">
                            <h3 className="font-bold text-lg text-white">{character.name}</h3>
                            <p className="text-sm text-neutral-400">{character.species}</p>
                            <p className="text-xs text-neutral-500 mt-1">{character.status}</p>
                          </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Only show episodes sidebar when on characters view and character has episodes */}
            {selectedView === 'characters' && selectedItem && (selectedItem.episodes?.length > 0 || (selectedItem.episode && selectedItem.episode.length > 0)) && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-3xl font-bold gradient-text">Episodes</h2>
                  <button
                    onClick={() => {
                      setRightSidebarWidth(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors text-2xl"
                  >
                    ✕
                  </button>
                </div>
                {selectedItem.episodes && selectedItem.episodes.length > 0 ? (
                  <div className="space-y-4">
                    {selectedItem.episodes.map((episode: any) => (
                      <div
                        key={episode.id}
                        onClick={async () => {
                          // Navigate to episodes tab with episode ID
                          router.push(`/dashboard/episodes?episodeId=${episode.id}`)
                        }}
                        className="bg-neutral-800/50 hover:bg-neutral-700/50 rounded-xl p-4 border border-neutral-700 cursor-pointer transition-all hover:scale-[1.02] hover:border-green-500/50"
                      >
                        <div className="flex items-center gap-4">
                          <div className="w-16 h-16 rounded-lg bg-green-500/20 flex items-center justify-center border-2 border-green-500/30">
                            <span className="text-2xl">🎬</span>
                          </div>
                          <div className="flex-1">
                            <h3 className="font-bold text-lg text-white">{episode.name}</h3>
                            <p className="text-sm text-neutral-400">{episode.episode}</p>
                            <p className="text-xs text-neutral-500 mt-1">{episode.air_date}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <div className="text-4xl mb-4 animate-spin">⚡</div>
                      <p className="text-neutral-400">Loading episodes...</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
