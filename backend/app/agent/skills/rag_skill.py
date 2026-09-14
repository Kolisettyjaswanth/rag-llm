from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from app.services.rag_service import RAGService


class RAGSkill:
    name = "rag"

    def __init__(
        self,
        rag_service: "RAGService | None" = None,
    ) -> None:
        if rag_service is None:
            from app.services.rag_service import RAGService

            rag_service = RAGService()

        self.rag_service = rag_service

    def execute(
        self,
        db: Session,
        question: str,
    ) -> dict:
        return self.rag_service.answer(
            db=db,
            question=question,
            top_k=5,
        )
