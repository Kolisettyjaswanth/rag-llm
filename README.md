# Lenny Growth Assistant

A Dockerized React and FastAPI application for grounded Lenny's Podcast research, Ship30-style essay generation, and self-contained HTML artifacts.

## Features

- React + TypeScript chat UI
- FastAPI API with persistent sessions and messages
- PostgreSQL with pgvector
- 272 ingested transcript documents and 31,595 stored chunks in the current local database
- Semantic retrieval with a 0.45 similarity threshold
- Deterministic RAG, Ship30, and artifact skills
- Ollama as the default local LLM
- Optional Claude Agent SDK and Hugging Face provider paths
- Source cards with transcript excerpts and episode links
- Sandboxed artifact viewer
- Docker health checks and automated backend tests

## Architecture

```text
React + Vite
    |
    v
FastAPI /api/chat
    |
    v
GrowthAgent -> AgentRouter -> RAGSkill / Ship30Skill / ArtifactSkill
    |                              |
    |                              v
    |                       RAGService + LLM execution
    |                              |
    v                              v
PostgreSQL + pgvector       Ollama by default
                             optional Claude Agent SDK / Hugging Face
```

The legacy Streamlit implementation remains in `app/` as a reference. The active application is the React/FastAPI stack.

## Technology Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, SQLAlchemy, Alembic
- Database: PostgreSQL 16 with pgvector
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`, 384 dimensions
- Local LLM: Ollama, default model `llama3.1:8b`
- Optional cloud/provider paths: Claude Agent SDK and Hugging Face

## Prerequisites and Windows Setup

Install Docker Desktop with WSL2 integration and install Ollama on Windows.

Pull the default model:

```powershell
ollama pull llama3.1:8b
ollama list
```

Keep Ollama running on the host. Docker reaches it through `host.docker.internal`.

Copy the environment template:

```powershell
Copy-Item .env.example .env
```

Set `TRANSCRIPTS_HOST_PATH` to the host directory whose immediate child directories contain `transcript.md` files. The container sees that directory as `/app/lenny_transcripts`.

## Environment Variables

Local defaults are documented in `.env.example`:

- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `FRONTEND_ORIGIN`
- `VITE_API_BASE_URL`
- `TRANSCRIPTS_HOST_PATH`
- `LLM_PROVIDER`, default `ollama`
- `OLLAMA_BASE_URL`, default `http://host.docker.internal:11434`
- `OLLAMA_MODEL`, default `llama3.1:8b`
- `CLAUDE_MODEL`, optional
- `HF_TOKEN` and `HF_MODEL`, optional when Hugging Face is selected

Do not commit `.env` or real provider credentials.

## Docker Startup

```powershell
docker compose up -d --build
docker compose ps
```

Open:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health: http://localhost:8000/health

Stop the stack:

```powershell
docker compose down
```

## Database and Migrations

