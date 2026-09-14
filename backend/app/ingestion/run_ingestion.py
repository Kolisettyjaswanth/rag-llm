import os
from pathlib import Path

from app.db.database import SessionLocal
from app.ingestion.chunker import chunk_transcript
from app.ingestion.cleaner import clean_transcript
from app.ingestion.embedder import TranscriptEmbedder
from app.ingestion.loader import load_transcript
from app.ingestion.repository import save_transcript


TRANSCRIPTS_ROOT = Path(
    os.getenv("TRANSCRIPTS_ROOT", "/app/lenny_transcripts")
)


def ingest_episode(file_path: Path) -> None:
    print(f"Processing: {file_path}")

    transcript = load_transcript(file_path)
    cleaned = clean_transcript(transcript.transcript)
    chunks = chunk_transcript(cleaned)

    embedder = TranscriptEmbedder()
    embeddings = embedder.embed_texts(chunks)

    db = SessionLocal()

    try:
        document = save_transcript(
            db,
            transcript,
            chunks,
            embeddings,
        )

        print(f"Document ID: {document.id}")
        print(f"Chunks: {len(chunks)}")
        print(f"Completed: {transcript.title}")
    finally:
        db.close()


def main() -> None:
    transcript_files = sorted(
        TRANSCRIPTS_ROOT.glob("*/transcript.md")
    )

    print(f"Found {len(transcript_files)} transcript files")

    if not transcript_files:
        raise RuntimeError("No transcript files found")

    for transcript_file in transcript_files:
     ingest_episode(transcript_file)


if __name__ == "__main__":
    main()