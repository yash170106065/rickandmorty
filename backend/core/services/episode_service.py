"""Episode service."""
from core.models import Episode, Note
from core.ports import RickAndMortyClient, NoteRepository


class EpisodeService:
    """Service for episode operations."""
    
    def __init__(self, api_client: RickAndMortyClient, note_repository: NoteRepository | None = None):
        self.api_client = api_client
        self.note_repository = note_repository
    
    async def get_episodes(self) -> list[Episode]:
        """Get all episodes."""
        return await self.api_client.get_episodes()
    
    async def get_episodes_paginated(self, page: int, limit: int) -> tuple[list[Episode], int]:
        """Get paginated episodes."""
        # GraphQL API returns 20 items per page by default
        # Calculate which GraphQL page we need
        graphql_page = ((page - 1) * limit) // 20 + 1
        start_offset = ((page - 1) * limit) % 20
        
        # Try to use page-specific method if available (more efficient)
        if hasattr(self.api_client, 'get_episodes_page'):
            try:
                episodes, total_count = await self.api_client.get_episodes_page(graphql_page)
                # If we need a subset from this page
                if start_offset > 0 or limit < 20:
                    end_offset = start_offset + limit
                    paginated = episodes[start_offset:end_offset]
                    return paginated, total_count
                return episodes, total_count
            except AttributeError:
                pass
        
        # Fallback: fetch all and paginate in memory
        all_episodes = await self.api_client.get_episodes()
        total = len(all_episodes)
        start = (page - 1) * limit
        end = start + limit
        paginated = all_episodes[start:end]
        return paginated, total
    
    async def get_episode(self, episode_id: int) -> Episode:
        """Get a specific episode by ID."""
        return await self.api_client.get_episode(episode_id)
    
    async def get_episode_with_characters(self, episode_id: int) -> tuple[Episode, list]:
        """Get episode with populated character objects."""
        episode = await self.get_episode(episode_id)
        
        # Extract character IDs from episode.characters (list of IDs or URLs)
        character_ids = []
        for char_ref in episode.characters:
            if isinstance(char_ref, str):
                # It's a URL, extract ID
                try:
                    char_id = int(char_ref.split("/")[-1])
                    character_ids.append(char_id)
                except (ValueError, IndexError):
                    continue
            elif isinstance(char_ref, int):
                character_ids.append(char_ref)
        
        characters = []
        if character_ids:
            characters = await self.api_client.get_characters(character_ids)
        
        return episode, characters
    
    async def get_episode_with_notes(self, episode_id: int) -> tuple[Episode, list[Note]]:
        """Get episode with associated notes."""
        episode = await self.get_episode(episode_id)
        notes = []
        if self.note_repository:
            notes = await self.note_repository.get_notes("episode", episode_id)
        return episode, notes
    
    async def add_note(self, episode_id: int, note_text: str) -> Note:
        """Add a note to an episode."""
        if not self.note_repository:
            raise ValueError("Note repository not available")
        # Verify episode exists
        await self.api_client.get_episode(episode_id)
        return await self.note_repository.add_note("episode", episode_id, note_text)
    
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

