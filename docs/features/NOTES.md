# Notes System Feature

Complete guide to the unified notes system for characters, locations, and episodes.

## Overview

The Notes System allows users to add, edit, delete, and organize personal notes for any entity in the Rick & Morty universe. Notes are searchable and integrated with AI features.

## Features

### Unified Notes
- **Multi-Entity Support**: Notes for characters, locations, and episodes
- **Single Interface**: Consistent UI across all entity types
- **Searchable**: Notes included in semantic search
- **Persistent**: Stored in database, never lost

### CRUD Operations
- **Create**: Add new notes
- **Read**: View all notes for an entity
- **Update**: Edit existing notes
- **Delete**: Remove notes

### AI Enhancement
- **Regenerate**: Improve note text with AI
- **Enhancement**: Expand brief notes into detailed ones
- **Style Consistency**: Maintain Rick & Morty tone

### Notes Panel
- **Resizable**: Adjustable width (300-800px)
- **Always Visible**: Accessible from detail views
- **Timestamps**: Creation date for each note
- **Edit Mode**: Inline editing with cancel option

## API Endpoints

### Get Notes
```http
GET /v1/{entity_type}s/{id}/notes
```
Example: `GET /v1/characters/1/notes`

**Response:**
```json
[
  {
    "id": 1,
    "subject_type": "character",
    "subject_id": 1,
    "note_text": "Rick's portal gun allows interdimensional travel",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Add Note
```http
POST /v1/{entity_type}s/{id}/notes
Content-Type: application/json

{
  "note_text": "Your note text here"
}
```

### Update Note
```http
PUT /v1/{entity_type}s/notes/{note_id}
Content-Type: application/json

{
  "note_text": "Updated note text"
}
```

### Delete Note
```http
DELETE /v1/{entity_type}s/notes/{note_id}
```

## Database Schema

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type TEXT NOT NULL,  -- 'character' | 'location' | 'episode'
    subject_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject_type, subject_id, note_text)  -- Prevent exact duplicates
);

CREATE INDEX idx_notes_subject ON notes(subject_type, subject_id);
```

## User Interface

### Notes Panel Layout
- **Header**: "Notes" title with entity name
- **Add Section**: Text area + "Add Note" button
- **AI Enhancement Button**: Improve note text
- **Notes List**: Chronological list (newest at bottom)
- **Note Items**: 
  - Note text
  - Timestamp
  - Edit/Delete buttons

### Interactions
- **Add Note**: Type and click "Add Note"
- **Edit Note**: Click edit icon, modify text, save
- **Delete Note**: Click delete, confirm
- **AI Enhancement**: Select note or use new note area, click AI button

## Technical Implementation

### Repository Pattern
```python
class NoteRepository(Protocol):
    async def get_notes(
        self, subject_type: str, subject_id: int
    ) -> list[Note]: ...
    
    async def add_note(
        self, subject_type: str, subject_id: int, text: str
    ) -> Note: ...
    
    async def update_note(
        self, note_id: int, text: str
    ) -> Note: ...
    
    async def delete_note(self, note_id: int) -> None: ...
```

### AI Enhancement
Uses the `regenerate-note` endpoint:
- Takes original note text
- Enhances with entity context
- Returns improved version
- User can accept or modify

### Search Integration
Notes are automatically included in semantic search:
1. When note added/updated
2. Search index rebuilt
3. Note text included in embedding
4. Searchable via natural language queries

## Usage Examples

### Add Character Note
1. Open character detail view
2. Notes panel visible on right
3. Type note in text area
4. Click "Add Note" or use AI enhancement
5. Note appears in list

### Edit Note
1. Find note in list
2. Click edit icon (pencil)
3. Modify text in edit mode
4. Click save or cancel

### Enhance Note with AI
1. Select note text (or type new note)
2. Click "✨ Enhance with AI" button
3. Wait for AI enhancement
4. Review improved text
5. Accept or modify further

### Delete Note
1. Find note in list
2. Click delete icon (trash)
3. Confirm deletion
4. Note removed from list

## Best Practices

1. **Be Descriptive**: Clear, detailed notes improve search
2. **Use AI Enhancement**: For longer, better-formatted notes
3. **Organize by Entity**: Keep notes entity-specific
4. **Regular Updates**: Keep notes current and accurate
5. **Search Integration**: Write notes with searchability in mind

## Notes in Semantic Search

Notes are automatically indexed and searchable:

**Example:**
- Note: "Rick's portal gun allows interdimensional travel"
- Query: "character with interdimensional travel device"
- Result: Rick Sanchez (high similarity)

**How It Works:**
1. Note added to entity
2. Search index rebuilt
3. Note text included in text_blob
4. Embedding generated for entire blob
5. Query matches note content

## Data Model

```python
@dataclass
class Note:
    id: int
    subject_type: str  # 'character' | 'location' | 'episode'
    subject_id: int
    note_text: str
    created_at: datetime
```

## Future Enhancements

- **Note Categories**: Organize by type (personality, plot, etc.)
- **Note Tags**: Tag system for better organization
- **Note Sharing**: Share notes with other users
- **Note Export**: Export notes to JSON/CSV
- **Rich Text**: Support formatting, links
- **Note Templates**: Predefined note structures

