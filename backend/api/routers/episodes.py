"""Episode routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_episode_service
from api.dtos import EpisodeResponse, EpisodeSummaryResponse, CharacterResponse, NoteResponse, AddNoteRequest
from core.services import EpisodeService


router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("", response_model=list[EpisodeSummaryResponse])
async def get_episodes(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Get paginated episodes."""
    try:
        episodes, total = await episode_service.get_episodes_paginated(page, limit)
        return [
            EpisodeSummaryResponse(
                id=ep.id,
                name=ep.name,
                air_date=ep.air_date,
                episode=ep.episode,
                character_count=getattr(ep, '_character_count', len(ep.characters) if isinstance(ep.characters, list) else (len(ep.characters_data) if ep.characters_data else 0)),
                characters=None,  # Don't include characters in list - only when fetching single episode
            )
            for ep in episodes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: int,
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Get a specific episode."""
    try:
        episode, characters = await episode_service.get_episode_with_characters(episode_id)
        from api.dtos import CharacterResponse
        from shared.logging import logger
        
        try:
            character_responses = [
                CharacterResponse(
                    id=char.id,
                    name=char.name,
                    status=char.status,
                    species=char.species,
                    type=char.type,
                    gender=char.gender,
                    origin=char.origin,
                    location=char.location,
                    image=char.image,
                    episode=char.episode,
                    url=getattr(char, 'url', ''),
                    created=getattr(char, 'created', ''),
                )
                for char in characters
            ]
        except Exception as e:
            logger.error(f"Error converting characters to response: {e}")
            character_responses = []
        
        return EpisodeResponse(
            id=episode.id,
            name=episode.name,
            air_date=episode.air_date,
            episode=episode.episode,
            characters=character_responses,
        )
    except ValueError as e:
        from shared.logging import logger
        logger.error(f"Episode {episode_id} not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from shared.logging import logger
        import traceback
        logger.error(f"Error fetching episode {episode_id}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{episode_id}/notes", response_model=list[NoteResponse])
async def get_episode_notes(
    episode_id: int,
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Get notes for an episode."""
    try:
        _, notes = await episode_service.get_episode_with_notes(episode_id)
        return [
            NoteResponse(
                id=note.id,
                subject_type=note.subject_type,
                subject_id=note.subject_id,
                note_text=note.note_text,
                created_at=note.created_at.isoformat(),
            )
            for note in notes
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{episode_id}/notes", response_model=NoteResponse)
async def add_episode_note(
    episode_id: int,
    request: AddNoteRequest,
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Add a note to an episode."""
    try:
        note = await episode_service.add_note(episode_id, request.note_text)
        
        # Rebuild search index after adding note
        from api.deps import get_generation_service
        generation_service = get_generation_service()
        await generation_service.rebuild_search_index("episode", str(episode_id))
        
        return NoteResponse(
            id=note.id,
            subject_type=note.subject_type,
            subject_id=note.subject_id,
            note_text=note.note_text,
            created_at=note.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_episode_note(
    note_id: int,
    request: AddNoteRequest,
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Update a note."""
    try:
        note = await episode_service.update_note(note_id, request.note_text)
        return NoteResponse(
            id=note.id,
            subject_type=note.subject_type,
            subject_id=note.subject_id,
            note_text=note.note_text,
            created_at=note.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
async def delete_episode_note(
    note_id: int,
    episode_service: EpisodeService = Depends(get_episode_service),
):
    """Delete a note."""
    try:
        await episode_service.delete_note(note_id)
        return {"message": "Note deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

