"""Generation repository implementation."""
import aiosqlite
import uuid
from datetime import datetime
from core.models import Generation
from shared.config import settings
from shared.logging import logger


class SQLiteGenerationRepository:
    """SQLite implementation of generation repository."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def close(self):
        """Close connection (for context manager)."""
        pass
    
    async def get_by_entity(
        self, entity_type: str, entity_id: str
    ) -> Generation | None:
        """Get generation by entity type and ID."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "SELECT generation_id, entity_type, entity_id, summary_text, "
                "factual_score, creativity_score, completeness_score, relevance_score, "
                "scores_status, created_at, updated_at "
                "FROM generations WHERE entity_type = ? AND entity_id = ?",
                (entity_type, entity_id),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            
            # Handle relevance_score which may not exist in older rows
            try:
                relevance_score = row["relevance_score"]
            except (KeyError, IndexError):
                relevance_score = None
            
            return Generation(
                generation_id=row["generation_id"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                summary_text=row["summary_text"],
                factual_score=row["factual_score"],
                creativity_score=row["creativity_score"],
                completeness_score=row["completeness_score"],
                relevance_score=relevance_score,
                scores_status=row["scores_status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        finally:
            await conn.close()
    
    async def create_initiated(
        self, entity_type: str, entity_id: str, summary_text: str
    ) -> Generation:
        """Create a generation with INITIATED status."""
        generation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        conn = await self._get_connection()
        try:
            await conn.execute(
                "INSERT INTO generations "
                "(generation_id, entity_type, entity_id, summary_text, "
                "factual_score, creativity_score, completeness_score, relevance_score, "
                "scores_status, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    generation_id,
                    entity_type,
                    entity_id,
                    summary_text,
                    None,  # factual_score
                    None,  # creativity_score
                    None,  # completeness_score
                    None,  # relevance_score
                    "INITIATED",
                    now,
                    now,
                ),
            )
            await conn.commit()
            
            return Generation(
                generation_id=generation_id,
                entity_type=entity_type,
                entity_id=entity_id,
                summary_text=summary_text,
                factual_score=None,
                creativity_score=None,
                completeness_score=None,
                relevance_score=None,
                scores_status="INITIATED",
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
            )
        finally:
            await conn.close()
    
    async def update_scores(
        self,
        entity_type: str,
        entity_id: str,
        factual_score: float,
        creativity_score: float,
        completeness_score: float,
        relevance_score: float,
    ) -> None:
        """Update scores and set status to GENERATED."""
        now = datetime.utcnow().isoformat()
        
        conn = await self._get_connection()
        try:
            await conn.execute(
                "UPDATE generations "
                "SET factual_score = ?, creativity_score = ?, completeness_score = ?, relevance_score = ?, "
                "scores_status = 'GENERATED', updated_at = ? "
                "WHERE entity_type = ? AND entity_id = ?",
                (
                    factual_score,
                    creativity_score,
                    completeness_score,
                    relevance_score,
                    now,
                    entity_type,
                    entity_id,
                ),
            )
            await conn.commit()
        finally:
            await conn.close()

