import asyncio
import sys
import types

from app.agent.agent import GrowthAgent
from app.agent.executor import ClaudeAgentExecutor
from app.agent.router import AgentRouter
from app.agent.skills.artifact_skill import ArtifactSkill
from app.agent.skills.rag_skill import RAGSkill
from app.agent.skills.ship30_skill import Ship30Skill


class RecordingSkill:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeRAGService:
    def __init__(self):
        self.sources = [
            {
                "chunk_id": "chunk-1",
                "document_id": "document-1",
                "chunk_index": 0,
                "content": "A supporting transcript excerpt.",
                "similarity": 0.8,
                "guest": "Guest",
                "title": "Episode",
            }
        ]

    def answer(self, **kwargs):
        return {"answer": "Grounded answer", "sources": self.sources}

    def retrieve(self, **kwargs):
        return {"context": "Transcript context", "sources": self.sources}


class FakeLLM:
    def __init__(self, response):
        self.response = response
        self.prompts = []

    def generate(self, prompt, system_prompt=None):
        self.prompts.append((prompt, system_prompt))
        return self.response


def test_router_selects_expected_skills():
    router = AgentRouter()

    assert router.route("What does Lenny say about onboarding?").skill == "rag"
    assert router.route("Write a Ship30 essay about onboarding").skill == "ship30"
    assert router.route("Create an HTML landing page").skill == "artifact"


def test_growth_agent_routes_without_initializing_expensive_dependencies():
    rag = RecordingSkill({"answer": "rag", "sources": []})
    ship30 = RecordingSkill({"answer": "essay", "sources": []})
    artifact = RecordingSkill(
        {
            "answer": "artifact",
            "sources": [],
            "artifact": {"type": "html", "content": "<html></html>"},
        }
    )
    agent = GrowthAgent(
        skills={"rag": rag, "ship30": ship30, "artifact": artifact}
    )

    rag_result = agent.execute(None, "What is product-market fit?")
    essay_result = agent.execute(None, "Write a Ship30 essay about growth")
    artifact_result = agent.execute(None, "Create an HTML dashboard")

    assert rag_result["skill"] == "rag"
    assert essay_result["skill"] == "ship30"
    assert artifact_result["skill"] == "artifact"
    assert len(rag.calls) == 1
    assert len(ship30.calls) == 1
    assert len(artifact.calls) == 1


def test_skills_reuse_rag_context_and_provider():
    rag_service = FakeRAGService()
    llm = FakeLLM("Generated content")

    essay = Ship30Skill(rag_service=rag_service, llm=llm).execute(
        db=None,
        topic="Write about onboarding",
    )
    artifact = ArtifactSkill(rag_service=rag_service, llm=llm).execute(
        db=None,
        request="Create a landing page about onboarding",
    )

    assert essay["sources"] == rag_service.sources
    assert essay["answer"] == "Generated content"
    assert artifact["artifact"]["type"] == "html"
    assert artifact["artifact"]["content"] == "Generated content"
    assert len(llm.prompts) == 2
    assert all("Transcript context" in prompt for prompt, _ in llm.prompts)


def test_artifact_sanitizer_removes_active_and_external_content():
    html = (
        '<html><script>alert(1)</script><img src="https://example.com/a.png" '
        'onerror="alert(2)"><a href="javascript:alert(3)">x</a>'
        '<iframe src="https://example.com"></iframe>'
        '<object data="https://example.com"></object>'
        '<style>@import url(https://example.com/a.css); body { background: url(https://example.com/a.png); }</style></html>'
    )

    sanitized = ArtifactSkill._sanitize(html)

    assert "<script" not in sanitized.lower()
    assert "onerror" not in sanitized.lower()
    assert "javascript:" not in sanitized.lower()
    assert "https://example.com" not in sanitized.lower()
    assert "<iframe" not in sanitized.lower()
    assert "<object" not in sanitized.lower()
    assert "@import" not in sanitized.lower()
    assert "url(" not in sanitized.lower()


def test_artifact_normalizes_fenced_html():
    fenced = "```html\n<!DOCTYPE html><html><style>body { color: red; }</style></html>\n```"

    normalized = ArtifactSkill.normalize_html_artifact(fenced)

    assert normalized.startswith("<!DOCTYPE html>")
    assert normalized.endswith("</html>")
    assert "```" not in normalized


def test_artifact_normalization_preserves_plain_html():
    html = "<!DOCTYPE html><html><body><h1>Hello</h1></body></html>"

    assert ArtifactSkill.normalize_html_artifact(html) == html


def test_artifact_normalization_handles_plain_fence():
    fenced = "```\n<html><body><p>Hello</p></body></html>\n```"

    assert ArtifactSkill.normalize_html_artifact(fenced).startswith("<html>")


def test_claude_agent_executor_uses_sdk_query_and_extracts_text(monkeypatch):
    class FakeTextBlock:
        text = "Claude response"

    class FakeAssistantMessage:
        def __init__(self):
            self.content = [FakeTextBlock()]

    captured = {}

    class FakeOptions:
        def __init__(self, **kwargs):
            captured["options"] = kwargs

    async def fake_query(*, prompt, options):
        captured["prompt"] = prompt
        yield FakeAssistantMessage()

    fake_sdk = types.ModuleType("claude_agent_sdk")
    fake_sdk.AssistantMessage = FakeAssistantMessage
    fake_sdk.ClaudeAgentOptions = FakeOptions
    fake_sdk.query = fake_query
    monkeypatch.setitem(sys.modules, "claude_agent_sdk", fake_sdk)
    monkeypatch.setenv("CLAUDE_MODEL", "test-model")

    result = asyncio.run(
        ClaudeAgentExecutor()._generate("prompt", "system")
    )

    assert result == "Claude response"
    assert captured["prompt"] == "prompt"
    assert captured["options"] == {
        "system_prompt": "system",
        "model": "test-model",
        "max_turns": 1,
        "allowed_tools": [],
    }
