# Episodes Feature

Complete guide to the Episodes feature in Rick & Morty AI Universe Explorer.

## Overview

The Episodes feature provides access to all episodes from the Rick & Morty series, with detailed information about plots, characters, air dates, and AI-generated summaries.

## Features

### Episode Browsing
- **Complete Catalog**: Access all episodes across all seasons
- **Paginated List**: Browse episodes 20 at a time
- **Visual Cards**: Episode cards with key information
- **Season Organization**: Episodes organized by season

### Episode Details
Each episode includes:
- **Metadata**:
  - Episode name/title
  - Episode code (e.g., "S01E01")
  - Air date
  - Character count
- **Character List**: All characters appearing in the episode
- **Navigation**: Click characters to view their profiles

### AI-Powered Summaries
- **Episode Summary**: AI-generated plot summaries
- **Character Interactions**: Analysis of character relationships
- **Themes**: Identification of episode themes
- **Quality Scoring**: Evaluation metrics for summaries

### Notes System
- **Episode Notes**: Personal annotations
- **Plot Notes**: Track important plot points
- **Character Notes**: Notes about character appearances
- **AI Enhancement**: Improve notes with AI

## API Endpoints

### List Episodes
```http
GET /v1/episodes?page=1&limit=20
```

### Get Episode Details
```http
GET /v1/episodes/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Pilot",
  "air_date": "December 2, 2013",
  "episode": "S01E01",
  "characters": [
    {
      "id": 1,
      "name": "Rick Sanchez",
      "species": "Human",
      "status": "Alive",
      "image": "https://..."
    }
  ]
}
```

### Episode Notes
```http
# Get notes
GET /v1/episodes/{id}/notes

# Add note
POST /v1/episodes/{id}/notes
{
  "note_text": "This episode introduces the portal gun"
}

# Update/Delete (similar to characters)
```

### Generate Episode Summary
```http
POST /v1/generate/episode-summary/{id}
```

## User Interface

### Episode Grid
- Responsive grid layout
- Episode cards with:
  - Episode code badge
  - Episode name
  - Air date
  - Character count
- Hover effects
- Click to view details

### Episode Detail View
- **Header**: Episode name, code, air date
- **Character Grid**: All characters in episode
- **AI Summary**: Flip card with generated summary
- **Notes Panel**: Side panel for notes

### Character Navigation
- Click any character card
- Navigate to character detail page
- View character's episode history

## Technical Implementation

### Data Fetching
Episodes are fetched with nested character data via GraphQL:

```graphql
query GetEpisode($id: ID!) {
  episode(id: $id) {
    id
    name
    air_date
    episode
    characters {
      id
      name
      species
      status
      image
    }
  }
}
```

### Caching Strategy
- Episode list: 1 hour
- Episode details: 1 hour
- Character data: Included in episode query
- Summaries: Permanent cache

## Usage Examples

### Browse Episodes
1. Navigate to Dashboard
2. Click "Episodes" in sidebar
3. Browse through pages
4. Click episode card

### View Episode with Characters
1. Open episode detail view
2. View episode metadata
3. Browse character grid
4. Click characters for details

### Generate Episode Summary
1. Open episode detail
2. Click "View Summary with AI"
3. View summary with quality scores
4. Toggle back to details

## Future Enhancements

- Episode timeline visualization
- Episode ratings/reviews
- Episode collections/playlists
- Episode comparison tool
- Character relationship graphs by episode

