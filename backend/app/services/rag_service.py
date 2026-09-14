from sqlalchemy.orm import Session

from app.ingestion.retriever import TranscriptRetriever
from app.llm.factory import get_llm_provider


class RAGService:
    def __init__(self, llm=None) -> None:
        self.retriever = TranscriptRetriever()
        self.llm = llm or get_llm_provider()

    def retrieve(
        self,
        db: Session,
        question: str,
        top_k: int = 5,
    ) -> dict:
        results = self.retriever.search(
            db=db,
            query=question,
            top_k=top_k,
        )

        sources = []

        for result in results:
            metadata = result.get("chunk_metadata") or {}

            sources.append(
                {
                    "chunk_id": str(result["id"]),
                    "document_id": str(result["document_id"]),
                    "chunk_index": result["chunk_index"],
                    "content": result["content"],
                    "similarity": float(result["similarity"]),
                    "guest": metadata.get("guest"),
                    "title": metadata.get("title"),
                    "youtube_url": metadata.get("youtube_url"),
                    "video_id": metadata.get("video_id"),
                    "publish_date": metadata.get("publish_date"),
                }
            )

        context = "\n\n".join(
            (
                f"Source {index + 1}\n"
                f"Guest: {source['guest']}\n"
                f"Episode: {source['title']}\n"
                f"Content:\n{source['content']}"
            )
            for index, source in enumerate(sources)
        )

        return {
            "question": question,
            "context": context,
            "sources": sources,
        }

    def answer(
        self,
        db: Session,
        question: str,
        top_k: int = 5,
    ) -> dict:
        retrieval = self.retrieve(
            db=db,
            question=question,
            top_k=top_k,
        )

        if not retrieval["sources"]:
            return {
                "answer": "I couldn't find sufficient supporting information in Lenny's transcript knowledge base.",
                "sources": [],
            }

        system_prompt = """You are Lenny Growth Assistant.

Answer the user's question using only the provided Lenny's Podcast transcript context.

Rules:
- Ground every factual claim in the provided context.
- Do not invent information.
- If the context does not contain enough information, say so.
- Give a clear, useful answer.
- Mention the relevant guest or episode when useful.
- Do not claim that Lenny or a guest said something unless the provided transcript context supports it.
"""

        prompt = f"""User question:
{question}

Transcript context:
{retrieval["context"]}

Answer the question using only this transcript context.
"""

        answer = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )

        return {
            "answer": answer,
            "sources": retrieval["sources"],
        }