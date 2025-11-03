.PHONY: setup backend frontend install init-db seed run-backend run-frontend help

help:
	@echo "Rick & Morty AI Challenge - Make Commands"
	@echo ""
	@echo "  make setup       - Full setup (backend + frontend)"
	@echo "  make backend     - Setup backend only"
	@echo "  make frontend    - Setup frontend only"
	@echo "  make init-db     - Initialize database"
	@echo "  make seed        - Seed vector embeddings"
	@echo "  make run-backend - Start backend server"
	@echo "  make run-frontend - Start frontend server"
	@echo ""

setup: backend frontend init-db
	@echo "✅ Setup complete!"

backend:
	@echo "Setting up backend..."
	cd backend && python3 -m venv venv || true
	cd backend && . venv/bin/activate && pip install -q --upgrade pip && pip install -q -r requirements.txt
	@if [ ! -f backend/.env ]; then \
		echo "Creating backend/.env template..."; \
		cp backend/.env.example backend/.env 2>/dev/null || echo "⚠️  Please create backend/.env with your OPENAI_API_KEY"; \
	fi
	@echo "✅ Backend setup complete"

frontend:
	@echo "Setting up frontend..."
	cd frontend && npm install --silent
	@if [ ! -f frontend/.env.local ]; then \
		echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local; \
	fi
	@echo "✅ Frontend setup complete"

init-db:
	@echo "Initializing database..."
	cd backend && . venv/bin/activate && python3 scripts/init_db.py
	@echo "✅ Database initialized"

seed:
	@echo "Seeding vector embeddings (this will use OpenAI API credits)..."
	cd backend && . venv/bin/activate && python3 scripts/seed_embeddings.py
	@echo "✅ Embeddings seeded"

run-backend:
	@echo "Starting backend server..."
	cd backend && . venv/bin/activate && uvicorn main:app --reload

run-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

