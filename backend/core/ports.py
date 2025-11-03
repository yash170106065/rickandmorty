"""Protocols defining interfaces for infrastructure dependencies."""
from typing import Protocol, Any
from core.models import (
    Character,
    Location,
    Episode,
    Note,
    GeneratedContent,
    EvaluationResult,
    SearchResult,
)


class RickAndMortyClient(Protocol):
    """Interface for Rick & Morty API client."""
    
    async def get_locations(self) -> list[Location]:
        """Fetch all locations with residents."""
        ...
    
    async def get_location(self, location_id: int) -> Location:
        """Fetch a specific location by ID."""
        ...
    
    async def get_character(self, character_id: int) -> Character:
        """Fetch a specific character by ID."""
        ...
    
    async def get_characters(self, character_ids: list[int]) -> list[Character]:
        """Fetch multiple characters by IDs."""
        ...
    
    async def get_all_characters(self) -> list[Character]:
        """Fetch all characters."""
        ...
    
    async def get_episodes(self) -> list[Episode]:
        """Fetch all episodes."""
        ...
    
    async def get_episode(self, episode_id: int) -> Episode:
        """Fetch a specific episode by ID."""
        ...
    
    async def get_episodes_by_ids(self, episode_ids: list[int]) -> list[Episode]:
        """Fetch multiple episodes by IDs."""
        ...


class NoteRepository(Protocol):
    """Interface for unified note persistence (characters, locations, episodes)."""
    
    async def get_notes(self, subject_type: str, subject_id: int) -> list[Note]:
        """Get all notes for a subject (character, location, or episode)."""
        ...
    
    async def add_note(self, subject_type: str, subject_id: int, note_text: str) -> Note:
        """Add a note to a subject (character, location, or episode)."""
        ...
    
    async def update_note(self, note_id: int, note_text: str) -> Note:
        """Update a note by ID."""
        ...
    
    async def delete_note(self, note_id: int) -> None:
        """Delete a note by ID."""
        ...


class CharacterRepository(Protocol):
    """Interface for character note persistence (legacy - kept for backward compatibility)."""
    
    async def get_notes(self, character_id: int) -> list[Note]:
        """Get all notes for a character."""
        ...
    
    async def add_note(self, character_id: int, note_text: str) -> Note:
        """Add a note to a character."""
        ...


class GeneratedContentRepository(Protocol):
    """Interface for generated content persistence."""
    
    async def save(self, content: GeneratedContent) -> GeneratedContent:
        """Save generated content."""
        ...
    
    async def get_by_subject(
        self, subject_id: int, prompt_type: str
    ) -> list[GeneratedContent]:
        """Get generated content for a subject."""
        ...
    
    async def get_latest_by_subject(
        self, subject_id: int, prompt_type: str
    ) -> GeneratedContent | None:
        """Get the most recent generated content for a subject."""
        ...
    
    async def update_scores(
        self,
        content_id: int,
        factual_score: float,
        completeness_score: float,
        creativity_score: float,
        relevance_score: float,
    ) -> None:
        """Update evaluation scores for existing content."""
        ...


class LLMProvider(Protocol):
    """Interface for LLM interactions."""
    
    async def generate(
        self, prompt: str, system_prompt: str | None = None
    ) -> str:
        """Generate text from a prompt."""
        ...
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text."""
        ...


class EvaluationProvider(Protocol):
    """Interface for content evaluation."""
    
    def evaluate(
        self,
        generated_text: str,
        factual_context: dict[str, Any],
    ) -> EvaluationResult:
        """Evaluate generated text."""
        ...


class VectorStore(Protocol):
    """Interface for vector storage and search."""
    
    async def upsert_character(
        self, character: Character, embedding: list[float]
    ) -> None:
        """Store character with embedding."""
        ...
    
    async def search(
        self, query_embedding: list[float], limit: int = 10
    ) -> list[SearchResult]:
        """Search for similar characters."""
        ...

