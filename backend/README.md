# KrishiMitra AI Backend

Production-ready FastAPI backend for KrishiMitra AI.

## Stack

- Python 3.11
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- PostgreSQL
- Alembic migrations
- JWT authentication
- bcrypt password hashing
- Docker and Docker Compose

## Project Layout

app/
- api/ (versioned endpoints)
- core/ (settings, security, logging)
- db/ (engine, session, base metadata)
- models/ (SQLAlchemy models)
- schemas/ (Pydantic request/response models)
- services/ (business logic)
- utils/ (shared helpers)

## Local Setup

1. Create environment file from template:
   - Copy .env.example to .env
2. Install dependencies:
   - pip install -r requirements.txt
3. Run API:
   - uvicorn app.main:app --reload

API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Setup

1. Copy .env.example to .env
2. Start services:
   - docker compose up --build

## Migrations

Create a new migration:
- alembic revision --autogenerate -m "init"

Apply migrations:
- alembic upgrade head

Rollback one migration:
- alembic downgrade -1

## API Endpoints

- GET /api/v1/health
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me
