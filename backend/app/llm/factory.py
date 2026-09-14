import os

from app.llm.huggingface_provider import HuggingFaceProvider
from app.llm.claude_agent_provider import ClaudeAgentProvider
from app.llm.ollama_provider import OllamaProvider
from app.llm.provider import LLMProvider


def get_llm_provider() -> LLMProvider:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "ollama":
        return OllamaProvider()

    if provider in {"huggingface", "hf"}:
        return HuggingFaceProvider()

    if provider in {"claude", "claude-agent-sdk"}:
        return ClaudeAgentProvider()

    raise ValueError(f"Unsupported LLM provider: {provider}")
