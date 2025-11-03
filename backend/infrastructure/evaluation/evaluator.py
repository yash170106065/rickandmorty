"""Content evaluation implementation with improved language and efficiency."""
import json
import re
from core.models import EvaluationResult
from core.ports import EvaluationProvider, LLMProvider
from shared.logging import logger


class HeuristicEvaluator(EvaluationProvider):
    """Heuristic-based content evaluator with improved scoring methods."""
    
    def evaluate(
        self,
        generated_text: str,
        factual_context: dict,
    ) -> EvaluationResult:
        """Evaluate generated text using heuristics and improved metrics."""
        
        # Factual Score: Check factual accuracy and consistency
        factual_score = self._compute_factual_score(
            generated_text, factual_context
        )
        
        # Completeness Score: Check coverage of available information
        completeness_score = self._compute_completeness_score(
            generated_text, factual_context
        )
        
        # Creativity Score: Check narrative quality (uses heuristic, async LLM scoring available)
        creativity_score = self._compute_creativity_score(generated_text)
        
        # Relevance Score: Check how well content focuses on the entity
        relevance_score = self._compute_relevance_score(
            generated_text, factual_context
        )
        
        return EvaluationResult(
            factual_score=factual_score,
            completeness_score=completeness_score,
            creativity_score=creativity_score,
            relevance_score=relevance_score,
        )
    
    def _compute_factual_score(
        self, text: str, context: dict
    ) -> float:
        """Compute factual accuracy score with improved matching."""
        text_lower = text.lower()
        score_parts = []
        
        # Check for character/resident names (improved matching)
        if "characters" in context or "residents" in context:
            characters = context.get("characters", context.get("residents", []))
            if isinstance(characters, list) and characters:
                matches = 0
                for char in characters[:10]:  # Limit to avoid excessive computation
                    if isinstance(char, dict) and "name" in char:
                        name = char["name"]
                        # Use word boundary matching for better accuracy
                        if re.search(r'\b' + re.escape(name.lower()) + r'\b', text_lower):
                            matches += 1
                if len(characters) > 0:
                    score_parts.append(matches / min(len(characters), 10))
        
        # Check for location details (more comprehensive)
        if "location" in context:
            loc = context["location"]
            if isinstance(loc, dict):
                loc_matches = 0
                loc_total = 0
                for key in ["name", "type", "dimension"]:
                    if key in loc and loc[key]:
                        loc_total += 1
                        value = str(loc[key]).lower()
                        if re.search(r'\b' + re.escape(value) + r'\b', text_lower):
                            loc_matches += 1
                if loc_total > 0:
                    score_parts.append(loc_matches / loc_total)
        
        # Check for episode details
        if "episode" in context:
            ep = context["episode"]
            if isinstance(ep, dict):
                ep_matches = 0
                ep_total = 0
                for key in ["name", "episode", "air_date"]:
                    if key in ep and ep[key]:
                        ep_total += 1
                        value = str(ep[key]).lower()
                        if re.search(r'\b' + re.escape(value) + r'\b', text_lower):
                            ep_matches += 1
                if ep_total > 0:
                    score_parts.append(ep_matches / ep_total)
        
        if not score_parts:
            return 0.5  # Neutral score if no entities to check
        
        # Average all score parts
        base_score = sum(score_parts) / len(score_parts)
        
        # Bonus for consistency (check for contradictory statements)
        # Simple heuristic: penalize if text contains common contradiction indicators
        contradiction_indicators = [
            "but", "however", "although", "despite", "contradict"
        ]
        contradiction_count = sum(1 for word in contradiction_indicators if word in text_lower)
        # Small penalty for too many contradictions (could indicate factual issues)
        penalty = min(0.1, contradiction_count * 0.02)
        
        return min(1.0, max(0.0, base_score - penalty))
    
    def _compute_completeness_score(
        self, text: str, context: dict
    ) -> float:
        """Compute completeness score with improved metrics."""
        text_words = len(text.split())
        
        # Count unique information elements in context
        context_info_count = 0
        if isinstance(context, dict):
            # Count non-empty fields
            for key, value in context.items():
                if isinstance(value, (dict, list)):
                    context_info_count += len(value) if isinstance(value, list) else len([v for v in value.values() if v])
                elif value:
                    context_info_count += 1
        
        # Base score on text length (heuristic)
        length_score = 0.0
        if text_words < 30:
            length_score = 0.2
        elif text_words < 60:
            length_score = 0.4
        elif text_words < 100:
            length_score = 0.6
        elif text_words < 150:
            length_score = 0.75
        elif text_words < 250:
            length_score = 0.9
        else:
            length_score = min(1.0, 0.9 + (text_words - 250) / 1000)
        
        # Bonus for covering multiple context elements
        coverage_bonus = 0.0
        if context_info_count > 0:
            # Count how many unique entities/concepts from context appear
            context_str = json.dumps(context, default=str).lower()
            context_terms = set(re.findall(r'\b\w{4,}\b', context_str))  # Words 4+ chars
            text_terms = set(re.findall(r'\b\w{4,}\b', text.lower()))
            if context_terms:
                overlap_ratio = len(text_terms & context_terms) / len(context_terms)
                coverage_bonus = min(0.2, overlap_ratio * 0.2)
        
        return min(1.0, length_score + coverage_bonus)
    
    def _compute_creativity_score(self, text: str) -> float:
        """Compute creativity score with improved heuristics."""
        text_lower = text.lower()
        score = 0.0
        
        # Check for narrative elements (weighted)
        narrative_indicators = {
            "dialogue": 0.15,
            "adventure": 0.12,
            "journey": 0.10,
            "story": 0.08,
            "tale": 0.08,
            "narrative": 0.08,
        }
        for indicator, weight in narrative_indicators.items():
            if indicator in text_lower:
                score += weight
        
        # Check punctuation variety (indicates engaging writing)
        punctuation_ratio = len([c for c in text if c in ".,!?:;"]) / max(len(text), 1)
        if punctuation_ratio > 0.04:
            score += 0.1  # Good punctuation variety
        
        # Check for engaging/exciting language
        engaging_phrases = [
            "epic", "amazing", "incredible", "fantastic", "legendary",
            "unforgettable", "mind-blowing", "extraordinary", "remarkable",
            "spectacular", "phenomenal", "outrageous", "wicked", "brutal"
        ]
        engaging_count = sum(1 for phrase in engaging_phrases if phrase in text_lower)
        score += min(0.15, engaging_count * 0.03)  # Cap at 0.15
        
        # Check for Rick & Morty style elements
        rick_morty_style = [
            "portal", "multiverse", "dimension", "scientist", "genius",
            "brilliant", "crazy", "insane", "absurd", "ridiculous",
            "paradox", "quantum", "galactic", "cosmic"
        ]
        style_count = sum(1 for word in rick_morty_style if word in text_lower)
        score += min(0.2, style_count * 0.05)  # Cap at 0.2
        
        # Check for variety in sentence structure (exclamation/question marks)
        if "!" in text or "?" in text:
            score += 0.1
        
        return min(1.0, score)
    
    def _compute_relevance_score(
        self, text: str, context: dict
    ) -> float:
        """Compute relevance score - how well content focuses on the entity."""
        text_lower = text.lower()
        relevance_indicators = []
        
        # Primary entity name should appear multiple times
        if "location" in context and isinstance(context["location"], dict):
            loc_name = context["location"].get("name", "")
            if loc_name:
                name_count = len(re.findall(r'\b' + re.escape(loc_name.lower()) + r'\b', text_lower))
                # Entity name should appear at least once, ideally 2-3 times
                if name_count >= 1:
                    relevance_indicators.append(min(1.0, name_count / 3.0))
        
        if "character" in context and isinstance(context["character"], dict):
            char_name = context["character"].get("name", "")
            if char_name:
                name_count = len(re.findall(r'\b' + re.escape(char_name.lower()) + r'\b', text_lower))
                if name_count >= 1:
                    relevance_indicators.append(min(1.0, name_count / 3.0))
        
        if "episode" in context and isinstance(context["episode"], dict):
            ep_name = context["episode"].get("name", "")
            if ep_name:
                name_count = len(re.findall(r'\b' + re.escape(ep_name.lower()) + r'\b', text_lower))
                if name_count >= 1:
                    relevance_indicators.append(min(1.0, name_count / 3.0))
        
        # Check for off-topic indicators (penalize)
        off_topic_penalty = 0.0
        off_topic_words = [
            "unrelated", "besides", "incidentally", "tangent",
            "digression", "by the way", "speaking of"
        ]
        off_topic_count = sum(1 for phrase in off_topic_words if phrase in text_lower)
        off_topic_penalty = min(0.2, off_topic_count * 0.05)
        
        # Check for focus keywords that indicate relevance
        focus_keywords = [
            "this", "here", "specifically", "particularly", 
            "notably", "especially", "specifically"
        ]
        focus_count = sum(1 for word in focus_keywords if word in text_lower)
        focus_bonus = min(0.15, focus_count * 0.03)
        
        if not relevance_indicators:
            # Fallback: base on text length and keyword presence
            base_score = 0.5
        else:
            base_score = sum(relevance_indicators) / len(relevance_indicators)
        
        return min(1.0, max(0.0, base_score + focus_bonus - off_topic_penalty))
    
    async def score_creativity_async(
        self, text: str, llm_provider: LLMProvider
    ) -> float:
        """Score creativity using LLM with improved prompt (returns 1-5 scale, normalized to 0-1)."""
        try:
            prompt = (
                "You are an expert evaluator of creative writing in the style of Rick & Morty. "
                "Rate the creativity and narrative style of this summary on a scale of 1-5:\n\n"
                "Scoring criteria:\n"
                "- 1-2: Generic, boring, lacks personality\n"
                "- 3: Somewhat engaging but missing the irreverent Rick & Morty tone\n"
                "- 4: Good creativity and style, captures some of the show's humor\n"
                "- 5: Excellent creativity, perfectly captures Rick & Morty's sarcastic, "
                "irreverent, and darkly comedic tone\n\n"
                f"Summary to evaluate:\n{text}\n\n"
                "Respond with only a single number (1-5)."
            )
            
            response = await llm_provider.generate(prompt)
            
            # Extract number from response
            match = re.search(r'\b([1-5])\b', response.strip())
            if match:
                score_1_5 = float(match.group(1))
                # Normalize to 0-1 scale (1->0.2, 5->1.0)
                normalized = (score_1_5 - 1) / 4.0
                logger.info(f"LLM creativity score: {score_1_5}/5 = {normalized:.2f}")
                return normalized
            else:
                # Fallback to heuristic if LLM response is unclear
                logger.warning(f"Could not parse LLM creativity score from: {response}")
                return self._compute_creativity_score(text)
        except Exception as e:
            logger.error(f"Error in async creativity scoring: {e}")
            # Fallback to heuristic
            return self._compute_creativity_score(text)
