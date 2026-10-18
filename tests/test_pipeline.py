from __future__ import annotations

from rag.pipeline import RAGPipeline


class FakeRetriever:
    def retrieve(self, query_embedding, top_k=4, document_filter=None):
        return [
            {
                "text": "The product launch was successful.",
                "document_id": "doc-1",
                "filename": "launch.pdf",
                "page_number": 3,
                "chunk_index": 1,
                "chunk_id": "doc-1-p3-c1",
                "distance": 0.12,
            }
        ]


class FakeGenerator:
    def generate(self, question, context_chunks):
        return "This is grounded in the source text."


def test_answer_question_returns_citations(monkeypatch):
    pipeline = object.__new__(RAGPipeline)
    pipeline.embedding_service = type(
        "EmbeddingStub",
        (),
        {"embed_query": lambda self, question: [0.1, 0.2], "embed_texts": lambda self, texts: [[0.1, 0.2] for _ in texts]},
    )()
    pipeline.retriever = FakeRetriever()
    pipeline.generator = FakeGenerator()

    result = pipeline.answer_question("What happened?", ["doc-1"])

    assert result["answer"] == "This is grounded in the source text."
    assert result["citations"][0]["filename"] == "launch.pdf"
    assert result["citations"][0]["page_number"] == 3
