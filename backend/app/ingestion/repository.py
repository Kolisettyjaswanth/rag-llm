from sqlalchemy.orm import Session

from app.db.models import Chunk, Document
from app.ingestion.loader import Transcript


def save_transcript(
    db: Session,
    transcript: Transcript,
    chunks: list[str],
    embeddings: list[list[float]],
) -> Document:
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Chunk count ({len(chunks)}) does not match "
            f"embedding count ({len(embeddings)})"
        )

    source = transcript.youtube_url or transcript.source_path

    existing_document = (
        db.query(Document)
        .filter(Document.source == source)
        .first()
    )

    if existing_document is not None:
        db.delete(existing_document)
        db.flush()

    document = Document(
        title=transcript.title[:255],
        source=source,
    )

    db.add(document)
    db.flush()

    for index, (content, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        chunk = Chunk(
            document_id=document.id,
            content=content,
            chunk_index=index,
            chunk_metadata={
                "guest": transcript.guest,
                "title": transcript.title,
                "youtube_url": transcript.youtube_url,
                "video_id": transcript.video_id,
                "publish_date": transcript.publish_date,
                "description": transcript.description,
                "duration": transcript.duration,
                "duration_seconds": transcript.duration_seconds,
                "view_count": transcript.view_count,
                "channel": transcript.channel,
                "keywords": transcript.keywords,
                "source_path": transcript.source_path,
            },
            embedding=embedding,
        )
        db.add(chunk)

    db.commit()
    db.refresh(document)

    return document