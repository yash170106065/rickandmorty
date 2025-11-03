'use client'

import { useState, useEffect } from 'react'
import { api, GeneratedContent, Location, Character, Episode } from '@/lib/api'
import LocationCard from './LocationCard'
import CompactCharacterCard from './CompactCharacterCard'
import CharacterGridCard from './CharacterGridCard'
import EpisodeCard from './EpisodeCard'
import Pagination from './Pagination'
import NotesPanel from './NotesPanel'

type EntityItem = Location | Character | Episode

// Type guard functions
function isLocation(item: EntityItem | null): item is Location {
  return item !== null && 'dimension' in item
}

function isEpisode(item: EntityItem | null): item is Episode {
  return item !== null && 'episode' in item && !('dimension' in item)
}

function isCharacter(item: EntityItem | null): item is Character {
  // Character has species, no dimension, and episode is an array (string[]) not a string
  if (!item || 'dimension' in item) return false
  // Episode has episode as string, Character has episode as string[]
  // Use type assertion to check the episode property safely
  const itemAny = item as any
  if ('episode' in itemAny) {
    // Episode has episode: string, Character has episode: string[]
    return Array.isArray(itemAny.episode) && 'species' in itemAny
  }
  // If no episode property, check for species (character)
  return 'species' in itemAny
}

// Helper to safely check if selected item matches an item ID
function matchesItemId(selectedItem: EntityItem | null, itemId: number, type: 'location' | 'episode' | 'character'): boolean {
  if (!selectedItem) return false
  if (type === 'location' && isLocation(selectedItem)) return selectedItem.id === itemId
  if (type === 'episode' && isEpisode(selectedItem)) return selectedItem.id === itemId
  if (type === 'character' && isCharacter(selectedItem)) return selectedItem.id === itemId
  return false
}

interface DashboardContentProps {
  selectedView: 'locations' | 'characters' | 'episodes' | null
  selectedItem: EntityItem | null
  onItemSelect: (item: EntityItem | null) => void
  rightSidebarWidth: number
  onRightSidebarWidthChange: (width: number) => void
  onNavigateToItem?: (view: string, itemId: number) => void
}

const ITEMS_PER_PAGE = 20
const DEFAULT_RIGHT_SIDEBAR_WIDTH = 280

