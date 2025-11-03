"""Character service."""
from core.models import Character, Note
from core.ports import RickAndMortyClient, CharacterRepository, NoteRepository


class CharacterService:
    """Service for character operations."""
    
    def __init__(
        self,
        api_client: RickAndMortyClient,
        note_repository: CharacterRepository,
        unified_note_repository: NoteRepository | None = None,
    ):
        self.api_client = api_client
        self.note_repository = note_repository
        self.unified_note_repository = unified_note_repository
    
    async def get_character(self, character_id: int) -> Character:
        """Get character by ID."""
        return await self.api_client.get_character(character_id)
    
    async def get_character_with_episodes(self, character_id: int) -> tuple[Character, list]:
        """Get character with populated episode objects."""
        character = await self.get_character(character_id)
        # Check if episodes_data is already populated from GraphQL query
        if character.episodes_data:
            return character, character.episodes_data
        # Otherwise, fetch episodes separately
        episodes = await self.get_character_episodes(character_id)
        return character, episodes
    
    async def get_all_characters(self) -> list[Character]:
        """Get all characters."""
        return await self.api_client.get_all_characters()
    
    async def get_characters_paginated(self, page: int, limit: int) -> tuple[list[Character], int]:
        """Get paginated characters."""
        # GraphQL API returns 20 items per page by default
        # Calculate which GraphQL page we need
        graphql_page = ((page - 1) * limit) // 20 + 1
        start_offset = ((page - 1) * limit) % 20
        
        # Try to use page-specific method if available (more efficient)
        if hasattr(self.api_client, 'get_characters_page'):
            try:
                characters, total_count = await self.api_client.get_characters_page(graphql_page)
                # If we need a subset from this page
                if start_offset > 0 or limit < 20:
                    end_offset = start_offset + limit
                    paginated = characters[start_offset:end_offset]
                    return paginated, total_count
                return characters, total_count
            except AttributeError:
                pass
        
        # Fallback: fetch all and paginate in memory
        all_characters = await self.api_client.get_all_characters()
        total = len(all_characters)
        start = (page - 1) * limit
        end = start + limit
        paginated = all_characters[start:end]
        return paginated, total
    
    async def get_character_with_notes(
        self, character_id: int
    ) -> tuple[Character, list[Note]]:
        """Get character with associated notes (legacy method)."""
        character = await self.get_character(character_id)
        notes = await self.note_repository.get_notes(character_id)
        # Legacy notes already have character_id, convert to unified format
        unified_notes = [
            Note(
                id=note.id,
                subject_type="character",
                subject_id=note.subject_id,  # Already converted in repository
                note_text=note.note_text,
                created_at=note.created_at,
            )
            for note in notes
        ]
        return character, unified_notes
    
    async def get_character_episodes(self, character_id: int) -> list:
        """Get episodes for a character."""
        character = await self.get_character(character_id)
        
        # Extract episode IDs from episode URLs
        episode_ids = []
        for ep_url in character.episode:
            try:
                # URLs are like "https://rickandmortyapi.com/api/episode/1"
                ep_id = int(ep_url.split("/")[-1])
                episode_ids.append(ep_id)
            except (ValueError, IndexError):
                continue
        
        if not episode_ids:
            return []
        
        # Use the API client to fetch episodes by IDs
        from core.models import Episode
        episodes = await self.api_client.get_episodes_by_ids(episode_ids)
        return episodes
    
    async def add_note(self, character_id: int, note_text: str) -> Note:
        """Add a note to a character."""
        # Verify character exists
        await self.api_client.get_character(character_id)
        # Use unified note repository if available, otherwise fall back to legacy
        if self.unified_note_repository:
            return await self.unified_note_repository.add_note("character", character_id, note_text)
        return await self.note_repository.add_note(character_id, note_text)
    
    async def get_character_with_unified_notes(self, character_id: int) -> tuple[Character, list[Note]]:
        """Get character with notes from unified repository."""
        character = await self.get_character(character_id)
        notes = []
        if self.unified_note_repository:
            notes = await self.unified_note_repository.get_notes("character", character_id)
        return character, notes
    
    async def update_note(self, note_id: int, note_text: str) -> Note:
        """Update a note."""
        if not self.unified_note_repository:
            raise ValueError("Note repository not available")
        return await self.unified_note_repository.update_note(note_id, note_text)
    
    async def delete_note(self, note_id: int) -> None:
        """Delete a note."""
        if not self.unified_note_repository:
            raise ValueError("Note repository not available")
        await self.unified_note_repository.delete_note(note_id)

