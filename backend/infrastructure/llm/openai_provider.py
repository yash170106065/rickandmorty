"""OpenAI LLM provider implementation."""
from openai import AsyncOpenAI
from core.ports import LLMProvider
from shared.config import settings
from shared.logging import logger


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.embedding_model = settings.embedding_model
    
    async def generate(
        self, prompt: str, system_prompt: str | None = None
    ) -> str:
        """Generate text from a prompt."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding vector for text."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

