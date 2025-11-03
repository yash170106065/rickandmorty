"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import locations, characters, episodes, generation, search
from shared.config import settings
from shared.logging import logger


app = FastAPI(
    title="Rick & Morty AI Challenge",
    description="AI-powered Rick & Morty data service",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Version 1
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/v1", tags=["v1"])

api_v1.include_router(locations.router)
api_v1.include_router(characters.router)
api_v1.include_router(episodes.router)
api_v1.include_router(generation.router)
api_v1.include_router(search.router)

app.include_router(api_v1)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup():
    """Initialize on startup."""
    logger.info("Starting Rick & Morty AI Challenge API")
    # Initialize database if needed
    import os
    os.makedirs("data", exist_ok=True)
    
    # Start background job queue worker
    from infrastructure.workers.job_queue import job_queue
    from api.deps import get_generation_service
    
    async def process_job(job: dict):
        """Process a job from the queue."""
        generation_service = get_generation_service()
        if job.get("type") == "FINALIZE_GENERATION":
            await generation_service._finalize_generation_job(job)
        elif job.get("type") == "SCORE_GENERATED_CONTENT":
            await generation_service._score_generated_content_job(job)
    
    job_queue.start_worker(process_job)
    logger.info("Background job queue worker started")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )

