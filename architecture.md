# Architecture

## System
```text
React + Vite
  -> POST /api/chat
FastAPI routes
  -> GrowthAgent
      -> AgentRouter
      -> RAGSkill       -> RAGService -> Retriever -> PostgreSQL/pgvector
      -> Ship30Skill   -> RAGService + LLM execution
      -> ArtifactSkill -> RAGService + LLM execution
  -> PostgreSQL messages
  -> Ollama by default, optional Claude Agent SDK/Hugging Face providers
```

## Boundaries
- `api`: HTTP schemas, validation, persistence, and transaction boundaries.
- `agent`: deterministic routing and skill orchestration.
- `services`: shared RAG behavior.
- `ingestion`: loading, cleaning, chunking, embedding, persistence, retrieval.
- `llm`: provider interface and configured implementations.
- `frontend`: chat presentation, source display, and sandboxed artifact preview.

## Database Schema
`users` own `sessions`; `sessions` own `messages`. `documents` own `chunks`. Chunks contain transcript metadata and 384-dimensional pgvector embeddings. Alembic owns schema changes.

## API
- `GET /health`: service and database status.
- `POST /api/sessions`: create a session.
- `GET /api/sessions/{id}`: retrieve a session.
- `GET /api/sessions/{id}/messages`: list session messages.
- `POST /api/sessions/{id}/messages`: persist a message.
- `POST /api/chat`: route a request, generate an answer, persist the turn, and return sources/metadata/artifact.

## Ingestion
Compose mounts the host transcript directory at `/app/lenny_transcripts`. The ingestion command discovers `*/transcript.md`, cleans timestamps, chunks text, creates normalized MiniLM embeddings, and replaces an existing document with the same source before saving the new document/chunks.

## Retrieval
The query is embedded with the same MiniLM model. PostgreSQL orders chunks by vector distance and filters results below the configured similarity threshold. RAG context includes only returned transcript excerpts and metadata.

## Agent Routing
`AgentRouter` lowercases and trims input, then checks artifact terms first, essay terms second, and defaults to RAG. `GrowthAgent` creates the selected skill lazily. Ollama uses the existing local provider. Claude mode creates `ClaudeAgentExecutor` in the application agent layer; that executor invokes `claude_agent_sdk.query()` with `ClaudeAgentOptions`.

## Skills
`RAGSkill` delegates to the existing `RAGService`. `Ship30Skill` reuses retrieval and asks the selected LLM executor for grounded structured writing. `ArtifactSkill` reuses retrieval, normalizes fenced model output, requests self-contained HTML without JavaScript or external resources, then applies defense-in-depth sanitization.

## Providers
`LLM_PROVIDER=ollama` is the default and uses `OLLAMA_BASE_URL` and `OLLAMA_MODEL`. `claude-agent-sdk` is optional and uses the installed SDK/Claude Code authentication outside the application. Hugging Face remains optional and requires its environment configuration.

## Security
Secrets are read from environment variables and `.env` is ignored. No provider credential is printed. Artifact generation strips common active/external content and the frontend uses a sandboxed iframe; this is defense-in-depth rather than a perfect sanitizer. The application is not an authenticated multi-tenant system.

## Docker
PostgreSQL starts with a pgvector image and health check. Backend waits for PostgreSQL, exposes `/health`, and has its own health check. Frontend depends on backend startup and exposes Vite on port 5173. The transcript mount is configurable with `TRANSCRIPTS_HOST_PATH` and is read-only.
