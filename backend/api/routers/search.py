"""Search routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_search_service
from api.dtos import UnifiedSearchResultResponse
from core.services.search_service import SearchService


router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[UnifiedSearchResultResponse])
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    search_service: SearchService = Depends(get_search_service),
):
    """Semantic search across characters, locations, and episodes."""
    try:
        results = await search_service.semantic_search(q, limit=limit)
        return [
            UnifiedSearchResultResponse(
                entity_type=result.entity_type,
                entity_id=result.entity_id,
                name=result.name,
                snippet=result.snippet,
                similarity=result.similarity,
            )
            for result in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