export default function DashboardContent({
  selectedView,
  selectedItem,
  onItemSelect,
  rightSidebarWidth,
  onRightSidebarWidthChange,
  onNavigateToItem,
}: DashboardContentProps) {
  const [locations, setLocations] = useState<Location[]>([])
  const [characters, setCharacters] = useState<Character[]>([])
  const [episodes, setEpisodes] = useState<Episode[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1)
  const [totalItems, setTotalItems] = useState(0)
  const [notesPanelWidth, setNotesPanelWidth] = useState<number>(400) // Always visible, resizable width
  
  // AI Summary state
  const [summary, setSummary] = useState<GeneratedContent | null>(null)
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false)
  const [isFlipped, setIsFlipped] = useState(false)

  // Reset page when view changes
  useEffect(() => {
    setCurrentPage(1)
  }, [selectedView])
  
  // Reset summary when item changes
  useEffect(() => {
    setSummary(null)
    setIsFlipped(false)
  }, [selectedItem?.id, selectedView])
  
  const handleGenerateSummary = async (type: 'location' | 'character' | 'episode', id: number) => {
    if (isFlipped) {
      // If already flipped, flip back to details
      setIsFlipped(false)
      return
    }
    
    // If summary already exists, just flip
    if (summary && summary.subject_id === id) {
      setIsFlipped(true)
      return
    }
    
    // Generate new summary - flip immediately to show loading state
    setIsGeneratingSummary(true)
    setIsFlipped(true)
    setSummary(null)
    
    try {
      let generatedSummary: GeneratedContent
      if (type === 'location') {
        generatedSummary = await api.generation.generateLocationSummary(id)
      } else if (type === 'episode') {
        generatedSummary = await api.generation.generateEpisodeSummary(id)
      } else if (type === 'character') {
        generatedSummary = await api.generation.generateCharacterSummary(id)
      } else {
        throw new Error('Unknown summary type')
      }
      setSummary(generatedSummary)
    } catch (err) {
      console.error('Failed to generate summary:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate summary. Please try again.'
      setError(errorMessage)
      // Flip back to details on error
      setIsFlipped(false)
    } finally {
      setIsGeneratingSummary(false)
    }
  }

  useEffect(() => {
    if (!selectedView) return
    // Don't fetch list data when an item is selected - we're showing detail view
    if (selectedItem) return

    const fetchData = async () => {
      setLoading(true)
      setError(null)
      try {
        if (selectedView === 'locations') {
          // For now, we'll fetch all and paginate client-side
          // In a production app, you'd want server-side pagination with total count
          const data = await api.locations.getPaginated(currentPage, ITEMS_PER_PAGE)
          setLocations(data)
          // Since we don't have total from API yet, estimate based on returned data
          // In production, API should return total count
          setTotalItems(data.length === ITEMS_PER_PAGE ? currentPage * ITEMS_PER_PAGE + 1 : (currentPage - 1) * ITEMS_PER_PAGE + data.length)
        } else if (selectedView === 'episodes') {
          const data = await api.episodes.getPaginated(currentPage, ITEMS_PER_PAGE)
          setEpisodes(data)
          setTotalItems(data.length === ITEMS_PER_PAGE ? currentPage * ITEMS_PER_PAGE + 1 : (currentPage - 1) * ITEMS_PER_PAGE + data.length)
        } else if (selectedView === 'characters') {
          const data = await api.characters.getPaginated(currentPage, ITEMS_PER_PAGE)
          setCharacters(data)
          setTotalItems(data.length === ITEMS_PER_PAGE ? currentPage * ITEMS_PER_PAGE + 1 : (currentPage - 1) * ITEMS_PER_PAGE + data.length)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedView, currentPage, selectedItem])

  // Reset notes panel width when item selection changes
  useEffect(() => {
    if (selectedItem && notesPanelWidth === 0) {
      // Reset to default width if somehow it got to 0
      setNotesPanelWidth(400)
    }
  }, [selectedItem, notesPanelWidth])

  const handleItemClick = (item: EntityItem) => {
    if (!item || !item.id) {
      console.error('Invalid item clicked:', item)
      return
    }
    
    // Navigate to URL directly - this will trigger the API call via URL loading
    if (onNavigateToItem && selectedView) {
      onNavigateToItem(selectedView, item.id)
    } else {
      console.error('onNavigateToItem not available or selectedView is null', { onNavigateToItem, selectedView })
    }
  }

  if (!selectedView) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-6">🌌</div>
          <h2 className="text-3xl font-bold gradient-text mb-4">Welcome to Dashboard</h2>
          <p className="text-neutral-400 text-xl">
            Select a category from the sidebar to begin exploring
          </p>
        </div>
      </div>
    )
  }

  // Don't show loading spinner when showing detail view - it's already loaded
  if (loading && !selectedItem) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-6 animate-spin">⚡</div>
          <p className="text-neutral-400 text-xl">Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 text-xl">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full p-8">
      {selectedView === 'locations' && (
        <div className="h-full flex flex-col">
          {!selectedItem && <h2 className="text-4xl font-bold mb-8 gradient-text">Locations</h2>}
          {selectedItem ? (
            <div className="flex-1 flex gap-0 overflow-hidden">
              {/* Details Panel (Left) */}
              <div className="flex-1 overflow-y-auto pr-4">
                <div className="flex items-center justify-between gap-4 mb-4">
                  <button
                    onClick={() => {
                      onItemSelect(null)
                      onRightSidebarWidthChange(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors px-3 py-1.5 bg-neutral-800 rounded-lg text-sm"
                  >
                    ← Back
                  </button>
                  <button
                    onClick={() => handleGenerateSummary('location', selectedItem.id)}
                    title="Generate an AI-powered summary of this location in the tone of a Rick & Morty narrator, including interesting details about residents and the dimension. The summary will be evaluated for factuality, completeness, and creativity."
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isGeneratingSummary}
                  >
                    {isFlipped ? (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        View Details
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        {isGeneratingSummary ? 'Generating...' : 'View Summary with AI'}
                      </>
                    )}
                  </button>
                </div>
                
                {/* Flip Card Container */}
                <div style={{ perspective: '1000px', minHeight: '600px' }}>
                  <div
                    style={{
                      position: 'relative',
                      width: '100%',
                      height: '100%',
                      transformStyle: 'preserve-3d',
                      transition: 'transform 0.5s',
                      transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                    }}
                  >
                    {/* Front: Location Details */}
                    <div
                      style={{
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-4 border border-neutral-800 h-full flex flex-col overflow-hidden" style={{ minHeight: '600px' }}>
                        <div className="mb-4 flex-shrink-0">
                          <h3 className="text-xl font-bold gradient-text">{selectedItem.name}</h3>
                        </div>
                        <div className="flex-1 overflow-y-auto">
                          <div className="space-y-3">
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Type</span>
                              <p className="text-white font-medium text-sm">{isLocation(selectedItem) ? selectedItem.type || 'Unknown' : 'Unknown'}</p>
                            </div>
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Dimension</span>
                              <p className="text-white font-medium text-sm">{isLocation(selectedItem) ? selectedItem.dimension || 'Unknown' : 'Unknown'}</p>
                            </div>
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Residents</span>
                              <p className="text-blue-400 font-medium text-sm">
                                {isLocation(selectedItem) 
                                  ? (selectedItem.residents?.length || selectedItem.resident_count || 0)
                                  : 0}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Back: AI Summary */}
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        transform: 'rotateY(180deg)',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-6 border border-neutral-800 h-full flex flex-col" style={{ minHeight: '600px' }}>
                        <div className="mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">🤖</span>
                            <h3 className="text-xl font-bold gradient-text">AI Summary</h3>
                          </div>
                          <p className="text-neutral-400 text-sm">Summarize this location in the tone of a Rick & Morty narrator</p>
                        </div>
                        {isGeneratingSummary ? (
                          <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                              <div className="animate-spin text-4xl mb-4">⚡</div>
                              <p className="text-neutral-400">Generating AI summary...</p>
                            </div>
                          </div>
                        ) : summary ? (
                          <div className="flex-1 overflow-y-auto">
                            <p className="text-white text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                              {summary.output_text}
                            </p>
                            {/* Evaluation Scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-neutral-800">
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Factual</p>
                                {summary.factual_score >= 0 ? (
                                  <p className="text-xl font-bold text-blue-400">
                                    {(summary.factual_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Complete</p>
                                {summary.completeness_score >= 0 ? (
                                  <p className="text-xl font-bold text-purple-400">
                                    {(summary.completeness_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Creative</p>
                                {summary.creativity_score >= 0 ? (
                                  <p className="text-xl font-bold text-pink-400">
                                    {(summary.creativity_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Relevant</p>
                                {summary.relevance_score >= 0 ? (
                                  <p className="text-xl font-bold text-green-400">
                                    {(summary.relevance_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex-1 flex items-center justify-center">
                            <p className="text-neutral-400 text-sm text-center">
                              Click "View Summary with AI" to generate
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Notes Panel (Right) - Always visible */}
              <div className="relative border-l border-neutral-800" style={{ width: `${notesPanelWidth}px` }}>
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
                  onMouseDown={(e) => {
                    e.preventDefault()
                    const startX = e.clientX
                    const startWidth = notesPanelWidth

                    const onMouseMove = (e: MouseEvent) => {
                      const diff = e.clientX - startX
                      const newWidth = Math.max(300, Math.min(800, startWidth + diff))
                      setNotesPanelWidth(newWidth)
                    }

                    const onMouseUp = () => {
                      document.removeEventListener('mousemove', onMouseMove)
                      document.removeEventListener('mouseup', onMouseUp)
                    }

                    document.addEventListener('mousemove', onMouseMove)
                    document.addEventListener('mouseup', onMouseUp)
                  }}
                />
                <NotesPanel
                  subjectType="location"
                  subjectId={selectedItem.id}
                  subjectName={selectedItem.name}
                />
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {locations.map((location) => (
                  <LocationCard
                    key={location.id}
                    location={location}
                    onClick={(e?: React.MouseEvent) => {
                      e?.stopPropagation?.()
                      handleItemClick(location)
                    }}
                    isSelected={matchesItemId(selectedItem, location.id, 'location')}
                  />
                ))}
              </div>
              <Pagination
                currentPage={currentPage}
                totalPages={Math.ceil(totalItems / ITEMS_PER_PAGE)}
                onPageChange={setCurrentPage}
                itemsPerPage={ITEMS_PER_PAGE}
                totalItems={totalItems}
              />
            </>
          )}
        </div>
      )}

      {selectedView === 'episodes' && (
        <div className="h-full flex flex-col">
          {!selectedItem && <h2 className="text-4xl font-bold mb-8 gradient-text">Episodes</h2>}
          {selectedItem ? (
            <div className="flex-1 flex gap-0 overflow-hidden">
              {/* Details Panel (Left) */}
              <div className="flex-1 overflow-y-auto pr-4">
                <div className="flex items-center justify-between gap-4 mb-4">
                  <button
                    onClick={() => {
                      onItemSelect(null)
                      onRightSidebarWidthChange(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors px-3 py-1.5 bg-neutral-800 rounded-lg text-sm"
                  >
                    ← Back
                  </button>
                  <button
                    onClick={() => handleGenerateSummary('episode', selectedItem.id)}
                    title="Generate an AI-powered summary of this episode in the tone of a Rick & Morty narrator, capturing the key events, character interactions, and themes. The summary will be evaluated for factuality, completeness, and creativity."
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isGeneratingSummary}
                  >
                    {isFlipped ? (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        View Details
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        {isGeneratingSummary ? 'Generating...' : 'View Summary with AI'}
                      </>
                    )}
                  </button>
                </div>
                
                {/* Flip Card Container */}
                <div style={{ perspective: '1000px', minHeight: '600px' }}>
                  <div
                    style={{
                      position: 'relative',
                      width: '100%',
                      height: '100%',
                      transformStyle: 'preserve-3d',
                      transition: 'transform 0.5s',
                      transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                    }}
                  >
                    {/* Front: Episode Details */}
                    <div
                      style={{
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-4 border border-neutral-800 h-full flex flex-col overflow-hidden" style={{ minHeight: '600px' }}>
                        <div className="mb-4 flex-shrink-0">
                          <h3 className="text-xl font-bold gradient-text">{selectedItem.name}</h3>
                        </div>
                        <div className="flex-1 overflow-y-auto">
                          <div className="space-y-3">
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Episode</span>
                              <p className="text-white font-medium text-sm">{isEpisode(selectedItem) ? selectedItem.episode || 'Unknown' : 'Unknown'}</p>
                            </div>
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Air Date</span>
                              <p className="text-white font-medium text-sm">{isEpisode(selectedItem) ? selectedItem.air_date || 'Unknown' : 'Unknown'}</p>
                            </div>
                            <div>
                              <span className="text-neutral-500 text-xs block mb-1">Characters</span>
                              <p className="text-purple-400 font-medium text-sm">
                                {isEpisode(selectedItem) 
                                  ? (selectedItem.characters?.length || selectedItem.character_count || 0)
                                  : 0}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Back: AI Summary */}
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        transform: 'rotateY(180deg)',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-6 border border-neutral-800 h-full flex flex-col" style={{ minHeight: '600px' }}>
                        <div className="mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">🤖</span>
                            <h3 className="text-xl font-bold gradient-text">AI Summary</h3>
                          </div>
                          <p className="text-neutral-400 text-sm">Summarize this episode in the tone of a Rick & Morty narrator</p>
                        </div>
                        {isGeneratingSummary ? (
                          <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                              <div className="animate-spin text-4xl mb-4">⚡</div>
                              <p className="text-neutral-400">Generating AI summary...</p>
                            </div>
                          </div>
                        ) : summary ? (
                          <div className="flex-1 overflow-y-auto">
                            <p className="text-white text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                              {summary.output_text}
                            </p>
                            {/* Evaluation Scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-neutral-800">
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Factual</p>
                                {summary.factual_score >= 0 ? (
                                  <p className="text-xl font-bold text-blue-400">
                                    {(summary.factual_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Complete</p>
                                {summary.completeness_score >= 0 ? (
                                  <p className="text-xl font-bold text-purple-400">
                                    {(summary.completeness_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Creative</p>
                                {summary.creativity_score >= 0 ? (
                                  <p className="text-xl font-bold text-pink-400">
                                    {(summary.creativity_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Relevant</p>
                                {summary.relevance_score >= 0 ? (
                                  <p className="text-xl font-bold text-green-400">
                                    {(summary.relevance_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex-1 flex items-center justify-center">
                            <p className="text-neutral-400 text-sm text-center">
                              Click "View Summary with AI" to generate
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Notes Panel (Right) - Always visible */}
              <div className="relative border-l border-neutral-800" style={{ width: `${notesPanelWidth}px` }}>
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
                  onMouseDown={(e) => {
                    e.preventDefault()
                    const startX = e.clientX
                    const startWidth = notesPanelWidth

                    const onMouseMove = (e: MouseEvent) => {
                      const diff = e.clientX - startX
                      const newWidth = Math.max(300, Math.min(800, startWidth + diff))
                      setNotesPanelWidth(newWidth)
                    }

                    const onMouseUp = () => {
                      document.removeEventListener('mousemove', onMouseMove)
                      document.removeEventListener('mouseup', onMouseUp)
                    }

                    document.addEventListener('mousemove', onMouseMove)
                    document.addEventListener('mouseup', onMouseUp)
                  }}
                />
                <NotesPanel
                  subjectType="episode"
                  subjectId={selectedItem.id}
                  subjectName={selectedItem.name}
                />
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {episodes.map((episode) => (
                  <EpisodeCard
                    key={episode.id}
                    episode={episode}
                    onClick={(e?: React.MouseEvent) => {
                      e?.stopPropagation?.()
                      handleItemClick(episode)
                    }}
                    isSelected={matchesItemId(selectedItem, episode.id, 'episode')}
                  />
                ))}
              </div>
              <Pagination
                currentPage={currentPage}
                totalPages={Math.ceil(totalItems / ITEMS_PER_PAGE)}
                onPageChange={setCurrentPage}
                itemsPerPage={ITEMS_PER_PAGE}
                totalItems={totalItems}
              />
            </>
          )}
        </div>
      )}

      {selectedView === 'characters' && (
        <div className="h-full flex flex-col">
          {!selectedItem && <h2 className="text-4xl font-bold mb-8 gradient-text">Characters</h2>}
          {selectedItem ? (
            <div className="flex-1 flex gap-0 overflow-hidden">
              {/* Details Panel (Left) */}
              <div className="flex-1 overflow-y-auto pr-4">
                <div className="flex items-center justify-between gap-4 mb-4">
                  <button
                    onClick={() => {
                      onItemSelect(null)
                      onRightSidebarWidthChange(0)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors px-3 py-1.5 bg-neutral-800 rounded-lg text-sm"
                  >
                    ← Back
                  </button>
                  <button
                    onClick={() => handleGenerateSummary('character', selectedItem.id)}
                    title="Generate an AI-powered summary of this character in the tone of a Rick & Morty narrator, including personality traits, memorable moments, and their role in the multiverse. The summary will be evaluated for factuality, completeness, and creativity."
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-4 py-1.5 rounded-lg text-sm font-semibold transition-all shadow-lg flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    disabled={isGeneratingSummary}
                  >
                    {isFlipped ? (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        View Details
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                        {isGeneratingSummary ? 'Generating...' : 'View Summary with AI'}
                      </>
                    )}
                  </button>
                </div>
                
                {/* Flip Card Container */}
                <div style={{ perspective: '1000px', minHeight: '600px' }}>
                  <div
                    style={{
                      position: 'relative',
                      width: '100%',
                      height: '100%',
                      transformStyle: 'preserve-3d',
                      transition: 'transform 0.5s',
                      transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)',
                    }}
                  >
                    {/* Front: Character Details */}
                    <div
                      style={{
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div style={{ minHeight: '600px', height: '100%' }}>
                        {selectedView === 'characters' && selectedItem ? (
                          <CompactCharacterCard character={selectedItem as Character} />
                        ) : null}
                      </div>
                    </div>
                    
                    {/* Back: AI Summary */}
                    <div
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backfaceVisibility: 'hidden',
                        WebkitBackfaceVisibility: 'hidden',
                        transform: 'rotateY(180deg)',
                        width: '100%',
                        height: '100%',
                        minHeight: '600px',
                      }}
                    >
                      <div className="bg-gradient-to-br from-neutral-900 to-black rounded-xl p-6 border border-neutral-800 h-full flex flex-col" style={{ minHeight: '600px' }}>
                        <div className="mb-4">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-2xl">🤖</span>
                            <h3 className="text-xl font-bold gradient-text">AI Summary</h3>
                          </div>
                          <p className="text-neutral-400 text-sm">Summarize this character in the tone of a Rick & Morty narrator</p>
                        </div>
                        {isGeneratingSummary ? (
                          <div className="flex-1 flex items-center justify-center">
                            <div className="text-center">
                              <div className="animate-spin text-4xl mb-4">⚡</div>
                              <p className="text-neutral-400">Generating AI summary...</p>
                            </div>
                          </div>
                        ) : summary ? (
                          <div className="flex-1 overflow-y-auto">
                            <p className="text-white text-sm leading-relaxed mb-6 whitespace-pre-wrap">
                              {summary.output_text}
                            </p>
                            {/* Evaluation Scores */}
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 border-t border-neutral-800">
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Factual</p>
                                {summary.factual_score >= 0 ? (
                                  <p className="text-xl font-bold text-blue-400">
                                    {(summary.factual_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Complete</p>
                                {summary.completeness_score >= 0 ? (
                                  <p className="text-xl font-bold text-purple-400">
                                    {(summary.completeness_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Creative</p>
                                {summary.creativity_score >= 0 ? (
                                  <p className="text-xl font-bold text-pink-400">
                                    {(summary.creativity_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                              <div className="text-center bg-neutral-800/30 rounded-lg p-3">
                                <p className="text-xs text-neutral-400 mb-1.5 font-medium">Relevant</p>
                                {summary.relevance_score >= 0 ? (
                                  <p className="text-xl font-bold text-green-400">
                                    {(summary.relevance_score * 100).toFixed(0)}%
                                  </p>
                                ) : (
                                  <p className="text-lg font-bold text-neutral-500">
                                    <span className="inline-block animate-pulse">⏳</span>
                                  </p>
                                )}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex-1 flex items-center justify-center">
                            <p className="text-neutral-400 text-sm text-center">
                              Click "View Summary with AI" to generate
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Notes Panel (Right) - Always visible */}
              <div className="relative border-l border-neutral-800" style={{ width: `${notesPanelWidth}px` }}>
                <div
                  className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-blue-500 transition-colors z-10"
                  onMouseDown={(e) => {
                    e.preventDefault()
                    const startX = e.clientX
                    const startWidth = notesPanelWidth

                    const onMouseMove = (e: MouseEvent) => {
                      const diff = e.clientX - startX
                      const newWidth = Math.max(300, Math.min(800, startWidth + diff))
                      setNotesPanelWidth(newWidth)
                    }

                    const onMouseUp = () => {
                      document.removeEventListener('mousemove', onMouseMove)
                      document.removeEventListener('mouseup', onMouseUp)
                    }

                    document.addEventListener('mousemove', onMouseMove)
                    document.addEventListener('mouseup', onMouseUp)
                  }}
                />
                <NotesPanel
                  subjectType="character"
                  subjectId={selectedItem?.id || 0}
                  subjectName={selectedItem?.name || ''}
                />
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {characters.map((character) => (
                  <CharacterGridCard
                    key={character.id}
                    character={character}
                    onClick={(e?: React.MouseEvent) => {
                      e?.stopPropagation?.()
                      handleItemClick(character)
                    }}
                    isSelected={matchesItemId(selectedItem, character.id, 'character')}
                  />
                ))}
              </div>
              <Pagination
                currentPage={currentPage}
                totalPages={Math.ceil(totalItems / ITEMS_PER_PAGE)}
                onPageChange={setCurrentPage}
                itemsPerPage={ITEMS_PER_PAGE}
                totalItems={totalItems}
              />
            </>
          )}
        </div>
      )}
    </div>
  )
}

