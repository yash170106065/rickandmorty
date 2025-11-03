# Quick Start Guide

## Step 1: Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
```

Initialize database:
```bash
python scripts/init_db.py
```

Start server:
```bash
uvicorn main:app --reload
```

## Step 2: Frontend Setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start dev server:
```bash
npm run dev
```

## Step 3: (Optional) Seed Vector Store

For semantic search to work, seed embeddings:
```bash
cd backend
python scripts/seed_embeddings.py
```

This fetches all characters and creates embeddings. Takes a few minutes.

## Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Features to Try

1. **Locations**: Browse `/locations` to see all locations
2. **Location Summary**: Click a location, then "Generate Summary" for AI-powered summaries with evaluation scores
3. **Character Notes**: Visit any character and add notes
4. **Semantic Search**: Use `/search` to find characters by description (requires embeddings seeding)

