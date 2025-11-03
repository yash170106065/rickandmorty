# Characters Feature

Complete guide to the Characters feature in Rick & Morty AI Universe Explorer.

## Overview

The Characters feature provides access to 800+ characters from the Rick & Morty universe, with detailed profiles, episode appearances, relationships, and AI-powered insights.

## Features

### Character Discovery
- **Browse All**: Paginated list of all characters
- **Grid View**: Visual character cards with images
- **Search**: Semantic search to find characters by description
- **Filter**: Filter by status, species (future)

### Character Profiles
Each character profile includes:
- **Basic Info**: Name, status, species, type, gender
- **Visual**: Character image/avatar
- **Origin**: Place of origin (location)
- **Location**: Current/last known location
- **Episodes**: List of episodes character appeared in
- **Relationships**: Connections to other characters

### AI-Powered Summaries
- **Character Summary**: AI-generated character descriptions
- **Personality Insights**: Character traits and memorable moments
- **Evaluation Metrics**: Quality scores for generated content
- **Style**: Written in Rick & Morty narrator tone

### Notes & Annotations
- **Personal Notes**: Add notes about characters
- **Edit/Delete**: Full CRUD operations
- **AI Enhancement**: Improve notes with AI regeneration
- **Searchable**: Notes included in semantic search

### Episode Integration
- **Appearance Tracking**: See all episodes character appears in
- **Episode Details**: Click episodes to view details
- **Character Relationships**: Through shared episodes

## API Endpoints

### List Characters
```http
GET /v1/characters?page=1&limit=20
```

### Get Character Details
```http
GET /v1/characters/{id}
```

**Response includes:**
```json
{
  "id": 1,
  "name": "Rick Sanchez",
  "status": "Alive",
  "species": "Human",
  "type": "",
  "gender": "Male",
  "origin": {"name": "Earth (C-137)", "url": "..."},
  "location": {"name": "Citadel of Ricks", "url": "..."},
  "image": "https://...",
  "episode": ["S01E01", "S01E02", ...],
  "episodes": [
    {
      "id": 1,
      "name": "Pilot",
      "episode": "S01E01",
      "air_date": "2013-12-02"
    }
  ]
}
```

### Get Character Episodes
```http
GET /v1/characters/{id}/episodes
```

### Character Notes
```http
# Get notes
GET /v1/characters/{id}/notes

# Add note
POST /v1/characters/{id}/notes
{
  "note_text": "Rick's portal gun allows interdimensional travel"
}

# Update note
PUT /v1/characters/notes/{note_id}
{
  "note_text": "Updated note text"
}

# Delete note
DELETE /v1/characters/notes/{note_id}
```

### Generate Character Summary
```http
POST /v1/generate/character-summary/{id}
```

## User Interface

### Character Grid
- Responsive grid layout (1-3 columns based on screen size)
- Character image thumbnails
- Name and key info visible
- Hover effects and animations
- Click to view details

### Character Detail View
- **Header**: Character image (large), name, status badge
- **Info Panel**: Species, type, gender, origin, location
- **Episodes Section**: List of episode appearances
- **AI Summary**: Flip card with generated summary and scores
- **Notes Panel**: Resizable side panel for notes

### Compact Character Card
Used in detail views:
- Full-size character image
- All character metadata
- Clean, readable layout

## Semantic Search

### How It Works
1. User enters natural language query
2. Query converted to embedding vector
3. Search across character data + notes + summaries
4. Cosine similarity calculated
5. Top results returned with similarity scores

### Example Queries
- "genius scientist with portal gun"
- "morty's grandpa"
- "characters from dimension C-137"
- "characters who died"
- "alien characters"

### Search Results
- Character name and image
- Snippet from notes/summaries
- Similarity percentage
- Entity type badge
- Click to navigate to character

## Technical Implementation

### Data Fetching Strategy

**GraphQL Queries:**
```graphql
query GetCharacter($id: ID!) {
  character(id: $id) {
    id
    name
    status
    species
    type
    gender
    origin {
      name
    }
    location {
      name
    }
    image
    episode {
      id
      name
      episode
      air_date
    }
  }
}
```

### Caching
- Character list: 1 hour cache
- Character details: 1 hour cache
- Episodes: Fetched with character (included)
- Summaries: Permanent cache (rarely change)

### Performance
- Lazy loading for images
- Pagination for lists
- Async summary generation
- Debounced search (300ms)

## Usage Examples

### Browse Characters
1. Navigate to Dashboard
2. Click "Characters" in sidebar
3. Scroll through paginated results
4. Click character card for details

### Find Character via Search
1. Use search bar in navbar
2. Type natural language query
3. View dropdown results
4. Click result to navigate

### View Character Profile
1. Open character detail view
2. View all character information
3. Browse episode appearances
4. Click episodes to view details

### Generate Character Summary
1. Open character detail view
2. Click "View Summary with AI"
3. Wait for generation
4. View summary with evaluation scores
5. Toggle between details and summary

### Add Character Note
1. Open character detail view
2. Notes panel on right side
3. Type note or use AI enhancement
4. Save note
5. Note appears in list

## Best Practices

1. **Use Semantic Search**: More effective than browsing for specific characters
2. **Leverage Notes**: Add notes to improve search results
3. **Episode Navigation**: Use episodes to discover related characters
4. **Summary Caching**: Summaries are cached - don't regenerate unnecessarily

## Character Data Model

```typescript
interface Character {
  id: number
  name: string
  status: "Alive" | "Dead" | "unknown"
  species: string
  type: string
  gender: "Male" | "Female" | "Genderless" | "unknown"
  origin: OriginLocation
  location: OriginLocation
  image: string
  episode: string[]  // Episode URLs
  episodes?: Episode[]  // Full episode objects
}
```

## Future Enhancements

- Character relationship graph
- Character comparisons
- Character collections/favorites
- Character timeline (appearance over seasons)
- Voice/language filters
- Character statistics dashboard

