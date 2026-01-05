.PHONY: help setup dev stop clean data train test-ml test backend frontend docker-build docker-up docker-down lint format

# Default target
help:
	@echo "🚀 Bravola Mini SaaS - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Initial project setup"
	@echo "  make docker-build   - Build Docker containers"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start all services (backend + frontend + DB)"
	@echo "  make backend        - Start backend only"
	@echo "  make frontend       - Start frontend only"
	@echo "  make stop           - Stop all services"
	@echo ""
	@echo "ML Pipeline:"
	@echo "  make data           - Generate synthetic data"
	@echo "  make train          - Train all ML models locally"
	@echo "  make test-ml        - Test model inference"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean temporary files"
	@echo "  make logs           - View Docker logs"

# Initial setup
setup:
	@chmod +x setup_project.sh
	@./setup_project.sh

# Start all services
dev:
	@echo "🚀 Starting Bravola Mini SaaS..."
	@docker-compose up -d postgres redis
	@sleep 3
	@make backend & make frontend

# Backend only
backend:
	@echo "🐍 Starting FastAPI backend..."
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend only
frontend:
	@echo "⚛️  Starting React frontend..."
	@cd frontend && npm run dev

# Stop services
stop:
	@echo "⏸️  Stopping services..."
	@docker-compose down
	@pkill -f "uvicorn app.main:app" || true
	@pkill -f "vite" || true

# ML Pipeline Commands
data:
	@echo "📊 Generating synthetic data..."
	@cd backend && source venv/bin/activate && python scripts/generate_data.py

train:
	@echo "🤖 Training ML models..."
	@cd backend && source venv/bin/activate && python scripts/train_local.py

test-ml:
	@echo "🧪 Testing model inference..."
	@cd backend && source venv/bin/activate && python scripts/test_inference.py

# Testing
test:
	@echo "🧪 Running tests..."
	@cd backend && source venv/bin/activate && pytest tests/ -v --cov=app

test-watch:
	@cd backend && source venv/bin/activate && pytest-watch

# Code quality
lint:
	@echo "🔍 Running linters..."
	@cd backend && source venv/bin/activate && flake8 app/ && black --check app/
	@cd frontend && npm run lint

format:
	@echo "✨ Formatting code..."
	@cd backend && source venv/bin/activate && black app/ && isort app/
	@cd frontend && npm run format

# Docker commands
docker-build:
	@echo "🐳 Building Docker containers..."
	@docker-compose build

docker-up:
	@echo "🐳 Starting Docker containers..."
	@docker-compose up -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	@docker-compose down

docker-logs:
	@docker-compose logs -f

# Database commands
db-migrate:
	@cd backend && source venv/bin/activate && alembic upgrade head

db-rollback:
	@cd backend && source venv/bin/activate && alembic downgrade -1

db-revision:
	@cd backend && source venv/bin/activate && alembic revision --autogenerate -m "$(msg)"

db-reset:
	@docker-compose down -v
	@docker-compose up -d postgres
	@sleep 5
	@make db-migrate

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf backend/.coverage 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Production build
build-prod:
	@echo "🏗️  Building for production..."
	@cd frontend && npm run build
	@docker-compose -f docker-compose.prod.yml build

# Deploy (example)
deploy:
	@echo "🚀 Deploying to production..."
	@docker-compose -f docker-compose.prod.yml up -d
