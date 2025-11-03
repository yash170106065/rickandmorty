# AI Generation Feature

Comprehensive guide to AI-powered content generation with quality evaluation.

## Overview

The AI Generation feature creates contextual summaries, dialogues, and insights using OpenAI's language models, with built-in quality evaluation scoring.

## Features

### Content Types

1. **Location Summaries**
   - Descriptions of locations in Rick & Morty narrator style
   - Includes resident information
   - Contextual details about dimensions

2. **Character Summaries**
   - Personality insights
   - Memorable moments
   - Role in the multiverse

3. **Episode Summaries**
   - Plot summaries
   - Character interactions
   - Themes and story arcs

4. **Dialogue Generation** (Future)
   - Character-to-character dialogues
   - Topic-based conversations

### Quality Evaluation

Every generated piece of content is automatically evaluated on four dimensions:

#### 1. Factual Score (0.0 - 1.0)
**Purpose**: Validates consistency with source data

**Evaluation Method**:
- Keyword matching against canonical data
- Fact verification (names, locations, relationships)
- Contradiction detection

**Scoring**:
- 1.0: Perfect factual accuracy
- 0.8-0.9: Minor omissions
- 0.6-0.7: Some inaccuracies
- < 0.6: Significant factual issues

#### 2. Completeness Score (0.0 - 1.0)
**Purpose**: Measures information coverage

**Evaluation Method**:
- Coverage of available facts
- Important details included
- No critical omissions

**Scoring**:
- 1.0: All important information covered
- 0.8-0.9: Most information included
- 0.6-0.7: Some important details missing
- < 0.6: Significant gaps

#### 3. Creativity Score (0.0 - 1.0)
**Purpose**: Assesses narrative quality and style

**Evaluation Method**:
- LLM-as-judge approach
- Style consistency with Rick & Morty tone
- Narrative engagement
- Original phrasing

**Scoring**:
- 1.0: Excellent narrative, perfect tone
- 0.8-0.9: Good style, engaging
- 0.6-0.7: Adequate but generic
- < 0.6: Poor style or tone mismatch

#### 4. Relevance Score (0.0 - 1.0)
**Purpose**: Ensures focus on the target entity

**Evaluation Method**:
- Entity mention frequency
- Focus on target vs. tangential information
- Context appropriateness

**Scoring**:
- 1.0: Perfectly focused on entity
- 0.8-0.9: Mostly relevant
- 0.6-0.7: Some tangents
- < 0.6: Off-topic or unfocused

## API Endpoints

### Generate Location Summary
```http
POST /v1/generate/location-summary/{location_id}
```

### Generate Character Summary
```http
POST /v1/generate/character-summary/{character_id}
```

### Generate Episode Summary
```http
POST /v1/generate/episode-summary/{episode_id}
```

**Response Format:**
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

### Regenerate Note Text
```http
POST /v1/generate/regenerate-note
{
  "note_text": "Original note text",
  "entity_type": "character",
  "entity_id": 1
}
```

## Technical Implementation

### Two-Phase Generation

**Phase 1: Immediate (Synchronous)**
1. User requests generation
2. Fetch entity data from API
3. Build context and prompt
4. Call OpenAI API
5. Save content with placeholder scores (-1)
6. Return immediately to user

**Phase 2: Async Evaluation (Background)**
1. Job queued for evaluation
2. Worker processes job
3. Calculate all four scores
4. Update content with final scores
5. Update search index if needed

### Prompt Engineering

**System Prompt:**
```
You are a narrator for the Rick and Morty universe. 
Write engaging, witty summaries in the tone of the show.
```

**Example Location Prompt:**
```
Write a creative, engaging summary of the location 'Earth (C-137)'
(Planet in Dimension C-137). Include interesting details about its 
71 residents: Rick Sanchez, Morty Smith, and more. 
Keep it fun, informative, and true to the Rick and Morty style.
```

### Evaluation Implementation

**Factual Score Calculation:**
```python
def _compute_factual_score(text: str, context: dict) -> float:
    # Extract facts from context
    canonical_facts = extract_facts(context)
    
    # Check for contradictions
    contradictions = check_contradictions(text, canonical_facts)
    
    # Calculate score
    base_score = 1.0
    for contradiction in contradictions:
        base_score -= 0.1
    
    return max(0.0, base_score)
```

**Creativity Score (LLM-as-Judge):**
```python
async def score_creativity_async(text: str, llm: LLMProvider) -> float:
    prompt = f"""
    Rate the creativity and narrative quality of this text (0.0-1.0):
    {text}
    
    Consider: style, tone, engagement, originality.
    Return only a number between 0.0 and 1.0.
    """
    
    response = await llm.generate(prompt)
    return float(response.strip())
```

### Caching Strategy

- **Generated Content**: Cached permanently (content doesn't change)
- **Evaluation Scores**: Updated asynchronously
- **Prompts**: Reusable across similar entities

## User Interface

### Generation Flow
1. User clicks "View Summary with AI"
2. Loading state displayed
3. Summary appears (scores may show -1 initially)
4. Scores update in real-time as evaluation completes
5. Final scores displayed

### Score Display
- Visual badges/chips for each score
- Color coding:
  - Blue: Factual
  - Purple: Completeness
  - Pink: Creativity
  - Green: Relevance
- Percentage display (0-100%)
- Loading state for scores (-1)

### Flip Card UI
- Front: Entity details
- Back: AI summary with scores
- Smooth 3D flip animation
- Toggle button to switch views

## Best Practices

1. **Cache Management**: Don't regenerate if summary exists
2. **Score Interpretation**: 
   - > 0.8: Excellent
   - 0.6-0.8: Good
   - < 0.6: May need regeneration
3. **Context Quality**: Better context → better summaries
4. **Async Patience**: Scores update automatically, no refresh needed

## Cost Considerations

**OpenAI API Costs:**
- Generation: ~$0.01-0.05 per summary (GPT-4)
- Evaluation: ~$0.005 per evaluation
- Embeddings: ~$0.0001 per embedding

**Optimization:**
- Caching reduces API calls
- Batch processing for evaluations
- Use GPT-3.5-turbo for non-critical generations

## Future Enhancements

- **Dialogue Generation**: Character conversations
- **Multi-Entity Summaries**: Compare locations/characters
- **Custom Prompts**: User-defined generation styles
- **Score History**: Track score improvements over time
- **A/B Testing**: Compare different prompt strategies

