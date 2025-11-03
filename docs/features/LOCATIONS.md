# Locations Feature

Comprehensive guide to the Locations feature in Rick & Morty AI Universe Explorer.

## Overview

The Locations feature allows users to explore all dimensions, planets, and locations in the Rick & Morty multiverse. Each location includes details about its type, dimension, and residents.

## Features

### Location Browsing
- **Paginated List**: Browse locations with pagination (20 per page)
- **Grid View**: Visual card-based layout with key information
- **Search Integration**: Find locations via semantic search

### Location Details
- **Metadata Display**: 
  - Location name
  - Type (planet, space station, etc.)
  - Dimension (e.g., "Dimension C-137")
  - Resident count

### Resident Management
- **Resident List**: View all characters living in a location
- **Character Navigation**: Click residents to view their profiles
- **Resident Cards**: Visual cards with character images and info

### AI-Powered Summaries
- **Generate Summary**: Create AI-generated location descriptions
- **Quality Scoring**: See evaluation metrics:
  - Factual Accuracy
  - Completeness
  - Creativity
  - Relevance
- **Flip Card UI**: Toggle between details and AI summary

### Notes System
- **Add Notes**: Attach personal notes to locations
- **Edit/Delete**: Manage your location notes
- **AI Enhancement**: Improve notes with AI regeneration

## API Endpoints

### List Locations
```http
GET /v1/locations?page=1&limit=20
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Earth (C-137)",
    "type": "Planet",
    "dimension": "Dimension C-137",
    "resident_count": 71,
    "residents": [...]
  }
]
```

### Get Location Details
```http
GET /v1/locations/{id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Earth (C-137)",
  "type": "Planet",
  "dimension": "Dimension C-137",
  "residents": [
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

### Add Location Note
```http
POST /v1/locations/{id}/notes
Content-Type: application/json

{
  "note_text": "This is where Rick and Morty first met."
}
```

### Generate Location Summary
```http
POST /v1/generate/location-summary/{id}
```

**Response:**
```json
{
  "id": 123,
  "subject_id": 1,
  "prompt_type": "location_summary",
  "output_text": "Earth (C-137) is a bustling planet...",
  "factual_score": 0.95,
  "completeness_score": 0.87,
  "creativity_score": 0.92,
  "relevance_score": 0.89,
  "created_at": "2024-01-15T10:30:00Z"
}
```

## User Interface

### Dashboard View
- Sidebar navigation to Locations
- Grid of location cards
- Pagination controls
- Search integration in navbar

### Detail View
- Left panel: Location details and resident list
- Center panel: Flip card with details/AI summary
- Right panel: Notes panel (resizable)

### Location Card
Displays:
- Location name (large, gradient text)
- Type badge
- Dimension info
- Resident count
- Hover effects and animations

## Technical Implementation

### Data Flow
1. User navigates to Locations view
2. Frontend requests paginated locations from API
3. Backend queries GraphQL API for location data
4. Locations displayed in grid
5. User clicks location → Detail view loads
6. Resident data fetched via nested GraphQL query
7. AI summary generation on demand
8. Notes loaded and displayed in side panel

### Caching Strategy
- Location list: No cache (changes rarely)
- Location details: Cache for 1 hour
- Residents: Fetched with location (included in query)
- AI summaries: Cached indefinitely (rarely change)

### Performance Considerations
- GraphQL nested queries reduce API calls
- Lazy loading for resident images
- Pagination prevents large data loads
- Async summary generation (non-blocking)

## Usage Examples

### Browse All Locations
1. Navigate to Dashboard
2. Click "Locations" in sidebar
3. Browse through pages
4. Click any location card

### View Location with Residents
1. Click on a location
2. View details panel
3. Scroll through resident list
4. Click resident to navigate to character page

### Generate AI Summary
1. Open location detail view
2. Click "View Summary with AI" button
3. Wait for generation (shows loading state)
4. View summary with quality scores
5. Toggle back to details view

### Add Location Note
1. Open location detail view
2. Notes panel visible on right
3. Type note in text area
4. Click "Add Note" or use AI enhancement
5. Note appears in list below

## Best Practices

1. **Resident Loading**: Residents are loaded with location data for efficiency
2. **Summary Caching**: Once generated, summaries are cached (don't regenerate unnecessarily)
3. **Note Organization**: Use clear, descriptive notes for easier searching
4. **Search Integration**: Notes are searchable via semantic search

## Future Enhancements

- Location comparisons (side-by-side)
- Location relationship graph
- Location history timeline
- User-created location collections
- Location-based episode filtering

