# Local Setup Guide

Complete step-by-step guide to set up the Rick & Morty AI Universe Explorer on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

### Verify Prerequisites

```bash
# Check Python version
python3 --version  # Should be 3.12 or higher

# Check Node.js version
node --version  # Should be 18 or higher

# Check npm version
npm --version
```

## Quick Setup (Recommended)

The fastest way to get started is using the provided Makefile:

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd rickandmorty

# Run full setup
make setup

# Initialize database
make init-db

# (Optional) Seed embeddings for semantic search
make seed
```

Then start the servers:

```bash
# Terminal 1: Backend
make run-backend

# Terminal 2: Frontend
make run-frontend
```

## Manual Setup

If you prefer to set up manually or need more control over the process:

### Step 1: Backend Setup

#### 1.1 Create Virtual Environment

```bash
cd backend
python3 -m venv venv
```

#### 1.2 Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

#### 1.3 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 1.4 Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
touch .env  # On Windows: type nul > .env
```

Add the following content:

```env
# Required: OpenAI API Key
OPENAI_API_KEY=sk-your-actual-api-key-here

# Optional: Customize these if needed
RICK_AND_MORTY_API_URL=https://rickandmortyapi.com/api
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Vector Store Configuration
ENABLE_VECTOR_STORE=true
EMBEDDING_MODEL=text-embedding-3-small
```

**⚠️ Important:** Replace `sk-your-actual-api-key-here` with your actual OpenAI API key.

#### 1.5 Initialize Database

```bash
# Make sure you're in the backend directory with venv activated
python scripts/init_db.py
```

This creates the SQLite database at `backend/data/app.db` with all necessary tables.

#### 1.6 Verify Backend Setup

```bash
python scripts/verify_setup.py
```

You should see:
```
✅ Config module imports correctly
✅ Core models import correctly
✅ API client imports correctly
✅ Repository imports correctly
✅ LLM provider imports correctly
✅ Services import correctly
```

#### 1.7 Start Backend Server

```bash
# Using uvicorn directly
uvicorn main:app --reload

# Or using Python
python main.py
```

The backend should start at `http://localhost:8000`

**Verify it's working:**
- Visit http://localhost:8000/docs for API documentation
- Visit http://localhost:8000/health for health check

### Step 2: Frontend Setup

#### 2.1 Install Dependencies

```bash
cd frontend
npm install
```

#### 2.2 Configure Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
touch .env.local  # On Windows: type nul > .env.local
```

Add the following content:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### 2.3 Start Frontend Server

```bash
npm run dev
```

The frontend should start at `http://localhost:3000`

### Step 3: Seed Vector Embeddings (Optional)

For semantic search to work properly, you need to seed the vector store with embeddings:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python scripts/seed_embeddings.py
```

**Note:** This script:
- Fetches all characters from the Rick & Morty API
- Generates embeddings using OpenAI
- Stores them in the SQLite database
- **This will consume OpenAI API credits** (costs ~$0.10-0.50 depending on volume)
- Takes 5-15 minutes depending on your connection

You can skip this step if you only want to test other features. Semantic search will be unavailable until embeddings are seeded.

## Verification Checklist

After setup, verify everything is working:

- [ ] Backend server running at http://localhost:8000
- [ ] Frontend server running at http://localhost:3000
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can navigate to http://localhost:3000 and see the landing page
- [ ] Database file exists at `backend/data/app.db`
- [ ] (Optional) Semantic search works (requires embeddings)

## Troubleshooting

### Backend Issues

**Issue: `ModuleNotFoundError`**
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

**Issue: `OPENAI_API_KEY not found`**
- Ensure `.env` file exists in `backend/` directory
- Check that the file contains `OPENAI_API_KEY=sk-...`
- Restart the backend server after creating/updating `.env`

**Issue: `Database locked`**
- Close any other processes accessing the database
- Delete `backend/data/app.db` and run `python scripts/init_db.py` again

**Issue: Port 8000 already in use**
- Change `API_PORT` in `backend/.env` to another port (e.g., 8001)
- Update `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to match

### Frontend Issues

**Issue: `Cannot connect to backend`**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Check browser console for CORS errors (shouldn't happen with default config)

**Issue: `Module not found` errors**
```bash
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**Issue: Port 3000 already in use**
```bash
# Use a different port
PORT=3001 npm run dev
```

### Semantic Search Issues

**Issue: Search returns no results**
- Ensure embeddings have been seeded: `python scripts/seed_embeddings.py`
- Check that OpenAI API key is valid and has credits
- Verify embeddings table exists: check `backend/data/app.db`

**Issue: Search is slow**
- This is normal for the first few queries (cold start)
- SQLite vector search is not optimized for large datasets
- See [FUTURE_IMPROVEMENTS.md](FUTURE_IMPROVEMENTS.md) for production solutions

## Development Tips

### Hot Reloading

Both frontend and backend support hot reloading:
- **Backend**: Started with `--reload` flag (automatic with `make run-backend`)
- **Frontend**: Next.js hot reloading is enabled by default

### Database Reset

To reset the database and start fresh:

```bash
cd backend
rm data/app.db
source venv/bin/activate
python scripts/init_db.py
```

### Viewing Database

You can use SQLite command-line tool or GUI:

```bash
# Command line
sqlite3 backend/data/app.db

# Recommended GUI tools:
# - DB Browser for SQLite (https://sqlitebrowser.org/)
# - DBeaver (https://dbeaver.io/)
```

### Logging

Backend logs are printed to console. For more detailed logging:
- Check `backend/shared/logging.py` for configuration
- Logs include request/response info, errors, and job queue status

## Next Steps

Once setup is complete:

1. **Explore the Application**
   - Visit http://localhost:3000
   - Browse locations, characters, and episodes
   - Try generating AI summaries

2. **Read the Documentation**
   - [Technical Decisions](TECH_DECISIONS.md) - Understand the architecture
   - [Feature Documentation](features/) - Learn about each feature
   - [Tradeoffs](TRADEOFFS.md) - Understand technology choices

3. **Customize**
   - Modify API endpoints in `backend/api/routers/`
   - Customize UI in `frontend/components/`
   - Adjust evaluation metrics in `backend/infrastructure/evaluation/`

## Getting Help

If you encounter issues not covered here:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review error messages in browser console (F12) and terminal
3. Check API documentation at http://localhost:8000/docs
4. Open an issue on GitHub with:
   - Your operating system
   - Python/Node versions
   - Error messages
   - Steps to reproduce

---

**Ready to explore the multiverse?** Visit http://localhost:3000 and start your journey! 🚀

