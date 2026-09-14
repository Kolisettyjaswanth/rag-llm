# Design

## Principles
The interface is quiet, source-first, and optimized for scanning. Generated content is clearly separated from evidence. Controls remain usable while the model is working, and failures explain what the user can do next.

## Information Architecture
The app has one primary workspace: the chat. Each assistant response may contain routing metadata, transcript sources, and an artifact preview. Sessions and messages remain persisted by the backend.

## Chat Experience
Users enter a question or generation request in the composer. User messages appear on the right; assistant responses appear on the left. A small skill badge identifies `rag`, `ship30`, or `artifact`, while the route reason provides concise transparency.

## Sources
RAG and writing responses show expandable source cards with guest, episode, excerpt, similarity, and episode link. Sources are returned by the API rather than inferred by the frontend.

## Artifact Viewer
HTML artifacts are rendered with `iframe srcDoc` and an empty sandbox attribute. The backend strips common scripts, event handlers, dangerous URL schemes, external resource attributes, CSS imports/URLs, and embedded active-content elements before returning the artifact. This is defense-in-depth, not a claim of perfect sanitization.

## States
- Empty: suggested questions provide a useful starting point.
- Loading: animated dots and disabled composer prevent duplicate requests.
- Degraded: the header shows backend status and failed chat requests receive a clear assistant message.
- No evidence: RAG and essay skills state that supporting transcript information was insufficient.

## Responsive Behavior
The chat panel fills the available viewport, message widths contract on small screens, and the composer remains a single usable row with a compact send control.

## Accessibility
The chat section has an accessible label, the composer input has a label, source excerpts use native details/summary controls, loading content has screen-reader text, and artifact iframes have descriptive titles.

## Design Decisions
The existing chat UI was retained to avoid disrupting working workflows. Agent metadata is additive, source cards remain unchanged, and artifacts are opt-in expandable content rather than a separate route.
