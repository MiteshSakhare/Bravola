# Bravola Mini SaaS - Backend

FastAPI backend with ML-powered growth marketing engines.

## Features

- **FastAPI** - Modern async Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - Async ORM
- **ML Engines** - Discovery, Benchmark, Strategy, Feedback
- **Integrations** - Shopify & Klaviyo APIs
- **Authentication** - JWT-based auth

## Setup

Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Copy environment file
cp .env.example .env

Run migrations
alembic upgrade head

Generate synthetic data
python scripts/generate_data.py

Train ML models
python scripts/train_local.py

Test inference
python scripts/test_inference.py

Start server
uvicorn app.main:app --reload

text

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

backend/
├── app/
│ ├── api/ # API endpoints
│ ├── core/ # Core config
│ ├── models/ # Database models
│ ├── schemas/ # Pydantic schemas
│ ├── discovery/ # Discovery engine
│ ├── benchmark/ # Benchmark engine
│ ├── strategy/ # Strategy engine
│ ├── feedback/ # Feedback engine
│ ├── integrations/ # External APIs
│ └── ml/ # ML utilities
├── scripts/ # Data & training scripts
└── tests/ # Test suite

text

## Testing

Run tests
pytest

With coverage
pytest --cov=app tests/

Watch mode
pytest-watch

text
undefined
