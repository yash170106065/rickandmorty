'use client'

import Link from 'next/link'
import { useRouter, usePathname } from 'next/navigation'
import { useState, useEffect, useRef } from 'react'
import { api, UnifiedSearchResult } from '@/lib/api'

export default function Navbar() {
  const router = useRouter()
  const pathname = usePathname()
  const [searchQuery, setSearchQuery] = useState('')
  const [results, setResults] = useState<UnifiedSearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const searchRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  
  const isHomepage = pathname === '/'

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  // Search when query has at least 3 characters
  useEffect(() => {
    const search = async () => {
      if (searchQuery.trim().length < 3) {
        setResults([])
        setShowDropdown(false)
        return
      }

      setIsLoading(true)
      try {
        const searchResults = await api.search.search(searchQuery.trim(), 10)
        setResults(searchResults)
        setShowDropdown(true)
      } catch (err) {
        console.error('Search error:', err)
        setResults([])
        setShowDropdown(false)
      } finally {
        setIsLoading(false)
      }
    }

    // Debounce search
    const timeoutId = setTimeout(search, 300)
    return () => clearTimeout(timeoutId)
  }, [searchQuery])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  const handleInputFocus = () => {
    if (results.length > 0) {
      setShowDropdown(true)
    }
  }

  const handleResultClick = (result: UnifiedSearchResult) => {
    // Navigate to respective entity
    if (result.entity_type === 'character') {
      router.push(`/dashboard/characters?characterId=${result.entity_id}`)
    } else if (result.entity_type === 'location') {
      router.push(`/dashboard/locations?locationId=${result.entity_id}`)
    } else if (result.entity_type === 'episode') {
      router.push(`/dashboard/episodes?episodeId=${result.entity_id}`)
    }
    
    setSearchQuery('')
    setResults([])
    setShowDropdown(false)
    inputRef.current?.blur()
  }

  const getTypeBadgeColor = (entityType: string) => {
    if (entityType === 'character') {
      return 'bg-blue-600/20 text-blue-400 border-blue-600/50'
    } else if (entityType === 'location') {
      return 'bg-purple-600/20 text-purple-400 border-purple-600/50'
    } else if (entityType === 'episode') {
      return 'bg-pink-600/20 text-pink-400 border-pink-600/50'
    }
    return 'bg-neutral-700 text-neutral-400 border-neutral-600'
  }

  return (
    <nav className="w-full border-b border-neutral-800 bg-black/50 backdrop-blur-sm z-50 sticky top-0">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-6">
        {/* Left: Logo */}
        <Link 
          href="/" 
          className="text-xl font-bold gradient-text hover:opacity-80 transition-opacity flex-shrink-0"
        >
          ⚡ Rick & Morty AI
        </Link>
        
        {/* Middle: Search Bar - Visible on all pages except homepage */}
        {!isHomepage && (
          <div className="flex-1 max-w-2xl mx-auto relative" ref={searchRef}>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400 text-lg pointer-events-none z-10">
                ✨
              </div>
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={handleInputChange}
                onFocus={handleInputFocus}
                placeholder="Semantic search from its notes & summaries... (min 3 chars)"
                className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-2 pl-10 pr-14 text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
              <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
                {searchQuery && (
                  <button
                    onClick={() => {
                      setSearchQuery('')
                      setResults([])
                      setShowDropdown(false)
                    }}
                    className="text-neutral-400 hover:text-white transition-colors p-1"
                    title="Clear search"
                  >
                    ✕
                  </button>
                )}
                <div className="text-neutral-400 pointer-events-none">
                  {isLoading ? (
                    <span className="animate-spin text-lg">⚡</span>
                  ) : (
                    <svg 
                      className="w-5 h-5" 
                      fill="none" 
                      stroke="currentColor" 
                      viewBox="0 0 24 24"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth={2} 
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" 
                      />
                    </svg>
                  )}
                </div>
              </div>
            </div>
            
            {/* Dropdown Results */}
            {showDropdown && (
              <div className="absolute top-full mt-2 w-full bg-neutral-900 border border-neutral-700 rounded-lg shadow-xl max-h-96 overflow-y-auto z-50">
                {isLoading ? (
                  <div className="p-4 text-center text-neutral-400">
                    <span className="animate-spin mr-2">⚡</span>
                    Searching...
                  </div>
                ) : results.length > 0 ? (
                  <div className="py-2">
                    {results.map((result, index) => (
                      <button
                        key={`${result.entity_type}-${result.entity_id}-${index}`}
                        onClick={() => handleResultClick(result)}
                        className="w-full px-4 py-3 hover:bg-neutral-800 transition-colors text-left border-b border-neutral-800 last:border-b-0"
                      >
                        <div className="flex items-start gap-3">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-white truncate">
                                {result.name}
                              </span>
                              <span
                                className={`px-2 py-0.5 rounded text-xs font-semibold border capitalize flex-shrink-0 ${getTypeBadgeColor(
                                  result.entity_type
                                )}`}
                              >
                                {result.entity_type}
                              </span>
                            </div>
                            <p className="text-sm text-neutral-400 line-clamp-2">
                              {result.snippet}
                            </p>
                          </div>
                          <div className="flex-shrink-0">
                            <p className="text-xs text-neutral-500 mb-1">Match</p>
                            <p className="text-sm font-semibold text-green-400">
                              {(result.similarity * 100).toFixed(0)}%
                            </p>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : searchQuery.trim().length >= 3 ? (
                  <div className="p-4 text-center text-neutral-400">
                    No results found
                  </div>
                ) : null}
              </div>
            )}
          </div>
        )}

        {/* Right: Navigation Links */}
        <div className="flex items-center gap-4 flex-shrink-0">
          <Link 
            href="/dashboard" 
            className="text-neutral-400 hover:text-white transition-colors px-4 py-2 rounded-lg hover:bg-neutral-800"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </nav>
  )
}
