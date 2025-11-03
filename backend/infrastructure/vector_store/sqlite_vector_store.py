"""SQLite-based vector store implementation."""
import aiosqlite
import json
import numpy as np
from typing import Any
from core.models import Character, SearchResult
from core.ports import VectorStore
from shared.config import settings
from shared.logging import logger


class SQLiteVectorStore(VectorStore):
    """SQLite implementation of vector store using cosine similarity."""
    
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.database_url.replace(
            "sqlite+aiosqlite:///", ""
        )
    
    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection."""
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        return conn
    
    def _cosine_similarity(
        self, vec1: list[float], vec2: list[float]
    ) -> float:
        """Compute cosine similarity between two vectors."""
        vec1_arr = np.array(vec1)
        vec2_arr = np.array(vec2)
        
        dot_product = np.dot(vec1_arr, vec2_arr)
        norm1 = np.linalg.norm(vec1_arr)
        norm2 = np.linalg.norm(vec2_arr)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    async def upsert_character(
        self, character: Character, embedding: list[float]
    ) -> None:
        """Store character with embedding."""
        async with await self._get_connection() as conn:
            # Convert embedding to JSON for storage
            embedding_json = json.dumps(embedding)
            character_json = json.dumps({
                "id": character.id,
                "name": character.name,
                "status": character.status,
                "species": character.species,
                "type": character.type,
                "gender": character.gender,
                "origin": character.origin,
                "location": character.location,
                "image": character.image,
                "episode": character.episode,
                "url": character.url,
                "created": character.created,
            })
            
            await conn.execute(
                "INSERT OR REPLACE INTO character_embeddings "
                "(character_id, character_name, character_data, embedding) "
                "VALUES (?, ?, ?, ?)",
                (character.id, character.name, character_json, embedding_json),
            )
            await conn.commit()
    
    async def search(
        self, query_embedding: list[float], limit: int = 10
    ) -> list[SearchResult]:
        """Search for similar characters using cosine similarity."""
        async with await self._get_connection() as conn:
            cursor = await conn.execute(
                "SELECT character_id, character_name, character_data, embedding "
                "FROM character_embeddings"
            )
            rows = await cursor.fetchall()
            
            if not rows:
                logger.warning(
                    "Vector store is empty. Run scripts/seed_embeddings.py to populate."
                )
                return []
            
            results = []
            for row in rows:
                try:
                    stored_embedding = json.loads(row["embedding"])
                    similarity = self._cosine_similarity(
                        query_embedding, stored_embedding
                    )
                    
                    character_data = json.loads(row["character_data"])
                    character = Character(
                        id=character_data["id"],
                        name=character_data["name"],
                        status=character_data["status"],
                        species=character_data["species"],
                        type=character_data["type"],
                        gender=character_data["gender"],
                        origin=character_data["origin"],
                        location=character_data["location"],
                        image=character_data["image"],
                        episode=character_data["episode"],
                        url=character_data["url"],
                        created=character_data["created"],
                    )
                    
                    results.append(
                        SearchResult(
                            character=character,
                            similarity_score=similarity,
                        )
                    )
                except Exception as e:
                    logger.warning(
                        f"Error processing embedding for character "
                        f"{row['character_id']}: {e}"
                    )
                    continue
            
            # Sort by similarity (descending) and return top results
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            return results[:limit]

