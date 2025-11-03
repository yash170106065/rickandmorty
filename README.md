# ⚡ Rick & Morty AI Universe Explorer

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

An AI-powered exploration platform for the Rick & Morty universe featuring semantic search, intelligent content generation with quality evaluation, and comprehensive note-taking capabilities.

## 🎬 Demo

**Watch the full demo video:** [https://www.loom.com/share/d5dfe2cc971f4ad7b3af74a0a1059d15](https://www.loom.com/share/d5dfe2cc971f4ad7b3af74a0a1059d15)

The demo showcases all features including semantic search, AI generation with quality evaluation, and comprehensive note-taking capabilities.

## ✨ Features

### 🗺️ **Location Exploration**
Browse through all dimensions, planets, and locations in the Rick & Morty multiverse. View detailed information including residents, dimensions, and types.

**Key Capabilities:**
- Paginated location browsing
- Resident listings with character details
- AI-powered location summaries with quality scoring
- Location-specific notes and annotations

[📖 Learn more about Locations feature](docs/features/LOCATIONS.md)

### 👽 **Character Discovery**
Explore 800+ characters from the Rick & Morty universe with comprehensive profiles, episode appearances, and relationships.

**Key Capabilities:**
- Detailed character profiles with images
- Episode appearance tracking
- Character-to-character relationships
- AI-generated character summaries
- Semantic character search
- Personal notes and annotations

[📖 Learn more about Characters feature](docs/features/CHARACTERS.md)

### 🎬 **Episode Journey**
Navigate through all episodes with detailed information about plots, characters, and air dates.

**Key Capabilities:**
- Complete episode catalog
- Character appearance tracking
- Episode summaries with AI insights
- Episode-specific notes

[📖 Learn more about Episodes feature](docs/features/EPISODES.md)

### 🤖 **AI-Powered Content Generation**
Generate contextual summaries, dialogues, and insights with built-in quality evaluation scoring.

**Key Capabilities:**
- **Location Summaries**: AI-generated descriptions in Rick & Morty narrator style
- **Character Summaries**: Personality insights and memorable moments
- **Episode Summaries**: Plot summaries with character interactions
- **Quality Scoring**: Every generation is evaluated on:
  - **Factual Accuracy** (0-1): Consistency with canonical data
  - **Completeness** (0-1): Coverage of available information
  - **Creativity** (0-1): Narrative quality and style
  - **Relevance** (0-1): Focus on the entity being described

**Technical Implementation:**
- Async scoring jobs for non-blocking generation
- Context-aware prompt engineering
- Multi-metric evaluation system
- Automatic search index updates

[📖 Learn more about AI Generation](docs/features/AI_GENERATION.md)

### 🔍 **Semantic Search**
Find characters, locations, and episodes using natural language queries. Powered by vector embeddings and cosine similarity.

**Key Capabilities:**
- Natural language query processing
- Unified search across characters, locations, and episodes
- Relevance scoring with similarity metrics
- Search results with snippets and context
- Real-time search with debouncing

**Search Features:**
- Search across notes and AI summaries
- Context-aware results
- Type-based filtering
- Similarity percentage display

[📖 Learn more about Semantic Search](docs/features/SEMANTIC_SEARCH.md)

### 📝 **Smart Notes System**
Add, edit, and organize notes for any entity in the Rick & Morty universe.

**Key Capabilities:**
- Unified notes across characters, locations, and episodes
- AI-powered note regeneration and enhancement
- Note history and timestamps
- Full CRUD operations (Create, Read, Update, Delete)
- Searchable notes integrated into semantic search

[📖 Learn more about Notes System](docs/features/NOTES.md)

## 🏗️ Architecture

This project follows a **hexagonal architecture** (ports and adapters) with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Dashboard  │  │   Search     │  │    Pages     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/REST
┌─────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Routers    │  │     DTOs    │  │    Deps      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ Protocol Interfaces
┌─────────────────────────────────────────────────────────┐
│               Core Domain Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Services   │  │    Models    │  │    Ports     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          ↕ Implementations
┌─────────────────────────────────────────────────────────┐
│          Infrastructure Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ GraphQL API  │  │  Repositories │  │ LLM Provider│  │
│  │  Client      │  │   (SQLite)    │  │   (OpenAI)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Evaluator   │  │ Vector Store │  │  Job Queue   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

[📖 Detailed Architecture Documentation](docs/TECH_DECISIONS.md)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- OpenAI API Key

### Installation

   ```bash
# Clone the repository
git clone <repository-url>
cd rickandmorty

# Use the Makefile for quick setup
make setup
```

**Or follow the [detailed setup guide](docs/LOCAL_SETUP.md) for step-by-step instructions.**

### Running the Application

   ```bash
# Terminal 1: Start backend
make run-backend

# Terminal 2: Start frontend  
make run-frontend
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📚 Documentation

### Core Documentation
- **[Local Setup Guide](docs/LOCAL_SETUP.md)** - Detailed installation and configuration
- **[Technical Decisions](docs/TECH_DECISIONS.md)** - Architecture, design patterns, and implementation details
- **[Tradeoffs Analysis](docs/TRADEOFFS.md)** - Decision rationale for technologies and approaches
- **[Future Improvements](docs/FUTURE_IMPROVEMENTS.md)** - Scalability plans and enhancement roadmap

### Feature Documentation
- **[Locations Feature](docs/features/LOCATIONS.md)**
- **[Characters Feature](docs/features/CHARACTERS.md)**
- **[Episodes Feature](docs/features/EPISODES.md)**
- **[AI Generation Feature](docs/features/AI_GENERATION.md)**
- **[Semantic Search Feature](docs/features/SEMANTIC_SEARCH.md)**
- **[Notes System Feature](docs/features/NOTES.md)**

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.12
- **Database**: SQLite (with SQLAlchemy)
- **API Client**: GraphQL (gql 4.0.0) for Rick & Morty API
- **LLM**: OpenAI (GPT-4, text-embedding-3-small)
- **Vector Store**: SQLite-based custom implementation
- **Job Queue**: In-memory async job processing

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript 5.0
- **Styling**: Tailwind CSS
- **State Management**: React Hooks
- **API Client**: Custom fetch-based client

[📖 See Tradeoffs Documentation](docs/TRADEOFFS.md) for technology selection rationale.

## 📁 Project Structure

```
rickandmorty/
├── backend/                 # Python FastAPI backend
│   ├── api/                # FastAPI routers and DTOs
│   ├── core/               # Domain logic (services, models, ports)
│   ├── infrastructure/     # External integrations (DB, LLM, API clients)
│   ├── shared/             # Cross-cutting utilities
│   ├── scripts/            # Database and seeding scripts
│   └── data/               # SQLite database files
├── frontend/               # Next.js frontend
│   ├── app/                # Next.js app router pages
│   ├── components/         # React components
│   └── lib/                # Utilities and API client
├── docs/                   # Documentation files
│   ├── features/           # Feature-specific documentation
│   └── demo/               # Demo screenshots and videos
└── README.md              # This file
```

[📖 Detailed Directory Structure](docs/TECH_DECISIONS.md#directory-structure)

## 🔑 Key Features in Detail

### Async Evaluation System
AI-generated content is scored asynchronously to provide immediate feedback while ensuring thorough quality analysis. Scores are updated in real-time as evaluation completes.

### Unified Search Index
Semantic search works across all entity types by maintaining a unified search index that combines:
- Canonical API data
- User notes
- AI-generated summaries

### Evaluation Metrics
Every AI generation includes four evaluation dimensions:
1. **Factual Score**: Validates consistency with source data
2. **Completeness Score**: Measures information coverage
3. **Creativity Score**: Assesses narrative quality (LLM-judged)
4. **Relevance Score**: Ensures focus on the target entity

## 🧪 Testing

   ```bash
# Run backend tests
   cd backend
pytest

# Run frontend tests  
cd frontend
npm test
```

## 🚀 Deployment

### Environment Variables

**Backend (.env):**
```env
OPENAI_API_KEY=your_openai_key
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
API_HOST=0.0.0.0
API_PORT=8000
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 🙏 Acknowledgments

- [Rick and Morty API](https://rickandmortyapi.com/) for providing the GraphQL API
- OpenAI for language models and embeddings
- FastAPI and Next.js communities

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Built with ⚡ for exploring the infinite dimensions of Rick & Morty**
