"""Location service."""
from core.models import Location, Note
from core.ports import RickAndMortyClient, NoteRepository


class LocationService:
    """Service for location operations."""
    
    def __init__(self, api_client: RickAndMortyClient, note_repository: NoteRepository | None = None):
        self.api_client = api_client
        self.note_repository = note_repository
    
    async def get_locations(self) -> list[Location]:
        """Get all locations with residents."""
        return await self.api_client.get_locations()
    
    async def get_locations_paginated(self, page: int, limit: int) -> tuple[list[Location], int]:
        """Get paginated locations with residents."""
        # GraphQL API returns 20 items per page by default
        # Calculate which GraphQL page we need
        graphql_page = ((page - 1) * limit) // 20 + 1
        start_offset = ((page - 1) * limit) % 20
        
        # Try to use page-specific method if available (more efficient)
        if hasattr(self.api_client, 'get_locations_page'):
            try:
                locations, total_count = await self.api_client.get_locations_page(graphql_page)
                # If we need a subset from this page
                if start_offset > 0 or limit < 20:
                    end_offset = start_offset + limit
                    paginated = locations[start_offset:end_offset]
                    return paginated, total_count
                return locations, total_count
            except AttributeError:
                pass
        
        # Fallback: fetch all and paginate in memory
        all_locations = await self.api_client.get_locations()
        total = len(all_locations)
        start = (page - 1) * limit
        end = start + limit
        paginated = all_locations[start:end]
        return paginated, total
    
    async def get_location(self, location_id: int) -> Location:
        """Get a specific location by ID."""
        return await self.api_client.get_location(location_id)
    
    async def get_location_with_notes(self, location_id: int) -> tuple[Location, list[Note]]:
        """Get location with associated notes."""
        location = await self.get_location(location_id)
        notes = []
        if self.note_repository:
            notes = await self.note_repository.get_notes("location", location_id)
        return location, notes
    
    async def add_note(self, location_id: int, note_text: str) -> Note:
        """Add a note to a location."""
        if not self.note_repository:
            raise ValueError("Note repository not available")
        # Verify location exists
        await self.api_client.get_location(location_id)
        return await self.note_repository.add_note("location", location_id, note_text)
    
    async def update_note(self, note_id: int, note_text: str) -> Note:
        """Update a note."""
        if not self.note_repository:
            raise ValueError("Note repository not available")
        return await self.note_repository.update_note(note_id, note_text)
    
    async def delete_note(self, note_id: int) -> None:
        """Delete a note."""
        if not self.note_repository:
            raise ValueError("Note repository not available")
        await self.note_repository.delete_note(note_id)

