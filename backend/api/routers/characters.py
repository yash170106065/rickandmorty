"""Character routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_character_service
from api.dtos import (
    CharacterResponse,
    NoteResponse,
    AddNoteRequest,
)
from core.services import CharacterService
from shared.logging import logger


router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=list[CharacterResponse])
async def get_characters(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    character_service: CharacterService = Depends(get_character_service),
):
    """Get paginated characters."""
    try:
        characters, total = await character_service.get_characters_paginated(page, limit)
        from api.dtos import EpisodeSummaryResponse
        
        result = []
        for character in characters:
            try:
                # Don't include episodes in list - only when fetching single character
                result.append(CharacterResponse(
                    id=character.id,
                    name=character.name,
                    status=character.status,
                    species=character.species,
                    type=character.type,
                    gender=character.gender,
                    origin=character.origin,
                    location=character.location,
                    image=character.image,
                    episode=character.episode,
                    episodes=None,  # Episodes only fetched when getting single character
                    url=character.url,
                    created=character.created,
                ))
            except Exception as e:
                # Log error but continue with other characters
                logger.error(f"Error converting character {character.id if character else 'unknown'} to response: {e}")
                continue
        return result
    except Exception as e:
        logger.error(f"Error in get_characters endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int,
    character_service: CharacterService = Depends(get_character_service),
):
    """Get a character by ID with episodes."""
    try:
        from api.dtos import EpisodeSummaryResponse
        
        # Fetch character with episodes in one call (like locations and episodes)
        character, episodes = await character_service.get_character_with_episodes(character_id)
        
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Build episodes response
        episodes_response = None
        if episodes:
            try:
                episodes_response = [
                    EpisodeSummaryResponse(
                        id=ep.id,
                        name=ep.name,
                        air_date=ep.air_date,
                        episode=ep.episode,
                        character_count=len(ep.characters) if isinstance(ep.characters, list) else (len(ep.characters_data) if hasattr(ep, 'characters_data') and ep.characters_data else 0),
                    )
                    for ep in episodes
                ]
            except Exception as e:
                logger.warning(f"Error building episodes response for character {character_id}: {e}")
                episodes_response = []
        
        # Build response with safe field access
        try:
            # Safely access all character fields with type checking
            char_id = getattr(character, 'id', character_id)
            if not isinstance(char_id, int):
                try:
                    char_id = int(char_id) if char_id else character_id
                except (ValueError, TypeError):
                    char_id = character_id
            
            # Safely convert origin and location to dict
            origin_val = getattr(character, 'origin', {}) or {}
            if not isinstance(origin_val, dict):
                origin_val = {}
            
            location_val = getattr(character, 'location', {}) or {}
            if not isinstance(location_val, dict):
                location_val = {}
            
            # Safely convert episode to list
            episode_val = getattr(character, 'episode', []) or []
            if not isinstance(episode_val, list):
                episode_val = []
            
            return CharacterResponse(
                id=char_id,
                name=str(getattr(character, 'name', 'Unknown') or 'Unknown'),
                status=str(getattr(character, 'status', 'Unknown') or 'Unknown'),
                species=str(getattr(character, 'species', 'Unknown') or 'Unknown'),
                type=str(getattr(character, 'type', '') or ''),
                gender=str(getattr(character, 'gender', 'Unknown') or 'Unknown'),
                origin=origin_val,
                location=location_val,
                image=str(getattr(character, 'image', '') or ''),
                episode=episode_val,
                episodes=episodes_response,
                url=str(getattr(character, 'url', '') or ''),
                created=str(getattr(character, 'created', '') or ''),
            )
        except Exception as e:
            logger.error(f"Error building CharacterResponse for character {character_id}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to build response: {str(e)}")
            
    except ValueError as e:
        logger.error(f"Character {character_id} error: {e}")
        raise HTTPException(status_code=404 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Error fetching character {character_id}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{character_id}/notes", response_model=list[NoteResponse])
async def get_character_notes(
    character_id: int,
    character_service: CharacterService = Depends(get_character_service),
):
    """Get notes for a character."""
    try:
        # Use unified notes if available
        if hasattr(character_service, 'get_character_with_unified_notes'):
            _, notes = await character_service.get_character_with_unified_notes(character_id)
        else:
            _, notes = await character_service.get_character_with_notes(character_id)
        
        return [
            NoteResponse(
                id=note.id,
                subject_type=note.subject_type if hasattr(note, 'subject_type') else 'character',
                subject_id=note.subject_id if hasattr(note, 'subject_id') else note.character_id,
                note_text=note.note_text,
                created_at=note.created_at.isoformat(),
            )
            for note in notes
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{character_id}/episodes", response_model=list)
async def get_character_episodes(
    character_id: int,
    character_service: CharacterService = Depends(get_character_service),
):
    """Get episodes for a character."""
    try:
        from api.dtos import EpisodeSummaryResponse
        
        episodes = await character_service.get_character_episodes(character_id)
        return [
            EpisodeSummaryResponse(
                id=ep.id,
                name=ep.name,
                air_date=ep.air_date,
                episode=ep.episode,
                character_count=len(ep.characters) if isinstance(ep.characters, list) else (len(ep.characters_data) if hasattr(ep, 'characters_data') and ep.characters_data else 0),
            )
            for ep in episodes
        ]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{character_id}/notes", response_model=NoteResponse)
async def add_character_note(
    character_id: int,
    request: AddNoteRequest,
    character_service: CharacterService = Depends(get_character_service),
):
    """Add a note to a character."""
    try:
        note = await character_service.add_note(character_id, request.note_text)
        
        # Rebuild search index after adding note
        from api.deps import get_generation_service
        generation_service = get_generation_service()
        await generation_service.rebuild_search_index("character", str(character_id))
        
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
        import traceback
        from shared.logging import logger
        logger.error(f"Error adding note: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_character_note(
    note_id: int,
    request: AddNoteRequest,
    character_service: CharacterService = Depends(get_character_service),
):
    """Update a note."""
    try:
        note = await character_service.update_note(note_id, request.note_text)
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
        import traceback
        from shared.logging import logger
        logger.error(f"Error updating note: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/notes/{note_id}")
async def delete_character_note(
    note_id: int,
    character_service: CharacterService = Depends(get_character_service),
):
    """Delete a note."""
    try:
        await character_service.delete_note(note_id)
        return {"message": "Note deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        from shared.logging import logger
        logger.error(f"Error deleting note: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

