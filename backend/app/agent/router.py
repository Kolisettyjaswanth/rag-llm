from dataclasses import dataclass


@dataclass(frozen=True)
class AgentRoute:
    skill: str
    reason: str


class AgentRouter:
    def route(self, message: str) -> AgentRoute:
        text = message.lower().strip()

        artifact_terms = (
            "html",
            "css",
            "artifact",
            "webpage",
            "landing page",
            "visual artifact",
            "dashboard",
            "render",
            "component",
        )

        ship30_terms = (
            "ship 30",
            "ship30",
            "essay",
            "article",
            "write a post",
            "write an essay",
            "linkedin post",
        )

        if any(term in text for term in artifact_terms):
            return AgentRoute(
                skill="artifact",
                reason="The request asks for a rendered or HTML/CSS artifact.",
            )

        if any(term in text for term in ship30_terms):
            return AgentRoute(
                skill="ship30",
                reason="The request asks for long-form or Ship30-style written content.",
            )

        return AgentRoute(
            skill="rag",
            reason="The request is a product or growth knowledge question.",
        )
