"""Search index repository implementation."""
import aiosqlite
import json
from shared.config import settings


class SQLiteSearchIndexRepository:
    """SQLite implementation of search index repository."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def upsert_entry(
        self,
        entity_type: str,
        entity_id: str,
        text_blob: str,
        embedding_vector: list[float],
    ) -> None:
        """Upsert an entry in the search index."""
        conn = await self._get_connection()
        try:
            embedding_json = json.dumps(embedding_vector)
            await conn.execute(
                "INSERT OR REPLACE INTO search_index "
                "(entity_type, entity_id, text_blob, embedding_vector, updated_at) "
                "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (entity_type, entity_id, text_blob, embedding_json),
            )
            await conn.commit()
        finally:
            await conn.close()
    
    async def get_all_entries(self) -> list[dict]:
        """Get all entries from search index."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "SELECT entity_type, entity_id, text_blob, embedding_vector "
                "FROM search_index"
            )
            rows = await cursor.fetchall()
            return [
                {
                    "entity_type": row["entity_type"],
                    "entity_id": row["entity_id"],
                    "text_blob": row["text_blob"],
                    "embedding_vector": json.loads(row["embedding_vector"]),
                }
                for row in rows
            ]
        finally:
            await conn.close()
    
    async def delete_entry(self, entity_type: str, entity_id: str) -> None:
        """Delete an entry from search index."""
        conn = await self._get_connection()
        try:
            await conn.execute(
                "DELETE FROM search_index WHERE entity_type = ? AND entity_id = ?",
                (entity_type, entity_id),
            )
            await conn.commit()
        finally:
            await conn.close()

