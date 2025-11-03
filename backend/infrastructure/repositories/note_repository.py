"""Unified note repository implementation."""
import aiosqlite
from datetime import datetime
from core.models import Note
from core.ports import NoteRepository
from shared.config import settings
from shared.logging import logger


class SQLiteNoteRepository(NoteRepository):
    """SQLite implementation of unified note repository."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def get_notes(self, subject_type: str, subject_id: int) -> list[Note]:
        """Get all notes for a subject (character, location, or episode)."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "SELECT id, subject_type, subject_id, note_text, created_at "
                "FROM notes WHERE subject_type = ? AND subject_id = ? "
                "ORDER BY created_at DESC",
                (subject_type, subject_id),
            )
            rows = await cursor.fetchall()
            return [
                Note(
                    id=row["id"],
                    subject_type=row["subject_type"],
                    subject_id=row["subject_id"],
                    note_text=row["note_text"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
        finally:
            await conn.close()
    
    async def get_notes_paginated(
        self, subject_type: str, subject_id: int, page: int = 1, limit: int = 20
    ) -> tuple[list[Note], int]:
        """Get paginated notes for a subject, ordered by created_at DESC (latest first)."""
        conn = await self._get_connection()
        try:
            # Get total count
            cursor = await conn.execute(
                "SELECT COUNT(*) as count "
                "FROM notes WHERE subject_type = ? AND subject_id = ?",
                (subject_type, subject_id),
            )
            row = await cursor.fetchone()
            total = row["count"] if row else 0
            
            # Get paginated notes (latest first)
            offset = (page - 1) * limit
            cursor = await conn.execute(
                "SELECT id, subject_type, subject_id, note_text, created_at "
                "FROM notes WHERE subject_type = ? AND subject_id = ? "
                "ORDER BY created_at DESC "
                "LIMIT ? OFFSET ?",
                (subject_type, subject_id, limit, offset),
            )
            rows = await cursor.fetchall()
            notes = [
                Note(
                    id=row["id"],
                    subject_type=row["subject_type"],
                    subject_id=row["subject_id"],
                    note_text=row["note_text"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
            return notes, total
        finally:
            await conn.close()
    
    async def add_note(self, subject_type: str, subject_id: int, note_text: str) -> Note:
        """Add a note to a subject (character, location, or episode)."""
        # Validate subject_type
        if subject_type not in ["character", "location", "episode"]:
            raise ValueError(f"Invalid subject_type: {subject_type}. Must be 'character', 'location', or 'episode'")
        
        conn = await self._get_connection()
        try:
            # Try to insert, ignore if duplicate (based on unique constraint)
            try:
                cursor = await conn.execute(
                    "INSERT INTO notes (subject_type, subject_id, note_text) "
                    "VALUES (?, ?, ?)",
                    (subject_type, subject_id, note_text),
                )
                await conn.commit()
                
                note_id = cursor.lastrowid
                if note_id is None:
                    raise ValueError("Failed to create note")
                
                # Fetch the created note
                cursor = await conn.execute(
                    "SELECT id, subject_type, subject_id, note_text, created_at "
                    "FROM notes WHERE id = ?",
                    (note_id,),
                )
                row = await cursor.fetchone()
                if not row:
                    raise ValueError("Failed to fetch created note")
                
                return Note(
                    id=row["id"],
                    subject_type=row["subject_type"],
                    subject_id=row["subject_id"],
                    note_text=row["note_text"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            except aiosqlite.IntegrityError:
                # Duplicate note - fetch existing one
                cursor = await conn.execute(
                    "SELECT id, subject_type, subject_id, note_text, created_at "
                    "FROM notes WHERE subject_type = ? AND subject_id = ? AND note_text = ?",
                    (subject_type, subject_id, note_text),
                )
                row = await cursor.fetchone()
                if row:
                    return Note(
                        id=row["id"],
                        subject_type=row["subject_type"],
                        subject_id=row["subject_id"],
                        note_text=row["note_text"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                raise ValueError("Failed to handle duplicate note")
        finally:
            await conn.close()
    
    async def update_note(self, note_id: int, note_text: str) -> Note:
        """Update a note by ID."""
        conn = await self._get_connection()
        try:
            # First check if note exists
            cursor = await conn.execute(
                "SELECT id, subject_type, subject_id, note_text, created_at "
                "FROM notes WHERE id = ?",
                (note_id,),
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError(f"Note with id {note_id} not found")
            
            # Update the note
            await conn.execute(
                "UPDATE notes SET note_text = ? WHERE id = ?",
                (note_text, note_id),
            )
            await conn.commit()
            
            # Fetch the updated note
            cursor = await conn.execute(
                "SELECT id, subject_type, subject_id, note_text, created_at "
                "FROM notes WHERE id = ?",
                (note_id,),
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Failed to fetch updated note")
            
            return Note(
                id=row["id"],
                subject_type=row["subject_type"],
                subject_id=row["subject_id"],
                note_text=row["note_text"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        finally:
            await conn.close()
    
    async def delete_note(self, note_id: int) -> None:
        """Delete a note by ID."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "DELETE FROM notes WHERE id = ?",
                (note_id,),
            )
            await conn.commit()
            
            if cursor.rowcount == 0:
                raise ValueError(f"Note with id {note_id} not found")
        finally:
            await conn.close()

