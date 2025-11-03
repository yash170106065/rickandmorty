"""Data Transfer Objects for API."""
from pydantic import BaseModel
from typing import Any


class CharacterResponse(BaseModel):
    """Character API response."""
    id: int
    name: str
    status: str
    species: str
    type: str
    gender: str
    origin: dict[str, Any]
    location: dict[str, Any]
    image: str
    episode: list[str]
    episodes: list | None = None  # Optional: full episode objects when available
    url: str = ""
    created: str = ""


class NoteResponse(BaseModel):
    """Note API response."""
    id: int
    subject_type: str  # 'character', 'location', or 'episode'
    subject_id: int
    note_text: str
    created_at: str


class LocationResponse(BaseModel):
    """Location API response."""
    id: int
    name: str
    type: str
    dimension: str
    residents: list[CharacterResponse]


class ResidentResponse(BaseModel):
    """Resident (character) summary for location."""
    id: int
    name: str
    status: str
    species: str
    image: str


class LocationSummaryResponse(BaseModel):
    """Location with simplified resident list."""
    id: int
    name: str
    type: str
    dimension: str
    resident_count: int
    residents: list[ResidentResponse]


class AddNoteRequest(BaseModel):
    """Request to add a note."""
    note_text: str


class GeneratedContentResponse(BaseModel):
    """Generated content with evaluation."""
    id: int
    subject_id: int
    prompt_type: str
    output_text: str
    factual_score: float
    completeness_score: float
    creativity_score: float
    relevance_score: float
    created_at: str


class SearchResultResponse(BaseModel):
    """Search result response (legacy - character only)."""
    character: CharacterResponse
    similarity_score: float


class UnifiedSearchResultResponse(BaseModel):
    """Unified search result response (characters, locations, episodes)."""
    entity_type: str  # "character" | "location" | "episode"
    entity_id: str
    name: str
    snippet: str
    similarity: float


class EpisodeSummaryResponse(BaseModel):
    """Episode summary for list view."""
    id: int
    name: str
    air_date: str
    episode: str
    character_count: int
    characters: list[CharacterResponse] | None = None  # Optional: include characters if available


class EpisodeResponse(BaseModel):
    """Episode API response with characters."""
    id: int
    name: str
    air_date: str
    episode: str
    characters: list[CharacterResponse]


class DialogueRequest(BaseModel):
    """Request to generate dialogue."""
    character_id2: int
    topic: str = ""


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str


class GenerateSummaryRequest(BaseModel):
    """Request to generate summary."""
    entityType: str  # "character" | "location" | "episode"
    entityId: str


class GenerateSummaryResponse(BaseModel):
    """Generate summary response."""
    entityType: str
    entityId: str
    summary: str
    factualScore: float | None
    creativityScore: float | None
    completenessScore: float | None
    relevanceScore: float | None
    scoresStatus: str  # "INITIATED" | "GENERATED"


class RegenerateNoteRequest(BaseModel):
    """Request to regenerate/improve note text with AI."""
    note_text: str
    entity_type: str  # "character" | "location" | "episode"
    entity_id: int


class RegenerateNoteResponse(BaseModel):
    """Response for regenerated note text."""
    improved_text: str

