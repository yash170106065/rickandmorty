"""Location routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from api.deps import get_location_service
from api.dtos import (
    LocationSummaryResponse,
    LocationResponse,
    ResidentResponse,
    CharacterResponse,
    NoteResponse,
    AddNoteRequest,
)
from core.services import LocationService
from typing import Optional


router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationSummaryResponse])
async def get_locations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    location_service: LocationService = Depends(get_location_service),
):
    """Get paginated locations."""
    try:
        locations, total = await location_service.get_locations_paginated(page, limit)
        return [
            LocationSummaryResponse(
                id=loc.id,
                name=loc.name,
                type=loc.type,
                dimension=loc.dimension,
                resident_count=getattr(loc, '_resident_count', len(loc.residents) if loc.residents else 0),
                residents=[],  # Don't include residents in list - only when fetching single location
            )
            for loc in locations
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(
    location_id: int,
    location_service: LocationService = Depends(get_location_service),
):
    """Get a specific location."""
    try:
        location = await location_service.get_location(location_id)
        from shared.logging import logger
        
        try:
            resident_responses = [
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
                for char in location.residents
            ]
        except Exception as e:
            logger.error(f"Error converting residents to response: {e}")
            resident_responses = []
        
        return LocationResponse(
            id=location.id,
            name=location.name,
            type=location.type,
            dimension=location.dimension,
            residents=resident_responses,
        )
    except ValueError as e:
        from shared.logging import logger
        logger.error(f"Location {location_id} not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        from shared.logging import logger
        import traceback
        logger.error(f"Error fetching location {location_id}: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{location_id}/notes", response_model=list[NoteResponse])
async def get_location_notes(
    location_id: int,
    location_service: LocationService = Depends(get_location_service),
):
    """Get notes for a location."""
    try:
        _, notes = await location_service.get_location_with_notes(location_id)
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


@router.post("/{location_id}/notes", response_model=NoteResponse)
async def add_location_note(
    location_id: int,
    request: AddNoteRequest,
    location_service: LocationService = Depends(get_location_service),
):
    """Add a note to a location."""
    try:
        note = await location_service.add_note(location_id, request.note_text)
        
        # Rebuild search index after adding note
        from api.deps import get_generation_service
        generation_service = get_generation_service()
        await generation_service.rebuild_search_index("location", str(location_id))
        
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
async def update_location_note(
    note_id: int,
    request: AddNoteRequest,
    location_service: LocationService = Depends(get_location_service),
):
    """Update a note."""
    try:
        note = await location_service.update_note(note_id, request.note_text)
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
async def delete_location_note(
    note_id: int,
    location_service: LocationService = Depends(get_location_service),
):
    """Delete a note."""
    try:
        await location_service.delete_note(note_id)
        return {"message": "Note deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

