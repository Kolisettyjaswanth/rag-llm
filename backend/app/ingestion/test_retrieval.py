from app.db.database import SessionLocal
from app.ingestion.retriever import TranscriptRetriever


def main() -> None:
    db = SessionLocal()

    try:
        retriever = TranscriptRetriever()

        results = retriever.search(
            db,
            "What does Adam Fishman say about onboarding?",
            top_k=5,
        )

        print("Results:", len(results))

        for index, result in enumerate(results, start=1):
            print(f"\n--- Result {index} ---")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Chunk index: {result['chunk_index']}")
            print(result["content"][:500])

    finally:
        db.close()


if __name__ == "__main__":
    main()