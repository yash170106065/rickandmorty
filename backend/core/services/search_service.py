"""Semantic search service."""
import numpy as np
from dataclasses import dataclass
from core.ports import LLMProvider
from infrastructure.repositories.search_index_repository import SQLiteSearchIndexRepository
from shared.logging import logger


@dataclass
class SearchResult:
    """Search result model."""
    entity_type: str
    entity_id: str
    name: str
    snippet: str
    similarity: float


class SearchService:
    """Service for semantic search operations."""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.search_index_repo = SQLiteSearchIndexRepository()
    
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
    
    async def semantic_search(
        self, query: str, limit: int = 10
    ) -> list[SearchResult]:
        """Perform semantic search across characters, locations, and episodes."""
        try:
            # Get embedding for query
            query_embedding = await self.llm_provider.get_embedding(query)
            
            # Get all entries from search index
            entries = await self.search_index_repo.get_all_entries()
            
            if not entries:
                logger.warning("Search index is empty. No results available.")
                return []
            
            # Compute similarity for each entry
            results = []
            for entry in entries:
                try:
                    similarity = self._cosine_similarity(
                        query_embedding, entry["embedding_vector"]
                    )
                    
                    # Extract snippet (first ~200 chars of text_blob)
                    snippet = entry["text_blob"][:200]
                    if len(entry["text_blob"]) > 200:
                        snippet += "..."
                    
                    # Extract name from text_blob (first line usually contains name)
                    name = entry["text_blob"].split("\n")[0]
                    if ":" in name:
                        name = name.split(":", 1)[1].strip()
                    
                    results.append(
                        SearchResult(
                            entity_type=entry["entity_type"],
                            entity_id=entry["entity_id"],
                            name=name,
                            snippet=snippet,
                            similarity=similarity,
                        )
                    )
                except Exception as e:
                    logger.warning(
                        f"Error processing entry {entry['entity_type']}/{entry['entity_id']}: {e}"
                    )
                    continue
            
            # Sort by similarity (descending) and return top results
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
