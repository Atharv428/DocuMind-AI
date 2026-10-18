from __future__ import annotations

from typing import Any

import chromadb

from .config import settings


class ChromaVectorStore:
    def __init__(self, collection_name: str = "documind_documents"):
        self.client = chromadb.PersistentClient(path=str(settings.chroma_path))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, records: list[dict], embeddings: list[list[float]]) -> None:
        if not records or not embeddings:
            return
        self.collection.upsert(
            ids=[record["chunk_id"] for record in records],
            documents=[record["text"] for record in records],
            embeddings=embeddings,
            metadatas=[
                {
                    "document_id": record["document_id"],
                    "filename": record["filename"],
                    "page_number": record["page_number"],
                    "chunk_index": record["chunk_index"],
                    "chunk_id": record["chunk_id"],
                }
                for record in records
            ],
        )

    def query(
        self,
        query_embedding: list[float],
        k: int = 4,
        document_filter: str | list[str] | None = None,
    ) -> dict[str, Any]:
        total_items = self.count()
        if total_items == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        if document_filter is None:
            where_clause = None
        elif isinstance(document_filter, list):
            if not document_filter:
                return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            if len(document_filter) == 1:
                where_clause = {"document_id": document_filter[0]}
            else:
                where_clause = {"document_id": {"$in": document_filter}}
        else:
            where_clause = {"document_id": str(document_filter)}

        n_results = max(1, min(k, total_items))
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
            where=where_clause,
        )

    def delete_document(self, document_id: str) -> None:
        if not document_id:
            return
        try:
            self.collection.delete(where={"document_id": str(document_id)})
        except Exception:
            # Fallback if where filter requires direct comparison
            try:
                self.collection.delete(where={"document_id": {"$eq": str(document_id)}})
            except Exception:
                pass

    def delete_collection(self) -> None:
        self.client.delete_collection(name=self.collection.name)

    def count(self) -> int:
        return self.collection.count()