```powershell
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

The schema contains `users`, `sessions`, `messages`, `documents`, and `chunks`. Chunks contain JSON transcript metadata and 384-dimensional embeddings.

## Transcript Ingestion

The mounted transcript structure must be:

```text
/app/lenny_transcripts/<episode-directory>/transcript.md
```

The ingestion command discovers `*/transcript.md`, cleans timestamps, chunks transcripts, creates normalized MiniLM embeddings, and saves documents/chunks. Existing documents with the same source are deleted and recreated; this is replacement ingestion, not a transactional upsert.

```powershell
docker compose exec backend python -m app.ingestion.run_ingestion
```

The transcript dataset is intentionally ignored by Git.

## RAG Behavior

A query is embedded with the same MiniLM model used during ingestion. PostgreSQL orders chunks using pgvector cosine distance and excludes rows below similarity `0.45`. Returned excerpts and metadata are passed to the LLM. If no supporting sources remain, the service returns a no-support answer without calling the LLM.

## Agent Routing and Skills

`AgentRouter` lowercases and trims the message, then routes in this order:

1. Artifact: `html`, `css`, `webpage`, `landing page`, `visual artifact`, `dashboard`, `render`, or `component`.
2. Ship30: `ship30`, `ship 30`, `essay`, `article`, `write a post`, `write an essay`, or `linkedin post`.
3. RAG: all other product and growth questions.

`RAGSkill` delegates to the existing `RAGService`. `Ship30Skill` retrieves transcript context and requests an approximately 1,250-word grounded essay. `ArtifactSkill` retrieves context, requests self-contained HTML/CSS, normalizes fenced model output, and applies server-side defense-in-depth sanitization.

## Artifact Viewer and Security

The API returns artifacts separately from the answer. The frontend renders HTML with `iframe srcDoc` and an empty `sandbox` attribute.

The server removes common active/external content including scripts, iframes, objects, embeds, forms, event handlers, resource attributes, CSS imports, and CSS `url(...)` references. This is defense-in-depth, not a complete HTML security boundary. Generated content is restricted by the prompt and iframe sandbox, but the application is not a general-purpose HTML sanitizer or hostile-content execution environment.

## Claude Agent SDK and Cloud Providers

Ollama remains the default and requires no cloud credential:

```text
LLM_PROVIDER=ollama
```

When `LLM_PROVIDER=claude-agent-sdk` or `claude` is selected, `GrowthAgent` creates `ClaudeAgentExecutor` from the application agent layer. That executor calls `claude_agent_sdk.query()` with `ClaudeAgentOptions`. Claude authentication and any required Claude Code installation are external prerequisites; Claude mode is not expected to work without them.

The Hugging Face provider is also optional and requires `HF_TOKEN` when selected. No cloud provider is required for the default demo.

## API

- `GET /health`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/sessions/{session_id}/messages`
- `POST /api/chat`

Chat response shape:

```json
{
  "message_id": "uuid",
  "answer": "...",
  "sources": [],
  "skill": "rag",
  "route_reason": "...",
  "artifact": null
}
```

Chat requests are transactional. Provider, retrieval, or persistence failure returns `503` and rolls back the in-progress turn.

## Tests and Frontend Build

Run all backend tests in the authoritative Docker environment:

```powershell
docker compose exec backend python -m pytest -q
```

Run focused tests:

```powershell
docker compose exec backend python -m pytest tests/test_agent.py tests/test_retrieval.py -q
```

Build the frontend:

```powershell
Push-Location frontend
npm install
npm run build
Pop-Location
```

Use [MANUAL_TEST_PLAN.md](MANUAL_TEST_PLAN.md) for evaluator-facing UI checks.

## Troubleshooting

- Backend unhealthy: inspect `docker compose logs backend` and confirm PostgreSQL health.
- Ollama errors: confirm Ollama is running, `ollama list` contains `llama3.1:8b`, and the backend uses `http://host.docker.internal:11434`.
- No transcripts: verify `TRANSCRIPTS_HOST_PATH` points to a directory with immediate child directories containing `transcript.md`.
- Provider settings seem unchanged: rebuild the backend after changing `.env` with `docker compose up -d --build backend`.
- Artifact is blank or text-only: inspect the returned artifact content and model output; the viewer is sandboxed and server sanitization may remove unsupported resources.
- Slow responses: embedding initialization and local Ollama generation can take time on the first request.

## Repository and No-Secrets Policy

Do not commit `.env`, API keys, tokens, passwords, transcript data, vector stores, `node_modules`, or build output. `.env.example` contains local development defaults only. The project has no production authentication or multi-tenant authorization.

See [PRD.md](PRD.md), [design.md](design.md), [architecture.md](architecture.md), [MANUAL_TEST_PLAN.md](MANUAL_TEST_PLAN.md), and [agent_logs/2026-09-14-phase4-10.md](agent_logs/2026-09-14-phase4-10.md).
