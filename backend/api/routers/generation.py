"""Generation routes."""
from fastapi import APIRouter, Depends, HTTPException
from api.deps import get_generation_service
from api.dtos import (
    GeneratedContentResponse,
    DialogueRequest,
    GenerateSummaryRequest,
    GenerateSummaryResponse,
    RegenerateNoteRequest,
    RegenerateNoteResponse,
)
from core.services import GenerationService


router = APIRouter(prefix="/generate", tags=["generation"])


@router.post(
    "/location-summary/{location_id}",
    response_model=GeneratedContentResponse,
)
async def generate_location_summary(
    location_id: int,
    generation_service: GenerationService = Depends(get_generation_service),
):
    """Generate a location summary with AI evaluation."""
    try:
        content = await generation_service.generate_location_summary(location_id)
        return GeneratedContentResponse(
            id=content.id,
            subject_id=content.subject_id,
            prompt_type=content.prompt_type,
            output_text=content.output_text,
            factual_score=content.factual_score,
            completeness_score=content.completeness_score,
            creativity_score=content.creativity_score,
            relevance_score=content.relevance_score,
            created_at=content.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/episode-summary/{episode_id}",
    response_model=GeneratedContentResponse,
)
async def generate_episode_summary(
    episode_id: int,
    generation_service: GenerationService = Depends(get_generation_service),
):
    """Generate an episode summary with AI evaluation."""
    try:
        content = await generation_service.generate_episode_summary(episode_id)
        return GeneratedContentResponse(
            id=content.id,
            subject_id=content.subject_id,
            prompt_type=content.prompt_type,
            output_text=content.output_text,
            factual_score=content.factual_score,
            completeness_score=content.completeness_score,
            creativity_score=content.creativity_score,
            relevance_score=content.relevance_score,
            created_at=content.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/character-summary/{character_id}",
    response_model=GeneratedContentResponse,
)
async def generate_character_summary(
    character_id: int,
    generation_service: GenerationService = Depends(get_generation_service),
):
    """Generate a character summary with AI evaluation."""
    try:
        content = await generation_service.generate_character_summary(character_id)
        return GeneratedContentResponse(
            id=content.id,
            subject_id=content.subject_id,
            prompt_type=content.prompt_type,
            output_text=content.output_text,
            factual_score=content.factual_score,
            completeness_score=content.completeness_score,
            creativity_score=content.creativity_score,
            relevance_score=content.relevance_score,
            created_at=content.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/dialogue/{character_id1}",
    response_model=GeneratedContentResponse,
)
async def generate_dialogue(
    character_id1: int,
    request: DialogueRequest,
    generation_service: GenerationService = Depends(get_generation_service),
):
    """Generate a dialogue between two characters."""
    try:
        content = await generation_service.generate_character_dialogue(
            character_id1, request.character_id2, request.topic
        )
        return GeneratedContentResponse(
            id=content.id,
            subject_id=content.subject_id,
            prompt_type=content.prompt_type,
            output_text=content.output_text,
            factual_score=content.factual_score,
            completeness_score=content.completeness_score,
            creativity_score=content.creativity_score,
            relevance_score=content.relevance_score,
            created_at=content.created_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/regenerate-note",
    response_model=RegenerateNoteResponse,
)
async def regenerate_note(
    request: RegenerateNoteRequest,
    generation_service: GenerationService = Depends(get_generation_service),
):
    """Regenerate/improve note text with AI - helper tool, no scoring or DB entry."""
    try:
        improved_text = await generation_service.regenerate_note_text(
            request.note_text,
            request.entity_type,
            request.entity_id,
        )
        return RegenerateNoteResponse(improved_text=improved_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

