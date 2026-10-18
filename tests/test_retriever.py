from __future__ import annotations

from rag.retriever import Retriever


class FakeVectorStore:
    def query(self, query_embedding, k=4, document_filter=None):
        return {
            "documents": [["first hit", "second hit"]],
            "metadatas": [[{"document_id": "doc-1", "filename": "one.pdf", "page_number": 2, "chunk_index": 1, "chunk_id": "doc-1-1"}, {"document_id": "doc-2", "filename": "two.pdf", "page_number": 4, "chunk_index": 2, "chunk_id": "doc-2-2"}]],
            "distances": [[0.12, 0.33]],
        }


def test_retriever_returns_hit_metadata():
    hits = Retriever(FakeVectorStore()).retrieve([0.1, 0.2], top_k=2)
    assert len(hits) == 2
    assert hits[0]["document_id"] == "doc-1"
    assert hits[0]["filename"] == "one.pdf"
    assert hits[1]["page_number"] == 4
