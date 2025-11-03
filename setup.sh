#!/bin/bash

# Rick & Morty AI Challenge - Setup Script

set -e

echo "🚀 Setting up Rick & Morty AI Challenge..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Found Python $PYTHON_VERSION${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Found Node.js $NODE_VERSION${NC}"
echo ""

# Backend Setup
echo -e "${YELLOW}📦 Setting up backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo -e "${GREEN}✅ Backend dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Creating .env file template...${NC}"
    cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key_here
RICK_AND_MORTY_API_URL=https://rickandmortyapi.com/api
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
ENABLE_VECTOR_STORE=true
EMBEDDING_MODEL=text-embedding-3-small
EOF
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your OPENAI_API_KEY${NC}"
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi

# Initialize database
echo "Initializing database..."
python3 scripts/init_db.py

echo -e "${GREEN}✅ Database initialized${NC}"

cd ..

# Frontend Setup
echo ""
echo -e "${YELLOW}📦 Setting up frontend...${NC}"
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --silent
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Frontend dependencies already installed${NC}"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✅ .env.local created${NC}"
else
    echo -e "${GREEN}✅ .env.local exists${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your OPENAI_API_KEY"
echo "2. (Optional) Seed embeddings: cd backend && python3 scripts/seed_embeddings.py"
echo "3. Start backend: cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "4. Start frontend: cd frontend && npm run dev"
echo ""
echo "Backend will run on http://localhost:8000"
echo "Frontend will run on http://localhost:3000"

