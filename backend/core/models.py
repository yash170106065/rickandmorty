"""Domain models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Location:
    """Location domain model."""
    id: int
    name: str
    type: str
    dimension: str
    residents: list["Character"]


@dataclass
class Character:
    """Character domain model."""
    id: int
    name: str
    status: str
    species: str
    type: str
    gender: str
    origin: dict[str, Any]
    location: dict[str, Any]
    image: str
    episode: list[str]  # URLs or episode codes
    episodes_data: list["Episode"] | None = None  # Full episode objects when available
    url: str = ""
    created: str = ""


@dataclass
class Note:
    """Note domain model - supports characters, locations, and episodes."""
    id: int
    subject_type: str  # 'character', 'location', or 'episode'
    subject_id: int
    note_text: str
    created_at: datetime


@dataclass
class EvaluationResult:
    """Evaluation result for generated content."""
    factual_score: float  # 0.0-1.0 - Factual accuracy and consistency
    completeness_score: float  # 0.0-1.0 - Coverage of available information
    creativity_score: float  # 0.0-1.0 - Narrative quality and style
    relevance_score: float  # 0.0-1.0 - Relevance and focus on the entity


@dataclass
class GeneratedContent:
    """Generated content with evaluation."""
    id: int
    subject_id: int
    prompt_type: str
    output_text: str
    factual_score: float
    completeness_score: float
    creativity_score: float
    relevance_score: float
    context_json: dict[str, Any]
    created_at: datetime


@dataclass
class Episode:
    """Episode domain model."""
    id: int
    name: str
    air_date: str
    episode: str
    characters: list[str]  # URLs or IDs
    characters_data: list["Character"] | None = None  # Full character objects when available
    url: str = ""
    created: str = ""


@dataclass
class SearchResult:
    """Semantic search result."""
    character: Character
    similarity_score: float


@dataclass
class Generation:
    """Generation with async scoring support."""
    generation_id: str
    entity_type: str  # "character" | "location" | "episode"
    entity_id: str
    summary_text: str
    factual_score: float | None
    creativity_score: float | None
    completeness_score: float | None
    relevance_score: float | None
    scores_status: str  # "INITIATED" | "GENERATED"
    created_at: datetime
    updated_at: datetime

