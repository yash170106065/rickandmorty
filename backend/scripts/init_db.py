"""Initialize database schema."""
import asyncio
import aiosqlite
import os
from pathlib import Path


async def init_database():
    """Initialize database with schema."""
    # Get schema file
    script_dir = Path(__file__).parent
    schema_path = script_dir.parent / "infrastructure" / "db" / "schema.sql"
    
    # Database path
    db_dir = script_dir.parent / "data"
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / "app.db"
    
    print(f"Initializing database at {db_path}")
    
    # Read schema
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Execute schema
    async with aiosqlite.connect(db_path) as conn:
        await conn.executescript(schema_sql)
        await conn.commit()
    
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(init_database())

