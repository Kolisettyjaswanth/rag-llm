from sqlalchemy import text
from sqlalchemy.orm import Session

from app.ingestion.embedder import TranscriptEmbedder


class TranscriptRetriever:
    def __init__(self) -> None:
        self.embedder = TranscriptEmbedder()

    def search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.45,
    ) -> list[dict]:
        query_embedding = self.embedder.embed_text(query)

        sql = text(
            """
            SELECT
                c.id,
                c.document_id,
                c.content,
                c.chunk_index,
                c.chunk_metadata,
                1 - (c.embedding <=> CAST(:query_embedding AS vector)) AS similarity
            FROM chunks c
            WHERE c.embedding IS NOT NULL
              AND 1 - (c.embedding <=> CAST(:query_embedding AS vector)) >= :min_similarity
            ORDER BY c.embedding <=> CAST(:query_embedding AS vector)
            LIMIT :top_k
            """
        )

        rows = db.execute(
            sql,
            {
                "query_embedding": str(query_embedding),
                "min_similarity": min_similarity,
                "top_k": top_k,
            },
        ).mappings().all()

        return [dict(row) for row in rows]