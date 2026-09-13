# Lenny Growth Assistant

This repository currently contains the original Streamlit-based RAG implementation as a preserved legacy reference, while the Phase 1 foundation for the new architecture is being established alongside it.

## Current implementation

The project now includes:

- React + TypeScript frontend foundation
- FastAPI backend foundation
- PostgreSQL database foundation
- Docker Compose setup for local development
- backend health check endpoint
- basic automated backend test

## Planned later phases

- Lenny transcript ingestion
- RAG and retrieval layer
- PostgreSQL + pgvector integration
- sessions/messages persistence
- agent layer
- Ollama and cloud LLM support
- Ship30 for 30 skill work
- artifact generation
- artifact viewer

## Architecture (Phase 1)

```text
React frontend
      ↓
FastAPI backend
      ↓
PostgreSQL
      ↓
Docker Compose
```

## Legacy implementation preserved

The original Streamlit application remains in place:

- app/app.py
- app/functions.py

This is intentionally kept untouched for later migration and reuse of the RAG logic.

## Local setup

1. Copy .env.example to .env
2. Run:

```bash
docker compose up --build
```

3. Open the frontend at:

- http://localhost:5173

4. Check the backend health endpoint at:

- http://localhost:8000/health

## Stop services

```bash
docker compose down
```

## Phase 1 validation

The project includes a minimal health check test for the backend. Run:

```bash
cd backend
python -m pytest tests/test_health.py
```

## Phase 2 - Database Persistence

The project now includes the Phase 2 persistence foundation for PostgreSQL-backed session and message storage.

### Database schema

- users
- sessions
- messages
- documents
- chunks

The chunk table includes a pgvector-compatible embedding column prepared for later retrieval and RAG work.

### Technologies used

- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL + pgvector
- FastAPI persistence routes

### Migration workflow

```bash
docker compose exec backend alembic upgrade head
```

### Relevant API endpoints

```text
POST /api/sessions
GET /api/sessions/{session_id}
GET /api/sessions/{session_id}/messages
POST /api/sessions/{session_id}/messages
```

### Test workflow

```bash
docker compose exec backend python -m pytest tests/test_persistence.py -q
```

### Notes

This does not implement RAG, embedding generation, vector similarity search, or later agent features. Those remain planned for future phases.

## Notes

This is not a complete end-to-end assessment implementation yet; it is the Phase 1 project foundation only. Later phases will add ingestion, RAG, agent orchestration, and document/artifact workflows.