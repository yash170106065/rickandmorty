"""Character repository implementation."""
import aiosqlite
from datetime import datetime
from core.models import Note
from core.ports import CharacterRepository
from shared.config import settings
from shared.logging import logger


class SQLiteCharacterRepository(CharacterRepository):
    """SQLite implementation of character repository."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def get_notes(self, character_id: int) -> list[Note]:
        """Get all notes for a character."""
        async with await self._get_connection() as conn:
            cursor = await conn.execute(
                "SELECT id, character_id, note_text, created_at "
                "FROM character_notes WHERE character_id = ? "
                "ORDER BY created_at DESC",
                (character_id,),
            )
            rows = await cursor.fetchall()
            return [
                Note(
                    id=row["id"],
                    subject_type="character",
                    subject_id=row["character_id"],
                    note_text=row["note_text"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
    
    async def add_note(self, character_id: int, note_text: str) -> Note:
        """Add a note to a character."""
        async with await self._get_connection() as conn:
            cursor = await conn.execute(
                "INSERT INTO character_notes (character_id, note_text) "
                "VALUES (?, ?)",
                (character_id, note_text),
            )
            await conn.commit()
            
            note_id = cursor.lastrowid
            if note_id is None:
                raise ValueError("Failed to create note")
            
            # Fetch the created note
            cursor = await conn.execute(
                "SELECT id, character_id, note_text, created_at "
                "FROM character_notes WHERE id = ?",
                (note_id,),
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Failed to fetch created note")
            
            return Note(
                id=row["id"],
                subject_type="character",
                subject_id=row["character_id"],
                note_text=row["note_text"],
                created_at=datetime.fromisoformat(row["created_at"]),
            )

