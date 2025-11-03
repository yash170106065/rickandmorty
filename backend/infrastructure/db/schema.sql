-- Unified Notes Table (supports characters, locations, episodes)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_type TEXT NOT NULL,  -- 'character', 'location', or 'episode'
    subject_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(subject_type, subject_id, note_text)  -- Prevent exact duplicates
);

-- Legacy character_notes table (keep for backward compatibility)
CREATE TABLE IF NOT EXISTS character_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Content Table
CREATE TABLE IF NOT EXISTS generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL,
    prompt_type TEXT NOT NULL,
    output_text TEXT NOT NULL,
    factual_score REAL,
    completeness_score REAL,
    creativity_score REAL,
    relevance_score REAL,
    context_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Character Embeddings Table (for semantic search)
CREATE TABLE IF NOT EXISTS character_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL UNIQUE,
    character_name TEXT NOT NULL,
    character_data TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generations Table (unified summary generation with async scoring)
CREATE TABLE IF NOT EXISTS generations (
    generation_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,        -- "character" | "location" | "episode"
    entity_id TEXT NOT NULL,
    summary_text TEXT NOT NULL,
    factual_score REAL,
    creativity_score REAL,
    completeness_score REAL,
    relevance_score REAL,
    scores_status TEXT NOT NULL,       -- "INITIATED" | "GENERATED"
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS generations_unique_entity
ON generations(entity_type, entity_id);

-- Indexes
-- Search Index Table (for unified semantic search across characters, locations, episodes)
CREATE TABLE IF NOT EXISTS search_index (
    entity_type TEXT NOT NULL,    -- "character" | "location" | "episode"
    entity_id TEXT NOT NULL,       -- "1", "3", etc.
    text_blob TEXT NOT NULL,       -- canonical facts + notes + AI summary
    embedding_vector TEXT NOT NULL, -- JSON string of float[] embedding
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (entity_type, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_character_notes_character_id ON character_notes(character_id);
CREATE INDEX IF NOT EXISTS idx_notes_subject ON notes(subject_type, subject_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_subject ON generated_content(subject_id, prompt_type);
CREATE INDEX IF NOT EXISTS idx_character_embeddings_character_id ON character_embeddings(character_id);
CREATE INDEX IF NOT EXISTS idx_search_index_entity ON search_index(entity_type, entity_id);

