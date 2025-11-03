"""Generated content repository implementation."""
import aiosqlite
import json
from datetime import datetime
from core.models import GeneratedContent
from core.ports import GeneratedContentRepository
from shared.config import settings


class SQLiteGeneratedContentRepository(GeneratedContentRepository):
    """SQLite implementation of generated content repository."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    async def save(self, content: GeneratedContent) -> GeneratedContent:
        """Save generated content."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "INSERT INTO generated_content "
                "(subject_id, prompt_type, output_text, factual_score, "
                "completeness_score, creativity_score, relevance_score, context_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    content.subject_id,
                    content.prompt_type,
                    content.output_text,
                    content.factual_score,
                    content.completeness_score,
                    content.creativity_score,
                    content.relevance_score,
                    json.dumps(content.context_json),
                ),
            )
            await conn.commit()
            
            note_id = cursor.lastrowid
            if note_id is None:
                raise ValueError("Failed to save generated content")
            
            # Fetch the created content
            cursor = await conn.execute(
                "SELECT id, subject_id, prompt_type, output_text, "
                "factual_score, completeness_score, creativity_score, relevance_score, "
                "context_json, created_at "
                "FROM generated_content WHERE id = ?",
                (note_id,),
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Failed to fetch created content")
            
            # Handle relevance_score which may not exist in older rows
            try:
                relevance_score = row["relevance_score"] if row["relevance_score"] is not None else 0.0
            except (KeyError, IndexError):
                relevance_score = 0.0
            
            return GeneratedContent(
                id=row["id"],
                subject_id=row["subject_id"],
                prompt_type=row["prompt_type"],
                output_text=row["output_text"],
                factual_score=row["factual_score"],
                completeness_score=row["completeness_score"],
                creativity_score=row["creativity_score"],
                relevance_score=relevance_score,
                context_json=json.loads(row["context_json"]),
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        finally:
            await conn.close()
    
    async def get_by_subject(
        self, subject_id: int, prompt_type: str
    ) -> list[GeneratedContent]:
        """Get generated content for a subject."""
        conn = await self._get_connection()
        try:
            cursor = await conn.execute(
                "SELECT id, subject_id, prompt_type, output_text, "
                "factual_score, completeness_score, creativity_score, relevance_score, "
                "context_json, created_at "
                "FROM generated_content "
                "WHERE subject_id = ? AND prompt_type = ? "
                "ORDER BY created_at DESC",
                (subject_id, prompt_type),
            )
            rows = await cursor.fetchall()
            return [
                GeneratedContent(
                    id=row["id"],
                    subject_id=row["subject_id"],
                    prompt_type=row["prompt_type"],
                    output_text=row["output_text"],
                    factual_score=row["factual_score"],
                    completeness_score=row["completeness_score"],
                    creativity_score=row["creativity_score"],
                    relevance_score=row["relevance_score"] if row["relevance_score"] is not None else 0.0,
                    context_json=json.loads(row["context_json"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
                for row in rows
            ]
        finally:
            await conn.close()
    
    async def get_latest_by_subject(
        self, subject_id: int, prompt_type: str
    ) -> GeneratedContent | None:
        """Get the most recent generated content for a subject."""
        existing = await self.get_by_subject(subject_id, prompt_type)
        return existing[0] if existing else None
    
    async def update_scores(
        self,
        content_id: int,
        factual_score: float,
        completeness_score: float,
        creativity_score: float,
        relevance_score: float,
    ) -> None:
        """Update evaluation scores for existing content."""
        conn = await self._get_connection()
        try:
            await conn.execute(
                "UPDATE generated_content "
                "SET factual_score = ?, completeness_score = ?, creativity_score = ?, relevance_score = ? "
                "WHERE id = ?",
                (factual_score, completeness_score, creativity_score, relevance_score, content_id),
            )
            await conn.commit()
        finally:
            await conn.close()

