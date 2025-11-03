const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const API_V1 = `${API_URL}/v1`

export interface Location {
  id: number
  name: string
  type: string
  dimension: string
  resident_count: number
  residents: Resident[]
}

export interface LocationDetail {
  id: number
  name: string
  type: string
  dimension: string
  residents: Character[]
}

export interface Resident {
  id: number
  name: string
  status: string
  species: string
  image: string
}

export interface OriginLocation {
  name: string
  url: string
}

export interface Character {
  id: number
  name: string
  status: string
  species: string
  type: string
  gender: string
  origin: OriginLocation | Record<string, never>
  location: OriginLocation | Record<string, never>
  image: string
  episode: string[]
  episodes?: Episode[]  // Optional: full episode objects when available
  url: string
  created: string
}

export interface Note {
  id: number
  subject_type: 'character' | 'location' | 'episode'
  subject_id: number
  note_text: string
  created_at: string
}

export interface GeneratedContent {
  id: number
  subject_id: number
  prompt_type: string
  output_text: string
  factual_score: number
  completeness_score: number
  creativity_score: number
  relevance_score: number
  created_at: string
}

export interface Episode {
  id: number
  name: string
  air_date: string
  episode: string
  character_count: number
  characters?: Character[]  // Optional: full character objects when available
}

export interface EpisodeDetail {
  id: number
  name: string
  air_date: string
  episode: string
  characters: Character[]
}

export interface SearchResult {
  character: Character
  similarity_score: number
}

export interface UnifiedSearchResult {
  entity_type: 'character' | 'location' | 'episode'
  entity_id: string
  name: string
  snippet: string
  similarity: number
}

export interface DialogueRequest {
  character_id2: number
  topic?: string
}

async function fetchAPI<T>(endpoint: string): Promise<T> {
  // endpoint already includes the full URL path (e.g., /v1/locations)
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`
  try {
    const response = await fetch(url)
    if (!response.ok) {
      let errorMessage = response.statusText
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // If response is not JSON, use statusText
      }
      throw new Error(`API error: ${errorMessage}`)
    }
    return response.json()
  } catch (err) {
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new Error(`Network error: Failed to connect to backend at ${API_URL}. Please ensure the backend is running.`)
    }
    throw err
  }
}

async function postAPI<T>(endpoint: string, data: unknown): Promise<T> {
  // endpoint already includes the full URL path
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    let errorMessage = response.statusText
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If response is not JSON, use statusText
    }
    throw new Error(`API error: ${errorMessage}`)
  }
  return response.json()
}

async function putAPI<T>(endpoint: string, data: unknown): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`
  const response = await fetch(url, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    let errorMessage = response.statusText
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If response is not JSON, use statusText
    }
    throw new Error(`API error: ${errorMessage}`)
  }
  return response.json()
}

async function deleteAPI<T>(endpoint: string): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`
  const response = await fetch(url, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  })
  if (!response.ok) {
    let errorMessage = response.statusText
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      // If response is not JSON, use statusText
    }
    throw new Error(`API error: ${errorMessage}`)
  }
  return response.json()
}

export const api = {
  locations: {
    getAll: () => fetchAPI<Location[]>(`${API_V1}/locations`),
    getPaginated: (page: number = 1, limit: number = 20) => 
      fetchAPI<Location[]>(`${API_V1}/locations?page=${page}&limit=${limit}`),
    getById: (id: number) => fetchAPI<LocationDetail>(`${API_V1}/locations/${id}`),
    getNotes: (id: number) => fetchAPI<Note[]>(`${API_V1}/locations/${id}/notes`),
    addNote: (id: number, noteText: string) =>
      postAPI<Note>(`${API_V1}/locations/${id}/notes`, { note_text: noteText }),
    updateNote: (noteId: number, noteText: string) =>
      putAPI<Note>(`${API_V1}/locations/notes/${noteId}`, { note_text: noteText }),
    deleteNote: (noteId: number) =>
      deleteAPI<{ message: string }>(`${API_V1}/locations/notes/${noteId}`),
  },
  characters: {
    getAll: () => fetchAPI<Character[]>(`${API_V1}/characters`),
    getPaginated: (page: number = 1, limit: number = 20) => 
      fetchAPI<Character[]>(`${API_V1}/characters?page=${page}&limit=${limit}`),
    getById: (id: number) => fetchAPI<Character>(`${API_V1}/characters/${id}`),
    getNotes: (id: number) => fetchAPI<Note[]>(`${API_V1}/characters/${id}/notes`),
    addNote: (id: number, noteText: string) =>
      postAPI<Note>(`${API_V1}/characters/${id}/notes`, { note_text: noteText }),
    updateNote: (noteId: number, noteText: string) =>
      putAPI<Note>(`${API_V1}/characters/notes/${noteId}`, { note_text: noteText }),
    deleteNote: (noteId: number) =>
      deleteAPI<{ message: string }>(`${API_V1}/characters/notes/${noteId}`),
    getEpisodes: (id: number) => fetchAPI<Episode[]>(`${API_V1}/characters/${id}/episodes`),
  },
  episodes: {
    getAll: () => fetchAPI<Episode[]>(`${API_V1}/episodes`),
    getPaginated: (page: number = 1, limit: number = 20) => 
      fetchAPI<Episode[]>(`${API_V1}/episodes?page=${page}&limit=${limit}`),
    getById: (id: number) => fetchAPI<EpisodeDetail>(`${API_V1}/episodes/${id}`),
    getNotes: (id: number) => fetchAPI<Note[]>(`${API_V1}/episodes/${id}/notes`),
    addNote: (id: number, noteText: string) =>
      postAPI<Note>(`${API_V1}/episodes/${id}/notes`, { note_text: noteText }),
    updateNote: (noteId: number, noteText: string) =>
      putAPI<Note>(`${API_V1}/episodes/notes/${noteId}`, { note_text: noteText }),
    deleteNote: (noteId: number) =>
      deleteAPI<{ message: string }>(`${API_V1}/episodes/notes/${noteId}`),
  },
  generation: {
    generateLocationSummary: (locationId: number) =>
      postAPI<GeneratedContent>(`${API_V1}/generate/location-summary/${locationId}`, {}),
    generateEpisodeSummary: (episodeId: number) =>
      postAPI<GeneratedContent>(`${API_V1}/generate/episode-summary/${episodeId}`, {}),
    generateCharacterSummary: (characterId: number) =>
      postAPI<GeneratedContent>(`${API_V1}/generate/character-summary/${characterId}`, {}),
    generateDialogue: (characterId1: number, characterId2: number, topic?: string) =>
      postAPI<GeneratedContent>(`${API_V1}/generate/dialogue/${characterId1}`, {
        character_id2: characterId2,
        topic: topic || '',
      }),
    regenerateNote: (noteText: string, entityType: 'character' | 'location' | 'episode', entityId: number) =>
      postAPI<{ improved_text: string }>(`${API_V1}/generate/regenerate-note`, {
        note_text: noteText,
        entity_type: entityType,
        entity_id: entityId,
      }),
  },
  search: {
    search: (query: string, limit: number = 10) =>
      fetchAPI<UnifiedSearchResult[]>(`${API_V1}/search?q=${encodeURIComponent(query)}&limit=${limit}`),
  },
}

