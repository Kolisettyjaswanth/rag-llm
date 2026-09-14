from app.ingestion.retriever import TranscriptRetriever
from app.services.rag_service import RAGService


class FakeEmbedder:
    def embed_text(self, text):
        return [0.1, 0.2, 0.3]


class FakeMappings:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def mappings(self):
        return FakeMappings(self.rows)


class FakeDatabase:
    def __init__(self, rows):
        self.rows = rows
        self.params = None
        self.sql = None

    def execute(self, sql, params):
        self.sql = str(sql)
        self.params = params
        filtered = [
            row
            for row in self.rows
            if row["similarity"] >= params["min_similarity"]
        ]
        return FakeResult(filtered[: params["top_k"]])


def make_row(similarity):
    return {
        "id": "chunk-1",
        "document_id": "document-1",
        "content": "Transcript evidence",
        "chunk_index": 2,
        "chunk_metadata": {
            "guest": "Guest",
            "title": "Episode",
            "youtube_url": "https://youtube.example/episode",
        },
        "similarity": similarity,
    }


def make_retriever():
    retriever = TranscriptRetriever.__new__(TranscriptRetriever)
    retriever.embedder = FakeEmbedder()
    return retriever


def test_relevant_similarity_returns_source_row():
    db = FakeDatabase([make_row(0.82)])

    results = make_retriever().search(db, "onboarding")

    assert len(results) == 1
    assert results[0]["document_id"] == "document-1"
    assert results[0]["similarity"] == 0.82
    assert db.params["min_similarity"] == 0.45
    assert "embedding <=>" in db.sql


def test_similarity_below_threshold_is_excluded():
    db = FakeDatabase([make_row(0.44)])

    results = make_retriever().search(db, "unsupported topic")

    assert results == []


def test_unrelated_query_returns_no_supporting_sources():
    service = RAGService.__new__(RAGService)
    service.retriever = type("EmptyRetriever", (), {"search": lambda *args, **kwargs: []})()

    result = service.retrieve(db=None, question="Mars colonization")

    assert result["sources"] == []
    assert result["context"] == ""


def test_retrieval_source_metadata_is_preserved():
    service = RAGService.__new__(RAGService)
    service.retriever = type(
        "SourceRetriever",
        (),
        {"search": lambda *args, **kwargs: [make_row(0.8)]},
    )()

    result = service.retrieve(db=None, question="onboarding")

    assert result["sources"][0]["chunk_id"] == "chunk-1"
    assert result["sources"][0]["document_id"] == "document-1"
    assert result["sources"][0]["guest"] == "Guest"
    assert "Transcript evidence" in result["context"]
