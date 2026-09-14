# Manual UI Test Plan

Run with Docker Compose, Ollama running, and `llama3.1:8b` available.

## 1. Startup and health

- [ ] Open `http://localhost:5173`.
- [ ] Confirm the chat UI loads.
- [ ] Confirm the header reports `Backend connected`.
- [ ] Confirm `GET http://localhost:8000/health` reports database `connected`.

Expected: the empty chat state and composer are usable.

## 2. RAG question

- [ ] Ask: `What does Adam Fishman say about onboarding?`
- [ ] Confirm the answer is labeled `rag`.
- [ ] Confirm a route reason is shown.
- [ ] Confirm transcript source cards appear with excerpts and similarity scores.

Expected: a grounded answer with relevant Adam Fishman sources.

## 3. Ship30 essay

- [ ] Ask: `Write a Ship30 essay about onboarding.`
- [ ] Confirm the answer is labeled `ship30`.
- [ ] Confirm the response is structured long-form writing of approximately the requested essay length.
- [ ] Confirm retrieved sources appear when supporting context is used.

Expected: a grounded essay, not an unsupported generic response.

## 4. HTML artifact

- [ ] Ask: `Create an HTML landing page about onboarding.`
- [ ] Confirm the answer is labeled `artifact`.
- [ ] Expand `View generated artifact`.
- [ ] Confirm a visual webpage renders in the viewer, not raw Markdown fences or HTML source text.
- [ ] Inspect the iframe and confirm it has an empty `sandbox` attribute.

Expected: a self-contained rendered artifact.

## 5. Persistence

- [ ] Send a question.
- [ ] Refresh or reopen the application.
- [ ] Confirm the backend retains the session/messages through the API.

Expected: user and assistant turns are persisted for the session.

## 6. Unsupported or unrelated question

- [ ] Ask an unrelated question such as `What is the capital of Mars?`.
- [ ] Confirm the system does not present fabricated transcript support.

Expected: a no-support answer or clearly qualified response with no irrelevant sources.

## 7. Failure state

- [ ] Stop Ollama temporarily or use an unavailable provider endpoint.
- [ ] Submit a request.
- [ ] Confirm the UI shows a useful error message and exits loading state.

Expected: no permanent spinner and no partial user-only chat turn.
