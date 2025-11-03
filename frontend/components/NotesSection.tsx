'use client'

import { useState } from 'react'
import { Note, api } from '@/lib/api'

interface NotesSectionProps {
  characterId: number
  initialNotes: Note[]
}

export default function NotesSection({
  characterId,
  initialNotes,
}: NotesSectionProps) {
  const [notes, setNotes] = useState<Note[]>(initialNotes)
  const [noteText, setNoteText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!noteText.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const newNote = await api.characters.addNote(characterId, noteText)
      setNotes([newNote, ...notes])
      setNoteText('')
    } catch (err) {
      setError('Failed to add note. Please try again.')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-neutral-900 to-black rounded-2xl p-8 border border-neutral-800 glow-effect">
      <h3 className="text-2xl font-semibold mb-4">Notes</h3>

      <form onSubmit={handleAddNote} className="mb-6">
        <textarea
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          placeholder="Add a note about this character..."
          className="w-full bg-black border border-neutral-800 rounded-xl p-4 mb-4 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 transition-all text-neutral-100"
          rows={3}
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !noteText.trim()}
          className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-3 rounded-xl font-semibold transition-all glow-effect disabled:glow-effect-0"
        >
          {isLoading ? 'Adding...' : 'Add Note'}
        </button>
        {error && (
          <p className="text-red-400 text-sm mt-2">{error}</p>
        )}
      </form>

      <div className="space-y-3">
        {notes.length === 0 ? (
          <p className="text-neutral-400 text-center py-4">
            No notes yet. Add one above!
          </p>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="bg-black/50 border border-neutral-800 rounded-xl p-5 hover:border-neutral-700 transition-colors"
            >
              <p className="text-neutral-300 whitespace-pre-wrap">
                {note.note_text}
              </p>
              <p className="text-neutral-500 text-xs mt-2">
                {new Date(note.created_at).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

