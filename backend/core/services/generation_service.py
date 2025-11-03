"""AI generation service."""
import json
from core.models import GeneratedContent, Generation
from core.ports import (
    RickAndMortyClient,
    LLMProvider,
    EvaluationProvider,
    GeneratedContentRepository,
    NoteRepository,
)
from infrastructure.repositories.generation_repository import SQLiteGenerationRepository
from infrastructure.repositories.search_index_repository import SQLiteSearchIndexRepository
from infrastructure.workers.job_queue import job_queue
from shared.logging import logger


class GenerationService:
    """Service for AI-powered content generation."""
    
    def __init__(
        self,
        api_client: RickAndMortyClient,
        llm_provider: LLMProvider,
        evaluator: EvaluationProvider,
        content_repository: GeneratedContentRepository,
        note_repository: NoteRepository | None = None,
    ):
        self.api_client = api_client
        self.llm_provider = llm_provider
        self.evaluator = evaluator
        self.content_repository = content_repository
        self.note_repository = note_repository
        self.generation_repository = SQLiteGenerationRepository()
        self.search_index_repo = SQLiteSearchIndexRepository()
    
    async def generate_location_summary(
        self, location_id: int
    ) -> GeneratedContent:
        """Generate a location summary with evaluation."""
        # Check if summary already exists
        existing = await self.content_repository.get_latest_by_subject(
            location_id, "location_summary"
        )
        if existing:
            # Return existing summary
            return existing
        
        # Fetch location data
        location = await self.api_client.get_location(location_id)
        
        # Build factual context
        context = {
            "location": {
                "id": location.id,
                "name": location.name,
                "type": location.type,
                "dimension": location.dimension,
            },
            "residents": [
                {
                    "id": char.id,
                    "name": char.name,
                    "status": char.status,
                    "species": char.species,
                }
                for char in location.residents
            ],
        }
        
        # Build prompt
        system_prompt = (
            "You are a narrator for the Rick and Morty universe. "
            "Write engaging, witty summaries in the tone of the show."
        )
        
        prompt = (
            f"Write a creative, engaging summary of the location '{location.name}' "
            f"({location.type} in {location.dimension}). "
            f"Include interesting details about its {len(location.residents)} residents: "
            f"{', '.join([char.name for char in location.residents[:5]])}"
            f"{' and more' if len(location.residents) > 5 else ''}. "
            f"Keep it fun, informative, and true to the Rick and Morty style."
        )
        
        # Generate
        output_text = await self.llm_provider.generate(prompt, system_prompt)
        
        # Save with placeholder scores (-1 indicates processing)
        content = GeneratedContent(
            id=0,  # Will be set by repository
            subject_id=location_id,
            prompt_type="location_summary",
            output_text=output_text,
            factual_score=-1.0,  # Placeholder - will be updated by async job
            completeness_score=-1.0,
            creativity_score=-1.0,
            relevance_score=-1.0,
            context_json=context,
            created_at=None,  # Will be set by repository
        )
        
        saved_content = await self.content_repository.save(content)
        
        # Queue async scoring job
        job_queue.enqueue({
            "type": "SCORE_GENERATED_CONTENT",
            "content_id": saved_content.id,
            "subject_id": location_id,
            "prompt_type": "location_summary",
            "generated_text": output_text,
            "factual_context": context,
        })
        
        return saved_content
    
    async def generate_episode_summary(
        self, episode_id: int
    ) -> GeneratedContent:
        """Generate an episode summary with evaluation."""
        # Check if summary already exists
        existing = await self.content_repository.get_latest_by_subject(
            episode_id, "episode_summary"
        )
        if existing:
            return existing
        
        # Fetch episode data
        from core.services.episode_service import EpisodeService
        episode_service = EpisodeService(self.api_client)
        episode, characters = await episode_service.get_episode_with_characters(episode_id)
        
        # Build factual context
        context = {
            "episode": {
                "id": episode.id,
                "name": episode.name,
                "air_date": episode.air_date,
                "episode": episode.episode,
            },
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "species": char.species,
                }
                for char in characters[:10]  # Limit for context
            ],
        }
        
        # Build prompt
        system_prompt = (
            "You are a narrator for the Rick and Morty universe. "
            "Write engaging, witty episode summaries in the tone of the show."
        )
        
        prompt = (
            f"Write a creative, engaging summary of the episode '{episode.name}' "
            f"(Episode {episode.episode}, aired {episode.air_date}). "
            f"Include details about the {len(characters)} characters involved: "
            f"{', '.join([char.name for char in characters[:5]])}"
            f"{' and more' if len(characters) > 5 else ''}. "
            f"Keep it fun, informative, and true to the Rick and Morty style."
        )
        
        # Generate
        output_text = await self.llm_provider.generate(prompt, system_prompt)
        
        # Save with placeholder scores
        content = GeneratedContent(
            id=0,
            subject_id=episode_id,
            prompt_type="episode_summary",
            output_text=output_text,
            factual_score=-1.0,
            completeness_score=-1.0,
            creativity_score=-1.0,
            relevance_score=-1.0,
            context_json=context,
            created_at=None,
        )
        
        saved_content = await self.content_repository.save(content)
        
        # Queue async scoring job
        job_queue.enqueue({
            "type": "SCORE_GENERATED_CONTENT",
            "content_id": saved_content.id,
            "subject_id": episode_id,
            "prompt_type": "episode_summary",
            "generated_text": output_text,
            "factual_context": context,
        })
        
        return saved_content
    
    async def generate_character_summary(
        self, character_id: int
    ) -> GeneratedContent:
        """Generate a character summary with evaluation."""
        # Check if summary already exists
        existing = await self.content_repository.get_latest_by_subject(
            character_id, "character_summary"
        )
        if existing:
            return existing
        
        # Fetch character data
        character = await self.api_client.get_character(character_id)
        
        # Get episodes data if available
        episodes_info = []
        if hasattr(character, 'episodes_data') and character.episodes_data:
            episodes_info = [
                {
                    "id": ep.id,
                    "name": ep.name,
                    "episode": ep.episode,
                }
                for ep in character.episodes_data[:10]
            ]
        
        # Build factual context
        origin_name = ""
        if character.origin:
            if isinstance(character.origin, dict):
                origin_name = character.origin.get("name", "")
            else:
                origin_name = ""
        
        location_name = ""
        if character.location:
            if isinstance(character.location, dict):
                location_name = character.location.get("name", "")
            else:
                location_name = ""
        
        context = {
            "character": {
                "id": character.id,
                "name": character.name,
                "status": character.status,
                "species": character.species,
                "type": character.type or "",
                "gender": character.gender,
                "origin": origin_name,
                "location": location_name,
            },
            "episodes": episodes_info,
        }
        
        # Build prompt
        system_prompt = (
            "You are a narrator for the Rick and Morty universe. "
            "Write engaging, witty character summaries in the tone of the show."
        )
        
        origin_text = f"From {origin_name}" if origin_name else ""
        location_text = f"Currently located at {location_name}" if location_name else ""
        episodes_text = f"Appears in {len(episodes_info)} episodes" if episodes_info else "Has appeared in multiple episodes"
        
        prompt = (
            f"Write a creative, engaging summary of the character '{character.name}' "
            f"({character.species}, {character.status}). "
            f"{origin_text} {location_text}. "
            f"{episodes_text}. "
            f"Keep it fun, informative, and true to the Rick and Morty style. "
            f"Include interesting personality traits and memorable moments if relevant."
        )
        
        # Generate
        output_text = await self.llm_provider.generate(prompt, system_prompt)
        
        # Save with placeholder scores
        content = GeneratedContent(
            id=0,
            subject_id=character_id,
            prompt_type="character_summary",
            output_text=output_text,
            factual_score=-1.0,
            completeness_score=-1.0,
            creativity_score=-1.0,
            relevance_score=-1.0,
            context_json=context,
            created_at=None,
        )
        
        saved_content = await self.content_repository.save(content)
        
        # Queue async scoring job
        job_queue.enqueue({
            "type": "SCORE_GENERATED_CONTENT",
            "content_id": saved_content.id,
            "subject_id": character_id,
            "prompt_type": "character_summary",
            "generated_text": output_text,
            "factual_context": context,
        })
        
        return saved_content
    
    async def generate_character_dialogue(
        self, character_id1: int, character_id2: int, topic: str = ""
    ) -> GeneratedContent:
        """Generate a dialogue between two characters."""
        char1 = await self.api_client.get_character(character_id1)
        char2 = await self.api_client.get_character(character_id2)
        
        context = {
            "character1": {
                "id": char1.id,
                "name": char1.name,
                "species": char1.species,
                "status": char1.status,
            },
            "character2": {
                "id": char2.id,
                "name": char2.name,
                "species": char2.species,
                "status": char2.status,
            },
            "topic": topic or "general conversation",
        }
        
        system_prompt = (
            "You are a writer for Rick and Morty. "
            "Write authentic dialogue that matches each character's personality."
        )
        
        prompt = (
            f"Write a short, engaging dialogue between {char1.name} "
            f"({char1.species}) and {char2.name} ({char2.species}). "
            f"{f'The topic should be about: {topic}' if topic else ''}"
            f"Keep it true to the show's humor and character personalities. "
            f"Maximum 10-12 exchanges between them."
        )
        
        output_text = await self.llm_provider.generate(prompt, system_prompt)
        
        evaluation = self.evaluator.evaluate(output_text, context)
        
        content = GeneratedContent(
            id=0,
            subject_id=character_id1,  # Primary character
            prompt_type="character_dialogue",
            output_text=output_text,
            factual_score=evaluation.factual_score,
            completeness_score=evaluation.completeness_score,
            creativity_score=evaluation.creativity_score,
            relevance_score=evaluation.relevance_score,
            context_json=context,
            created_at=None,
        )
        
        return await self.content_repository.save(content)
    
    async def generate_summary(
        self, entity_type: str, entity_id: str
    ) -> Generation:
        """Unified summary generation with async scoring."""
        # Check cache
        existing = await self.generation_repository.get_by_entity(
            entity_type, entity_id
        )
        if existing:
            return existing
        
        # Fetch canonical context based on entity type
        canonical_context = await self._fetch_canonical_context(
            entity_type, int(entity_id)
        )
        
        # Build prompt
        system_prompt = (
            "You are a sarcastic, in-universe narrator from Rick & Morty. "
            "Summarize this in 3-5 sentences. Be irreverent and funny, but stay "
            "consistent with the structured data below. Do not invent characters "
            "or contradict facts. Output only plain text - no markdown or JSON."
        )
        
        prompt = self._build_prompt(entity_type, canonical_context)
        
        # Generate summary
        summary_text = await self.llm_provider.generate(prompt, system_prompt)
        
        # Store with INITIATED status
        generation = await self.generation_repository.create_initiated(
            entity_type, entity_id, summary_text
        )
        
        # Enqueue async scoring job
        job_queue.enqueue({
            "type": "FINALIZE_GENERATION",
            "entityType": entity_type,
            "entityId": entity_id,
            "summaryText": summary_text,
            "canonicalContext": canonical_context,
        })
        
        return generation
    
    async def _fetch_canonical_context(
        self, entity_type: str, entity_id: int
    ) -> dict:
        """Fetch canonical context for grounding."""
        if entity_type == "location":
            location = await self.api_client.get_location(entity_id)
            return {
                "name": location.name,
                "type": location.type,
                "dimension": location.dimension,
                "residents": [
                    {
                        "name": char.name,
                        "status": char.status,
                        "species": char.species,
                    }
                    for char in location.residents
                ],
            }
        elif entity_type == "character":
            character = await self.api_client.get_character(entity_id)
            origin_name = ""
            if character.origin and isinstance(character.origin, dict):
                origin_name = character.origin.get("name", "")
            
            location_name = ""
            if character.location and isinstance(character.location, dict):
                location_name = character.location.get("name", "")
            
            return {
                "name": character.name,
                "status": character.status,
                "species": character.species,
                "origin": origin_name,
                "lastKnownLocation": location_name,
            }
        elif entity_type == "episode":
            episode = await self.api_client.get_episode(entity_id)
            # Get characters for episode
            characters_list = []
            if hasattr(episode, 'characters_data') and episode.characters_data:
                characters_list = [char.name for char in episode.characters_data]
            elif hasattr(episode, 'characters') and episode.characters:
                # If we have character URLs, extract IDs and fetch
                character_ids = []
                for char_url in episode.characters[:10]:  # Limit to 10
                    if isinstance(char_url, str) and '/character/' in char_url:
                        try:
                            char_id = int(char_url.split('/character/')[-1])
                            character_ids.append(char_id)
                        except:
                            pass
                
                # Fetch character names
                for char_id in character_ids[:5]:  # Limit to 5 for context
                    try:
                        char = await self.api_client.get_character(char_id)
                        characters_list.append(char.name)
                    except:
                        pass
            
            return {
                "title": episode.name,
                "episodeCode": episode.episode,
                "airDate": episode.air_date,
                "characters": characters_list,
            }
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
    
    def _build_prompt(self, entity_type: str, context: dict) -> str:
        """Build prompt from canonical context."""
        context_json = json.dumps(context, indent=2)
        
        if entity_type == "location":
            return (
                f"Summarize this location in the tone of a Rick & Morty narrator:\n\n"
                f"Data:\n{context_json}\n\n"
                f"Output only plain text - no markdown or JSON."
            )
        elif entity_type == "character":
            return (
                f"Summarize this character in the tone of a Rick & Morty narrator:\n\n"
                f"Data:\n{context_json}\n\n"
                f"Output only plain text - no markdown or JSON."
            )
        elif entity_type == "episode":
            return (
                f"Summarize this episode in the tone of a Rick & Morty narrator:\n\n"
                f"Data:\n{context_json}\n\n"
                f"Output only plain text - no markdown or JSON."
            )
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
    
    async def _finalize_generation_job(self, job: dict) -> None:
        """Process FINALIZE_GENERATION job - compute scores asynchronously."""
        entity_type = job["entityType"]
        entity_id = job["entityId"]
        summary_text = job["summaryText"]
        canonical_context = job["canonicalContext"]
        
        # 1. Evaluate factual consistency
        factual_score = self.evaluator._compute_factual_score(
            summary_text, canonical_context
        )
        
        # 2. Evaluate creativity (async LLM judge)
        creativity_score = await self.evaluator.score_creativity_async(
            summary_text, self.llm_provider
        )
        
        # 3. Evaluate completeness
        completeness_score = self.evaluator._compute_completeness_score(
            summary_text, canonical_context
        )
        
        # 4. Evaluate relevance
        relevance_score = self.evaluator._compute_relevance_score(
            summary_text, canonical_context
        )
        
        # 5. Update database
        await self.generation_repository.update_scores(
            entity_type,
            entity_id,
            factual_score,
            creativity_score,
            completeness_score,
            relevance_score,
        )
        
        logger.info(
            f"Finalized generation for {entity_type}/{entity_id}: "
            f"factual={factual_score:.2f}, creativity={creativity_score:.2f}, "
            f"completeness={completeness_score:.2f}, relevance={relevance_score:.2f}"
        )
        
        # Rebuild search index after finalizing generation
        await self.rebuild_search_index(entity_type, entity_id)
    
    async def _score_generated_content_job(self, job: dict) -> None:
        """Process SCORE_GENERATED_CONTENT job - compute scores asynchronously."""
        content_id = job["content_id"]
        generated_text = job["generated_text"]
        factual_context = job["factual_context"]
        
        # Evaluate
        evaluation = self.evaluator.evaluate(generated_text, factual_context)
        
        # Update scores in database
        await self.content_repository.update_scores(
            content_id,
            evaluation.factual_score,
            evaluation.completeness_score,
            evaluation.creativity_score,
            evaluation.relevance_score,
        )
        
        logger.info(
            f"Updated scores for content {content_id}: "
            f"factual={evaluation.factual_score:.2f}, "
            f"completeness={evaluation.completeness_score:.2f}, "
            f"creativity={evaluation.creativity_score:.2f}, "
            f"relevance={evaluation.relevance_score:.2f}"
        )
        
        # Rebuild search index for this entity
        # Extract entity info from the saved content
        saved_content = await self.content_repository.get_by_subject(
            job.get("subject_id", 0), job.get("prompt_type", "")
        )
        if saved_content:
            content = saved_content[0] if saved_content else None
            if content:
                # Determine entity type from prompt_type
                entity_type_map = {
                    "location_summary": "location",
                    "character_summary": "character",
                    "episode_summary": "episode",
                }
                entity_type = entity_type_map.get(content.prompt_type)
                if entity_type:
                    await self.rebuild_search_index(entity_type, str(content.subject_id))
    
    async def regenerate_note_text(
        self, note_text: str, entity_type: str, entity_id: int
    ) -> str:
        """Regenerate/improve note text with AI - no scoring, no DB entry."""
        # Fetch entity context based on type
        if entity_type == "location":
            location = await self.api_client.get_location(entity_id)
            context_info = f"Location: {location.name} ({location.type} in {location.dimension})"
            entity_context = f"{len(location.residents)} residents"
        elif entity_type == "episode":
            from core.services.episode_service import EpisodeService
            episode_service = EpisodeService(self.api_client)
            episode, characters = await episode_service.get_episode_with_characters(entity_id)
            context_info = f"Episode: {episode.name} (Episode {episode.episode}, aired {episode.air_date})"
            entity_context = f"{len(characters)} characters"
        elif entity_type == "character":
            character = await self.api_client.get_character(entity_id)
            context_info = f"Character: {character.name} ({character.species}, {character.status})"
            entity_context = character.name
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        # Build prompt
        system_prompt = (
            "You are a helpful writing assistant for Rick & Morty notes. "
            "Improve and enhance the given note text while keeping it concise "
            "and relevant to the entity. Keep it under 300 words. "
            "Maintain the original meaning and style if provided, or create "
            "engaging content in the Rick & Morty tone if the text is minimal."
        )
        
        prompt = (
            f"Improve and enhance this note about {context_info}:\n\n"
            f"Original note:\n{note_text}\n\n"
            f"Context: {entity_context}\n\n"
            f"Generate an improved version that is clear, engaging, and relevant. "
            f"Keep it concise (under 300 words). Maintain the Rick & Morty universe tone. "
            f"Output only the improved text, no explanations or metadata."
        )
        
        # Generate improved text
        improved_text = await self.llm_provider.generate(prompt, system_prompt)
        
        # Limit to 300 words as requested
        words = improved_text.split()
        if len(words) > 300:
            improved_text = " ".join(words[:300]) + "..."
        
        return improved_text.strip()
    
    async def rebuild_search_index(
        self, entity_type: str, entity_id: str
    ) -> None:
        """Rebuild search index entry for an entity (character, location, or episode)."""
        try:
            entity_id_int = int(entity_id)
            
            # Build text blob from canonical data + notes + AI summary
            text_parts = []
            
            # 1. Fetch canonical data
            if entity_type == "character":
                entity = await self.api_client.get_character(entity_id_int)
                origin_name = ""
                if entity.origin and isinstance(entity.origin, dict):
                    origin_name = entity.origin.get("name", "")
                location_name = ""
                if entity.location and isinstance(entity.location, dict):
                    location_name = entity.location.get("name", "")
                
                text_parts.append(f"Name: {entity.name}")
                text_parts.append(f"Species: {entity.species}")
                text_parts.append(f"Status: {entity.status}")
                text_parts.append(f"Type: {entity.type or 'Unknown'}")
                text_parts.append(f"Gender: {entity.gender}")
                if origin_name:
                    text_parts.append(f"Origin: {origin_name}")
                if location_name:
                    text_parts.append(f"Location: {location_name}")
                text_parts.append(f"Episodes: {len(entity.episode) if entity.episode else 0}")
                
            elif entity_type == "location":
                entity = await self.api_client.get_location(entity_id_int)
                text_parts.append(f"Name: {entity.name}")
                text_parts.append(f"Type: {entity.type}")
                text_parts.append(f"Dimension: {entity.dimension}")
                text_parts.append(f"Residents: {len(entity.residents)}")
                if entity.residents:
                    resident_names = ", ".join([char.name for char in entity.residents[:10]])
                    text_parts.append(f"Residents include: {resident_names}")
                    
            elif entity_type == "episode":
                entity = await self.api_client.get_episode(entity_id_int)
                text_parts.append(f"Title: {entity.name}")
                text_parts.append(f"Episode: {entity.episode}")
                text_parts.append(f"Air Date: {entity.air_date}")
                if hasattr(entity, 'characters_data') and entity.characters_data:
                    char_names = ", ".join([char.name for char in entity.characters_data[:10]])
                    text_parts.append(f"Characters: {char_names}")
                elif hasattr(entity, 'characters') and entity.characters:
                    text_parts.append(f"Characters: {len(entity.characters)} characters")
            else:
                logger.warning(f"Unknown entity type for search index: {entity_type}")
                return
            
            # 2. Fetch notes
            if self.note_repository:
                try:
                    notes = await self.note_repository.get_notes(entity_type, entity_id_int)
                    if notes:
                        note_texts = [note.note_text for note in notes[:5]]  # Limit to 5 most recent
                        if note_texts:
                            text_parts.append("\nUser notes:")
                            for note_text in note_texts:
                                text_parts.append(f"- {note_text}")
                except Exception as e:
                    logger.warning(f"Error fetching notes for search index: {e}")
            
            # 3. Fetch latest AI summary
            prompt_type_map = {
                "character": "character_summary",
                "location": "location_summary",
                "episode": "episode_summary",
            }
            prompt_type = prompt_type_map.get(entity_type)
            if prompt_type:
                try:
                    summary = await self.content_repository.get_latest_by_subject(
                        entity_id_int, prompt_type
                    )
                    if summary and summary.output_text:
                        # Only include if scores are complete (not processing)
                        if summary.factual_score >= 0:
                            text_parts.append(f"\nAI Summary: {summary.output_text[:500]}")  # Limit length
                except Exception as e:
                    logger.warning(f"Error fetching summary for search index: {e}")
            
            # Combine into text blob
            text_blob = "\n".join(text_parts)
            
            # Get embedding
            embedding = await self.llm_provider.get_embedding(text_blob)
            
            # Upsert into search index
            await self.search_index_repo.upsert_entry(
                entity_type, entity_id, text_blob, embedding
            )
            
            logger.info(f"Rebuilt search index for {entity_type}/{entity_id}")
            
        except Exception as e:
            logger.error(f"Error rebuilding search index for {entity_type}/{entity_id}: {e}")
            # Don't raise - search index rebuild should not break main flow

