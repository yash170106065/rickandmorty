"""Seed vector store with character embeddings."""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.api.rick_and_morty_client import RickAndMortyAPIClient
from infrastructure.llm.openai_provider import OpenAIProvider
from infrastructure.vector_store.sqlite_vector_store import SQLiteVectorStore
from shared.config import settings
from shared.logging import logger


async def seed_embeddings():
    """Seed vector store with character embeddings."""
    api_client = RickAndMortyAPIClient()
    llm_provider = OpenAIProvider()
    vector_store = SQLiteVectorStore()
    
    logger.info("Fetching all characters...")
    
    # Get all locations to extract all characters
    locations = await api_client.get_locations()
    all_characters = set()
    
    for location in locations:
        for character in location.residents:
            all_characters.add(character.id)
    
    logger.info(f"Found {len(all_characters)} unique characters")
    
    # Process in batches
    character_ids = list(all_characters)
    batch_size = 10
    processed = 0
    
    for i in range(0, len(character_ids), batch_size):
        batch = character_ids[i:i + batch_size]
        characters = await api_client.get_characters(batch)
        
        for character in characters:
            try:
                # Create embedding text from character data
                embedding_text = (
                    f"{character.name} is a {character.species} "
                    f"({character.type or 'standard'}). "
                    f"Status: {character.status}. "
                    f"Gender: {character.gender}. "
                    f"From {character.origin.get('name', 'unknown')}. "
                    f"Currently at {character.location.get('name', 'unknown')}."
                )
                
                # Get embedding
                embedding = await llm_provider.get_embedding(embedding_text)
                
                # Store in vector store
                await vector_store.upsert_character(character, embedding)
                
                processed += 1
                if processed % 10 == 0:
                    logger.info(f"Processed {processed}/{len(all_characters)} characters")
            except Exception as e:
                logger.error(f"Error processing character {character.id}: {e}")
    
    logger.info(f"Successfully seeded {processed} character embeddings!")


if __name__ == "__main__":
    asyncio.run(seed_embeddings())

