import asyncio
import os

from app.llm.provider import LLMProvider


class ClaudeAgentExecutor(LLMProvider):
    """Claude Agent SDK execution path used by GrowthAgent when selected."""

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:
        return asyncio.run(self._generate(prompt, system_prompt))

    async def _generate(
        self,
        prompt: str,
        system_prompt: str | None,
    ) -> str:
        try:
            from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, query
        except ImportError as exc:
            raise RuntimeError(
                "claude-agent-sdk is required for LLM_PROVIDER=claude-agent-sdk"
            ) from exc

        options = ClaudeAgentOptions(
            system_prompt=system_prompt,
            model=os.getenv("CLAUDE_MODEL") or None,
            max_turns=1,
            allowed_tools=[],
        )
        text_blocks: list[str] = []

        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                text_blocks.extend(
                    block.text
                    for block in message.content
                    if hasattr(block, "text") and block.text
                )

        answer = "\n".join(text_blocks).strip()
        if not answer:
            raise RuntimeError("Claude Agent SDK returned an empty response")
        return answer
