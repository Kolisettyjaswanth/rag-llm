import os

from sqlalchemy.orm import Session

from app.agent.executor import ClaudeAgentExecutor
from app.agent.router import AgentRouter
from app.agent.skills.artifact_skill import ArtifactSkill
from app.agent.skills.rag_skill import RAGSkill
from app.agent.skills.ship30_skill import Ship30Skill


class GrowthAgent:
    def __init__(
        self,
        router: AgentRouter | None = None,
        skills: dict[str, object] | None = None,
    ) -> None:
        self.router = router or AgentRouter()
        self.skills = skills or {}

    def execute(
        self,
        db: Session,
        message: str,
    ) -> dict:
        route = self.router.route(message)
        skill = self.skills.get(route.skill)

        if skill is None:
            llm = self._create_llm()
            from app.services.rag_service import RAGService

            rag_service = RAGService(llm=llm)

            if route.skill == "rag":
                skill = RAGSkill(rag_service=rag_service)
            elif route.skill == "ship30":
                skill = Ship30Skill(rag_service=rag_service, llm=llm)
            elif route.skill == "artifact":
                skill = ArtifactSkill(rag_service=rag_service, llm=llm)
            else:
                raise ValueError(f"Unsupported agent skill: {route.skill}")

        if route.skill == "rag":
            result = skill.execute(db=db, question=message)
        elif route.skill == "ship30":
            result = skill.execute(db=db, topic=message)
        else:
            result = skill.execute(db=db, request=message)

        return {
            "skill": route.skill,
            "route_reason": route.reason,
            **result,
        }

    @staticmethod
    def _create_llm():
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()

        if provider in {"claude", "claude-agent-sdk"}:
            return ClaudeAgentExecutor()

        from app.llm.factory import get_llm_provider

        return get_llm_provider()
