from __future__ import annotations

from typing import Any


class Retriever:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def retrieve(
        self,
        query_embedding: list[float],
        top_k: int = 4,
        document_filter: str | list[str] | None = None,
    ) -> list[dict[str, Any]]:
        raw_result = self.vector_store.query(query_embedding=query_embedding, k=top_k, document_filter=document_filter)
        hits: list[dict[str, Any]] = []
        for idx, document in enumerate(raw_result.get("documents", [[]])[0]):
            metadata = (raw_result.get("metadatas", [[]])[0][idx]) if raw_result.get("metadatas") else {}
            hits.append(
                {
                    "text": document,
                    "document_id": metadata.get("document_id"),
                    "filename": metadata.get("filename"),
                    "page_number": metadata.get("page_number"),
                    "chunk_index": metadata.get("chunk_index"),
                    "chunk_id": metadata.get("chunk_id"),
                    "distance": (raw_result.get("distances", [[]])[0][idx]) if raw_result.get("distances") else None,
                }
            )
        return hits
