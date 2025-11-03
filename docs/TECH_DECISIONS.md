# Technical Decisions & Architecture

This document outlines the architectural approach, design patterns, and technical implementation decisions for the Rick & Morty AI Universe Explorer.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Patterns](#design-patterns)
3. [Directory Structure](#directory-structure)
4. [Technology Stack](#technology-stack)
5. [Implementation Details](#implementation-details)
6. [Code Organization Principles](#code-organization-principles)

## Architecture Overview

### Hexagonal Architecture (Ports & Adapters)

The project follows **hexagonal architecture** (also known as ports and adapters), which provides:

- **Clear separation** between business logic and infrastructure
- **Testability** through dependency injection
- **Flexibility** to swap implementations without changing core logic
- **Independence** from frameworks and external services

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Core Domain (Business Logic)              │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │  Models   │  │  Services  │  │   Ports    │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Adapters (External Implementations)          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │   API      │  │    DB      │  │    LLM     │     │  │
│  │  │  Client    │  │ Repository │  │  Provider  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

#### 1. API Layer (`backend/api/`)
- **Purpose**: HTTP interface, request/response handling
- **Responsibilities**:
  - Route definitions
  - Request validation
  - Response serialization
  - HTTP status mapping
- **Rules**: NO business logic, only HTTP concerns

#### 2. Core Domain Layer (`backend/core/`)
- **Purpose**: Pure business logic
- **Responsibilities**:
  - Domain models (entities)
  - Business services (use cases)
  - Protocol definitions (interfaces)
- **Rules**: 
  - NO imports from `api` or `infrastructure`
  - NO framework dependencies (FastAPI, SQLAlchemy, etc.)
  - Pure Python, testable in isolation

#### 3. Infrastructure Layer (`backend/infrastructure/`)
- **Purpose**: External integrations
- **Responsibilities**:
  - Database repositories (SQLite)
  - API clients (GraphQL)
  - LLM providers (OpenAI)
  - Vector stores
  - Evaluation logic
- **Rules**:
  - Implements protocols from `core/ports`
  - NO business rules
  - Handles I/O, network, file system

#### 4. Shared Layer (`backend/shared/`)
- **Purpose**: Cross-cutting utilities
- **Responsibilities**:
  - Configuration
  - Logging
  - Error types
  - Constants
- **Rules**: Can be imported anywhere, but cannot import back

## Design Patterns

### 1. Service Pattern

Each business use case is implemented as a service method:

```python
# Example: CharacterService
class CharacterService:
    def __init__(self, api_client, repository, note_repository):
        self.api_client = api_client
        self.repository = repository
        self.note_repository = note_repository
    
    async def get_character_with_notes(self, character_id: int) -> Character:
        # Business logic here
        character = await self.api_client.get_character(character_id)
        notes = await self.note_repository.get_notes('character', character_id)
        # ...
        return character_with_notes
```

**Benefits:**
- Single responsibility per service
- Easy to test
- Clear business logic flow

### 2. Repository Pattern

Data access is abstracted through repositories:

```python
# Protocol (Port)
class NoteRepository(Protocol):
    async def get_notes(self, subject_type: str, subject_id: int) -> list[Note]: ...
    async def add_note(self, subject_type: str, subject_id: int, text: str) -> Note: ...

# Implementation (Adapter)
class SQLiteNoteRepository(NoteRepository):
    async def get_notes(self, subject_type: str, subject_id: int) -> list[Note]:
        # SQLite-specific implementation
        ...
```

**Benefits:**
- Easy to swap database implementations
- Core logic doesn't know about SQL
- Testable with mock repositories

### 3. Dependency Injection

Dependencies are injected at composition time:

```python
# api/deps.py
def get_generation_service() -> GenerationService:
    return GenerationService(
        api_client=get_api_client(),
        llm_provider=get_llm_provider(),
        evaluator=get_evaluator(),
        content_repository=get_content_repository()
    )

# api/routers/generation.py
@router.post("/location-summary/{location_id}")
async def generate_location_summary(
    location_id: int,
    service: GenerationService = Depends(get_generation_service)
):
    return await service.generate_location_summary(location_id)
```

**Benefits:**
- Loose coupling
- Easy testing (inject mocks)
- Centralized dependency management

### 4. Async Job Queue Pattern

Long-running operations (like evaluation) are queued for async processing:

```python
# Generate summary (fast, returns immediately)
content = await service.generate_location_summary(location_id)

# Queue evaluation job (async)
job_queue.enqueue({
    "type": "SCORE_GENERATED_CONTENT",
    "content_id": content.id,
    "generated_text": content.output_text,
    "factual_context": context
})

# Job processor (runs in background)
async def process_job(job):
    if job["type"] == "SCORE_GENERATED_CONTENT":
        evaluation = evaluator.evaluate(...)
        await repository.update_scores(...)
```

**Benefits:**
- Non-blocking API responses
- Better user experience
- Scales to handle heavy workloads

## Directory Structure

### Backend Structure

```
backend/
├── api/                          # FastAPI application layer
│   ├── routers/                  # Route handlers
│   │   ├── characters.py
│   │   ├── locations.py
│   │   ├── episodes.py
│   │   ├── generation.py
│   │   └── search.py
│   ├── dtos.py                   # Request/Response models
│   └── deps.py                   # Dependency injection
│
├── core/                         # Domain logic (business layer)
│   ├── models.py                 # Domain entities
│   ├── ports.py                  # Protocol definitions (interfaces)
│   └── services/                 # Business services
│       ├── character_service.py
│       ├── location_service.py
│       ├── episode_service.py
│       ├── generation_service.py
│       └── search_service.py
│
├── infrastructure/                # External integrations
│   ├── api/                      # External API clients
│   │   ├── graphql_client.py     # Rick & Morty GraphQL client
│   │   └── rick_and_morty_client.py
│   ├── db/                       # Database
│   │   ├── schema.sql            # Database schema
│   │   └── migrations/           # SQL migrations
│   ├── repositories/             # Data access implementations
│   │   ├── character_repository.py
│   │   ├── note_repository.py
│   │   ├── generated_content_repository.py
│   │   ├── generation_repository.py
│   │   └── search_index_repository.py
│   ├── llm/                      # LLM provider
│   │   └── openai_provider.py
│   ├── evaluation/               # Content evaluation
│   │   └── evaluator.py
│   ├── vector_store/             # Vector search
│   │   └── sqlite_vector_store.py
│   └── workers/                  # Background jobs
│       └── job_queue.py
│
├── shared/                       # Cross-cutting utilities
│   ├── config.py                 # Configuration management
│   └── logging.py                # Logging setup
│
├── scripts/                      # Utility scripts
│   ├── init_db.py                # Database initialization
│   ├── seed_embeddings.py        # Vector store seeding
│   └── verify_setup.py           # Setup verification
│
├── data/                         # Data files
│   └── app.db                    # SQLite database
│
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
└── pyproject.toml                # Project configuration
```

### Frontend Structure

```
frontend/
├── app/                          # Next.js App Router
│   ├── page.tsx                  # Landing page
│   ├── layout.tsx                # Root layout
│   ├── dashboard/                # Dashboard pages
│   │   ├── page.tsx
│   │   ├── characters/
│   │   ├── locations/
│   │   └── episodes/
│   ├── characters/[id]/          # Character detail
│   ├── locations/[id]/            # Location detail
│   ├── episodes/[id]/           # Episode detail
│   └── search/                   # Search page
│
├── components/                   # React components
│   ├── dashboard/                # Dashboard-specific
│   │   ├── DashboardContent.tsx
│   │   ├── DashboardSidebar.tsx
│   │   ├── NotesPanel.tsx
│   │   └── ...
│   ├── CharacterCard.tsx
│   ├── LocationCard.tsx
│   ├── EpisodeCard.tsx
│   ├── Navbar.tsx
│   └── ...
│
├── lib/                          # Utilities
│   └── api.ts                    # API client
│
├── globals.css                   # Global styles
└── package.json                  # Dependencies
```

## Technology Stack

### Backend Technologies

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Python** | 3.12 | Core language | Modern async support, type hints |
| **FastAPI** | 0.104.1 | Web framework | Fast, async, automatic docs |
| **SQLite** | - | Database | Zero-config, perfect for demos |
| **SQLAlchemy** | 2.0.23 | ORM | Type-safe queries, migrations |
| **gql** | 4.0.0 | GraphQL client | Efficient data fetching |
| **OpenAI** | 1.3.6 | LLM provider | Best-in-class models |
| **numpy** | 1.26.2 | Vector ops | Efficient embedding calculations |

### Frontend Technologies

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Next.js** | 14 | React framework | Server components, routing |
| **TypeScript** | 5.0 | Type safety | Catch errors early |
| **Tailwind CSS** | Latest | Styling | Fast development, consistent design |
| **React** | 18 | UI library | Component-based, hooks |

See [TRADEOFFS.md](TRADEOFFS.md) for detailed rationale behind each choice.

## Implementation Details

### Async Evaluation System

**Problem**: LLM evaluation is slow (2-5 seconds), would block API responses.

**Solution**: Two-phase generation:
1. **Phase 1** (Immediate): Generate text, save with placeholder scores (-1)
2. **Phase 2** (Async): Queue evaluation job, update scores when complete

**Implementation**:
```python
# GenerationService.generate_location_summary()
content = GeneratedContent(
    factual_score=-1.0,  # Placeholder
    # ...
)
saved = await repository.save(content)

# Queue async job
job_queue.enqueue({
    "type": "SCORE_GENERATED_CONTENT",
    "content_id": saved.id,
    # ...
})

# Frontend polls or WebSocket updates scores when ready
```

### Vector Search Implementation

**Approach**: SQLite-based vector store with cosine similarity.

**Storage**:
- Embeddings stored as JSON arrays in TEXT column
- Indexed by entity_type + entity_id

**Search**:
```python
# 1. Generate query embedding
query_embedding = await llm_provider.get_embedding(query)

# 2. Fetch all embeddings
all_embeddings = await repository.get_all_embeddings()

# 3. Calculate cosine similarity
similarities = [
    cosine_similarity(query_embedding, emb.vector)
    for emb in all_embeddings
]

# 4. Sort and return top results
```

**Limitations**: 
- Full table scan (O(n))
- Not optimized for large datasets
- See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for production solutions

### Unified Notes System

**Design**: Single `notes` table supports multiple entity types.

**Schema**:
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    subject_type TEXT NOT NULL,  -- 'character' | 'location' | 'episode'
    subject_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Benefits**:
- Single repository handles all note types
- Consistent API across entities
- Easy to extend to new entity types

### GraphQL vs REST

**Choice**: GraphQL for Rick & Morty API

**Rationale**:
- More efficient (fetch only needed fields)
- Nested queries (locations with residents)
- Single endpoint, fewer network calls

**Example**:
```graphql
query GetLocation($id: ID!) {
  location(id: $id) {
    name
    type
    dimension
    residents {
      id
      name
      species
      image
    }
  }
}
```

## Code Organization Principles

### Import Rules

```
core/          → Can import: shared/
api/           → Can import: core/, infrastructure/, shared/
infrastructure/ → Can import: core/, shared/
shared/        → Can import: (nothing)
```

**Enforcement**: These rules are enforced through code review and architecture checks.

### Naming Conventions

- **Services**: `{Entity}Service` (e.g., `CharacterService`)
- **Repositories**: `SQLite{Entity}Repository` (e.g., `SQLiteNoteRepository`)
- **Models**: PascalCase (e.g., `GeneratedContent`)
- **Functions**: `snake_case` (e.g., `get_character_with_notes`)
- **Protocols**: Descriptive names (e.g., `RickAndMortyClient`)

### Error Handling

- **Domain Errors**: Custom exceptions in `shared/`
- **API Errors**: HTTP status codes with descriptive messages
- **Logging**: All errors logged with context
- **User Feedback**: Clear error messages in frontend

### Testing Strategy

**Unit Tests**: Test `core/` services in isolation
**Integration Tests**: Test `api/` + `infrastructure/` together
**E2E Tests**: Test full user flows

*(Note: Test suite implementation is pending)*

## Future Architectural Considerations

See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for:
- Cloud queue systems (Kafka, SQS)
- Database migration paths
- Caching strategies
- Microservices breakdown

---

This architecture provides a solid foundation that's:
- ✅ Easy to understand
- ✅ Easy to test
- ✅ Easy to extend
- ✅ Ready for production scaling

