'use client'

import { useState, useEffect, useRef } from 'react'
import { api, Note } from '@/lib/api'

interface NotesPanelProps {
  subjectType: 'character' | 'location' | 'episode'
  subjectId: number
  subjectName: string
}

export default function NotesPanel({ subjectType, subjectId, subjectName }: NotesPanelProps) {
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)
  const [newNote, setNewNote] = useState('')
  const [adding, setAdding] = useState(false)
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null)
  const [editingText, setEditingText] = useState('')
  const [updating, setUpdating] = useState(false)
  const [deleting, setDeleting] = useState<number | null>(null)
  const [regenerating, setRegenerating] = useState(false)
  const notesContainerRef = useRef<HTMLDivElement>(null)

  const fetchNotes = async () => {
    try {
      setLoading(true)
      let fetchedNotes: Note[] = []
      
      if (subjectType === 'character') {
        fetchedNotes = await api.characters.getNotes(subjectId)
      } else if (subjectType === 'location') {
        fetchedNotes = await api.locations.getNotes(subjectId)
      } else if (subjectType === 'episode') {
        fetchedNotes = await api.episodes.getNotes(subjectId)
      }
      
      // Reverse the order for display: oldest first, latest at bottom
      setNotes([...fetchedNotes].reverse())
      
      // Scroll to bottom after notes are loaded (to show latest notes first)
      setTimeout(() => {
        const container = notesContainerRef.current
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      }, 0)
    } catch (err) {
      console.error('Failed to fetch notes:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (subjectId) {
      fetchNotes()
    }
  }, [subjectType, subjectId])

  const handleAddNote = async () => {
    if (!newNote.trim()) return

    try {
      setAdding(true)
      let addedNote: Note
      
      if (subjectType === 'character') {
        addedNote = await api.characters.addNote(subjectId, newNote.trim())
      } else if (subjectType === 'location') {
        addedNote = await api.locations.addNote(subjectId, newNote.trim())
      } else {
        addedNote = await api.episodes.addNote(subjectId, newNote.trim())
      }
      
      // Add new note at the end (latest at bottom display)
      setNotes([...notes, addedNote])
      setNewNote('')
    } catch (err) {
      console.error('Failed to add note:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to add note. Please try again.'
      alert(errorMessage)
    } finally {
      setAdding(false)
    }
  }

  const handleEditNote = (note: Note) => {
    setEditingNoteId(note.id)
    setEditingText(note.note_text)
  }

  const handleCancelEdit = () => {
    setEditingNoteId(null)
    setEditingText('')
  }

  const handleUpdateNote = async (noteId: number) => {
    if (!editingText.trim()) {
      alert('Note cannot be empty')
      return
    }

    try {
      setUpdating(true)
      let updatedNote: Note
      
      if (subjectType === 'character') {
        updatedNote = await api.characters.updateNote(noteId, editingText.trim())
      } else if (subjectType === 'location') {
        updatedNote = await api.locations.updateNote(noteId, editingText.trim())
      } else {
        updatedNote = await api.episodes.updateNote(noteId, editingText.trim())
      }
      
      setNotes(notes.map(note => note.id === noteId ? updatedNote : note))
      setEditingNoteId(null)
      setEditingText('')
    } catch (err) {
      console.error('Failed to update note:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to update note. Please try again.'
      alert(errorMessage)
    } finally {
      setUpdating(false)
    }
  }

  const handleDeleteNote = async (noteId: number) => {
    if (!confirm('Are you sure you want to delete this note?')) {
      return
    }

    try {
      setDeleting(noteId)
      
      if (subjectType === 'character') {
        await api.characters.deleteNote(noteId)
      } else if (subjectType === 'location') {
        await api.locations.deleteNote(noteId)
      } else {
        await api.episodes.deleteNote(noteId)
      }
      
      setNotes(notes.filter(note => note.id !== noteId))
    } catch (err) {
      console.error('Failed to delete note:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete note. Please try again.'
      alert(errorMessage)
    } finally {
      setDeleting(null)
    }
  }

  const handleRegenerateWithAI = async (forEditing: boolean = false) => {
    try {
      setRegenerating(true)
      
      // Get the current text (either from new note or editing note)
      const currentText = forEditing ? editingText : newNote
      
      // If no text, use empty string to let AI generate something new
      const textToImprove = currentText.trim() || 'Create a helpful note'
      
      // Call the regenerate endpoint
      const response = await api.generation.regenerateNote(
        textToImprove,
        subjectType,
        subjectId
      )
      
      // Replace the text with improved version
      if (forEditing) {
        setEditingText(response.improved_text)
      } else {
        setNewNote(response.improved_text)
      }
    } catch (err) {
      console.error('Failed to regenerate with AI:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to regenerate with AI. Please try again.'
      alert(errorMessage)
    } finally {
      setRegenerating(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-b from-neutral-900 to-black border-l border-neutral-800 overflow-hidden">
      <div className="px-4 py-3 border-b border-neutral-800">
        <h2 className="text-lg font-bold gradient-text">Notes</h2>
      </div>

      <div 
        ref={notesContainerRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-3"
      >
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="text-center">
              <div className="text-4xl mb-4 animate-spin">⚡</div>
              <p className="text-neutral-400">Loading notes...</p>
            </div>
          </div>
        ) : notes.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="text-6xl mb-4 opacity-50">📝</div>
              <p className="text-neutral-400 text-lg">No notes yet</p>
              <p className="text-neutral-500 text-sm mt-2">Add your first note below</p>
            </div>
          </div>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="bg-neutral-800/50 rounded-xl p-4 border border-neutral-700 hover:border-neutral-600 transition-colors"
            >
              {editingNoteId === note.id ? (
                <div className="space-y-2">
                  <textarea
                    value={editingText}
                    onChange={(e) => setEditingText(e.target.value)}
                    className="w-full bg-neutral-900 border border-neutral-600 rounded-lg px-3 py-2 text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500 resize-none"
                    rows={3}
                    disabled={updating || regenerating}
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleUpdateNote(note.id)}
                      disabled={!editingText.trim() || updating || regenerating}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-neutral-700 disabled:cursor-not-allowed text-white text-sm rounded-lg font-semibold transition-colors"
                    >
                      {updating ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      onClick={() => handleRegenerateWithAI(true)}
                      disabled={updating || regenerating}
                      className="px-3 py-1 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 disabled:from-neutral-700 disabled:to-neutral-800 disabled:cursor-not-allowed text-white text-sm rounded-lg font-semibold transition-all flex items-center gap-1"
                    >
                      <span>{regenerating ? '⏳' : '✨'}</span>
                      {regenerating ? 'AI...' : 'AI'}
                    </button>
                    <button
                      onClick={handleCancelEdit}
                      disabled={updating || regenerating}
                      className="px-3 py-1 bg-neutral-700 hover:bg-neutral-600 disabled:bg-neutral-800 disabled:cursor-not-allowed text-white text-sm rounded-lg font-semibold transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <p className="text-white mb-2 whitespace-pre-wrap">{note.note_text}</p>
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-neutral-500">{formatDate(note.created_at)}</p>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditNote(note)}
                        className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteNote(note.id)}
                        disabled={deleting === note.id}
                        className="text-xs text-red-400 hover:text-red-300 disabled:text-neutral-600 transition-colors"
                      >
                        {deleting === note.id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>

      <div className="px-4 py-3 border-t border-neutral-800 bg-neutral-900/50">
        <div className="flex flex-col gap-2">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleAddNote()
              }
            }}
            placeholder={`Add a note about ${subjectName}...`}
            className="w-full bg-neutral-800 border border-neutral-700 rounded-lg px-4 py-3 text-white placeholder-neutral-500 focus:outline-none focus:border-blue-500 resize-none"
            rows={3}
            disabled={adding || regenerating}
          />
          <div className="flex gap-2">
            <button
              onClick={handleAddNote}
              disabled={!newNote.trim() || adding || regenerating}
              className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:bg-neutral-700 disabled:cursor-not-allowed text-white rounded-lg text-xs font-semibold transition-colors"
            >
              {adding ? 'Adding...' : 'Add Note'}
            </button>
            <button
              onClick={() => handleRegenerateWithAI(false)}
              disabled={regenerating || adding}
              className="flex-1 px-3 py-1.5 bg-gradient-to-br from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 disabled:from-neutral-700 disabled:to-neutral-800 disabled:cursor-not-allowed text-white rounded-lg text-xs font-semibold transition-all duration-200 flex items-center justify-center gap-1.5 shadow-lg shadow-purple-500/20 hover:shadow-purple-500/30"
            >
              <span className="text-sm">{regenerating ? '⏳' : '✨'}</span>
              {regenerating ? 'AI Improving...' : 'Improve With AI'}
            </button>
          </div>
          <p className="text-xs text-neutral-500 text-center">
            Press Cmd/Ctrl + Enter to add
          </p>
        </div>
      </div>
    </div>
  )
}

