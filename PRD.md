# Product Requirements Document

## Problem
Product and growth practitioners need fast, trustworthy answers from Lenny's Podcast without manually searching hundreds of transcripts. They also need to turn evidence into publishable writing and simple visual artifacts.

## Target User
Product managers, growth leaders, founders, and operators researching product strategy and communicating what they learned.

## Success Metrics
- Relevant questions return grounded answers with inspectable transcript sources.
- Users can route one conversation into knowledge answers, Ship30-style essays, or HTML artifacts.
- A fresh Docker setup reaches a usable chat UI without cloud credentials.
- Automated tests cover routing, persistence, retrieval boundaries, and artifact safety.

## Scope
Included: React chat, FastAPI API, PostgreSQL/pgvector, transcript ingestion, semantic retrieval, Ollama, optional Claude Agent SDK provider, deterministic skill routing, essay generation, sanitized HTML artifacts, and sandboxed preview.

Excluded: authentication, multi-user authorization, arbitrary code execution, external artifact hosting, and production cloud deployment.

## User Flows
1. User opens the frontend and receives a persisted session.
2. User asks a podcast knowledge question and receives an answer plus sources.
3. User asks for an essay and receives generated writing grounded in retrieved context.
4. User asks for an HTML artifact and receives a preview in a sandboxed iframe.
5. If the provider or database fails, the request returns a safe error and does not persist a partial turn.

## Acceptance Criteria
- `/api/chat` returns answer, skill, route reason, sources, and optional artifact.
- RAG retrieval excludes low-similarity unsupported context.
- Routing is deterministic and test-covered.
- Artifact output cannot execute scripts, inline event handlers, external resources, or iframes in the preview.
- Ollama remains the default provider.
- Docker services have health checks and the backend tests run in the container.

## Risks
- Local Ollama latency can make generation slow.
- Transcript quality and embedding similarity affect answer quality.
- The optional Claude SDK requires a separately authenticated Claude Code environment.
- The current application has no authentication or per-user authorization.

## Implementation Plan
1. Foundation and persistence.
2. Ingestion and pgvector retrieval.
3. Ollama provider and grounded RAG.
4. GrowthAgent, skills, and deterministic routing.
5. Artifact viewer, tests, and documentation.
6. Final Docker and end-to-end validation.
