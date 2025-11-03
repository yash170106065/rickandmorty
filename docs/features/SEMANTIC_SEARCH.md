# Semantic Search Feature

Complete guide to the semantic search functionality using vector embeddings.

## Overview

Semantic Search allows users to find characters, locations, and episodes using natural language queries. Powered by vector embeddings and cosine similarity.

## How It Works

### 1. Embedding Generation
- User query converted to embedding vector (1536 dimensions)
- Uses OpenAI's `text-embedding-3-small` model
- Same model used for indexing

### 2. Vector Search
- Query embedding compared against stored embeddings
- Cosine similarity calculated for all entities
- Results sorted by similarity score

### 3. Unified Search Index
Searches across:
- **Canonical Data**: Names, species, status, etc.
- **User Notes**: All notes attached to entities
- **AI Summaries**: Generated summaries (if available)

### 4. Result Ranking
- Similarity score (0.0 - 1.0)
- Displayed as percentage
- Sorted highest to lowest

## Features

### Natural Language Queries
Search using:
- Descriptions: "genius scientist"
- Relationships: "morty's grandpa"
- Traits: "characters who can travel dimensions"
- Locations: "characters from Earth"
- Concepts: "characters who died"

### Unified Results
- Characters, locations, and episodes in same results
- Type badges for easy identification
- Snippet preview from matched content

### Real-Time Search
- Debounced input (300ms delay)
- Search triggered after 3+ characters
- Dropdown results
- Loading states

### Search Integration
- Navbar search bar
- Global search accessible from all pages
- Navigate directly to entities

## API Endpoint

```http
GET /v1/search?q={query}&limit=10
```

**Example:**
```http
GET /v1/search?q=genius scientist with portal gun&limit=10
```

**Response:**
```json
[
  {
    "entity_type": "character",
    "entity_id": "1",
    "name": "Rick Sanchez",
    "snippet": "Rick is a genius scientist...",
    "similarity": 0.92
  },
  {
    "entity_type": "location",
    "entity_id": "1",
    "name": "Earth (C-137)",
    "snippet": "Home of Rick Sanchez, a brilliant...",
    "similarity": 0.78
  }
]
```

## Technical Implementation

### Index Structure
```sql
CREATE TABLE search_index (
    entity_type TEXT NOT NULL,    -- 'character' | 'location' | 'episode'
    entity_id TEXT NOT NULL,
    text_blob TEXT NOT NULL,       -- Searchable text content
    embedding_vector TEXT NOT NULL, -- JSON array of floats
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_type, entity_id)
);
```

### Text Blob Composition
For each entity, `text_blob` contains:
1. **Canonical Data**:
   - Entity name
   - Metadata (species, status, type, etc.)
   - Relationships
2. **User Notes** (up to 5 most recent)
3. **AI Summary** (if available and scored)

### Search Algorithm
```python
async def semantic_search(query: str, limit: int = 10):
    # 1. Generate query embedding
    query_embedding = await llm_provider.get_embedding(query)
    
    # 2. Fetch all indexed entities
    all_entries = await search_index_repo.get_all()
    
    # 3. Calculate similarities
    results = []
    for entry in all_entries:
        entry_embedding = json.loads(entry.embedding_vector)
        similarity = cosine_similarity(query_embedding, entry_embedding)
        
        results.append({
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "name": extract_name(entry.text_blob),
            "snippet": extract_snippet(entry.text_blob, query),
            "similarity": similarity
        })
    
    # 4. Sort and return top results
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:limit]
```

### Index Updates
Index is automatically updated when:
- Entity data changes
- New note added
- AI summary generated/updated
- Manual rebuild triggered

## User Interface

### Search Bar
- Located in navbar (all pages except homepage)
- Real-time dropdown results
- Search icon on right
- Clear button when typing
- Loading indicator

### Search Results
- Entity name with image/icon
- Type badge (character/location/episode)
- Snippet preview
- Similarity percentage
- Click to navigate

### Search Page (Future)
- Full-page search results
- Filters and sorting
- Search history
- Saved searches

## Usage Examples

### Find Character by Description
```
Query: "morty's grandpa who is a scientist"
Result: Rick Sanchez (92% match)
```

### Find Location
```
Query: "dimension where rick and morty live"
Result: Earth (C-137) (87% match)
```

### Find by Concept
```
Query: "characters who can travel dimensions"
Result: Rick Sanchez, Rick variants (89% match)
```

## Performance

### Current Implementation (SQLite)
- **Speed**: ~100ms for 1K entities
- **Scale**: Good up to ~10K entities
- **Limitation**: Full table scan (O(n))

### Production Optimization (See FUTURE_IMPROVEMENTS.md)
- PostgreSQL + pgvector: ~5-10ms for 1M entities
- HNSW indexes for approximate nearest neighbor
- Distributed search for very large datasets

## Setup Requirements

### Initial Seeding
```bash
cd backend
python scripts/seed_embeddings.py
```

This script:
1. Fetches all characters/locations/episodes
2. Builds text blobs
3. Generates embeddings (OpenAI API)
4. Stores in search_index table

**Cost**: ~$0.10-0.50 depending on entity count
**Time**: 5-15 minutes

### Automatic Updates
- Index updates automatically when:
  - Notes added/updated
  - Summaries generated
  - Entity data refreshed

## Best Practices

1. **Query Clarity**: More specific queries = better results
2. **Note Quality**: Better notes improve search relevance
3. **Summary Integration**: AI summaries enhance searchability
4. **Index Maintenance**: Rebuild index periodically for accuracy

## Limitations

1. **Language**: Currently English only
2. **Context**: Searches current data only (no historical)
3. **Scale**: Performance degrades with > 10K entities
4. **Typo Tolerance**: Limited (semantic, not fuzzy)

## Future Enhancements

- **Faceted Search**: Filter by type, status, species
- **Autocomplete**: Search suggestions
- **Fuzzy Matching**: Handle typos
- **Multi-language**: Support other languages
- **Advanced Filters**: Date ranges, relationships
- **Search Analytics**: Track popular queries

