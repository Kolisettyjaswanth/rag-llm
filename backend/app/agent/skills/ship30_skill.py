from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.services.rag_service import RAGService
    from app.llm.provider import LLMProvider


class Ship30Skill:
    name = "ship30"

    def __init__(
        self,
        rag_service: "RAGService | None" = None,
        llm: "LLMProvider | None" = None,
    ) -> None:
        if rag_service is None:
            from app.services.rag_service import RAGService

            rag_service = RAGService()

        if llm is None:
            from app.llm.factory import get_llm_provider

            llm = get_llm_provider()

        self.rag_service = rag_service
        self.llm = llm

    def execute(
        self,
        db: Session,
        topic: str,
    ) -> dict:
        retrieval = self.rag_service.retrieve(
            db=db,
            question=topic,
            top_k=5,
        )

        if not retrieval["sources"]:
            return {
                "answer": (
                    "I couldn't find sufficient supporting information "
                    "in Lenny's Podcast knowledge base to write this essay."
                ),
                "sources": [],
            }

        system_prompt = """You are the Ship30 for 30 writing skill for Lenny Growth Assistant.

Create an approximately 1,250-word essay grounded ONLY in the supplied Lenny's Podcast transcript context.

Writing requirements:
- Start with a strong hook.
- Build a clear narrative progression.
- Use useful headings.
- Use bullets where they improve scanability.
- Use selective bold emphasis.
- End with a specific, practical takeaway.
- Do not invent facts, quotes, guests, companies, statistics, or experiences.
- Do not attribute a claim to a guest unless the supplied transcript context supports it.
- Every substantive claim must be grounded in the supplied transcript context.
- If the evidence is insufficient for a claim, omit the claim.
"""

        prompt = f"""Topic:
{topic}

Transcript context:
{retrieval["context"]}

Write the essay now.
"""

        answer = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return {
            "answer": answer,
            "sources": retrieval["sources"],
        }
