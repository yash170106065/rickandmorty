"""Dependency injection for FastAPI."""
from core.ports import (
    RickAndMortyClient,
    CharacterRepository,
    NoteRepository,
    GeneratedContentRepository,
    LLMProvider,
    EvaluationProvider,
    VectorStore,
)
from core.services import (
    LocationService,
    CharacterService,
    GenerationService,
    SearchService,
)
from infrastructure.api.graphql_client import RickAndMortyGraphQLClient
from infrastructure.repositories.character_repository import (
    SQLiteCharacterRepository,
)
from infrastructure.repositories.note_repository import (
    SQLiteNoteRepository,
)
from infrastructure.repositories.generated_content_repository import (
    SQLiteGeneratedContentRepository,
)
from infrastructure.llm.openai_provider import OpenAIProvider
from infrastructure.evaluation.evaluator import HeuristicEvaluator
from infrastructure.vector_store.sqlite_vector_store import SQLiteVectorStore


# Infrastructure instances
_api_client: RickAndMortyClient | None = None
_character_repo: CharacterRepository | None = None
_note_repo: NoteRepository | None = None
_content_repo: GeneratedContentRepository | None = None
_llm_provider: LLMProvider | None = None
_evaluator: EvaluationProvider | None = None
_vector_store: VectorStore | None = None


def get_api_client() -> RickAndMortyClient:
    """Get Rick & Morty API client (GraphQL)."""
    global _api_client
    if _api_client is None:
        _api_client = RickAndMortyGraphQLClient()
    return _api_client


def get_character_repository() -> CharacterRepository:
    """Get character repository (legacy)."""
    global _character_repo
    if _character_repo is None:
        _character_repo = SQLiteCharacterRepository()
    return _character_repo


def get_note_repository() -> NoteRepository:
    """Get unified note repository."""
    global _note_repo
    if _note_repo is None:
        _note_repo = SQLiteNoteRepository()
    return _note_repo


def get_content_repository() -> GeneratedContentRepository:
    """Get generated content repository."""
    global _content_repo
    if _content_repo is None:
        _content_repo = SQLiteGeneratedContentRepository()
    return _content_repo


def get_llm_provider() -> LLMProvider:
    """Get LLM provider."""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = OpenAIProvider()
    return _llm_provider


def get_evaluator() -> EvaluationProvider:
    """Get evaluation provider."""
    global _evaluator
    if _evaluator is None:
        _evaluator = HeuristicEvaluator()
    return _evaluator


def get_vector_store() -> VectorStore:
    """Get vector store."""
    global _vector_store
    if _vector_store is None:
        _vector_store = SQLiteVectorStore()
    return _vector_store


# Service instances
def get_location_service() -> LocationService:
    """Get location service."""
    return LocationService(get_api_client(), get_note_repository())


def get_character_service() -> CharacterService:
    """Get character service."""
    return CharacterService(
        get_api_client(),
        get_character_repository(),
        get_note_repository(),
    )


def get_generation_service() -> GenerationService:
    """Get generation service."""
    return GenerationService(
        get_api_client(),
        get_llm_provider(),
        get_evaluator(),
        get_content_repository(),
        get_note_repository(),
    )


def get_search_service() -> SearchService:
    """Get search service."""
    return SearchService(get_llm_provider())


def get_episode_service() -> "EpisodeService":
    """Get episode service."""
    from core.services.episode_service import EpisodeService
    return EpisodeService(get_api_client(), get_note_repository())

