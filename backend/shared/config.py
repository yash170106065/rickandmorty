"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Configuration
    openai_api_key: str
    
    # Rick & Morty API
    rick_and_morty_api_url: str = "https://rickandmortyapi.com/api"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    # Vector Store
    enable_vector_store: bool = True
    embedding_model: str = "text-embedding-3-small"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

