"""Background job queue for async scoring."""
import asyncio
from typing import Any
from collections import deque
from shared.logging import logger


class JobQueue:
    """In-memory job queue for background processing."""
    
    def __init__(self):
        self.queue: deque[dict[str, Any]] = deque()
        self.running = False
    
    def enqueue(self, job: dict[str, Any]) -> None:
        """Add a job to the queue."""
        self.queue.append(job)
        logger.info(f"Enqueued job: {job.get('type')} for {job.get('entityType')}/{job.get('entityId')}")
    
    def dequeue(self) -> dict[str, Any] | None:
        """Get next job from queue."""
        if len(self.queue) == 0:
            return None
        return self.queue.popleft()
    
    def start_worker(self, process_job: callable) -> None:
        """Start background worker that processes jobs every 200ms."""
        if self.running:
            return
        
        self.running = True
        
        async def worker_loop():
            while self.running:
                job = self.dequeue()
                if job:
                    try:
                        await process_job(job)
                    except Exception as e:
                        logger.error(f"Error processing job: {e}", exc_info=True)
                
                await asyncio.sleep(0.2)  # 200ms interval
        
        # Start worker task
        asyncio.create_task(worker_loop())
        logger.info("Job queue worker started")
    
    def stop_worker(self) -> None:
        """Stop background worker."""
        self.running = False
        logger.info("Job queue worker stopped")


# Global job queue instance
job_queue = JobQueue()

