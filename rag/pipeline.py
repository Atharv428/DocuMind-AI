from __future__ import annotations

from typing import Any

from .chunker import build_chunks_from_pages
from .config import settings
from .document_loader import build_document_record
from .embeddings import EmbeddingService
from .generator import GeminiGenerator, OllamaGenerator, UnifiedGenerator
from .retriever import Retriever
from .vector_store import ChromaVectorStore


class RAGPipeline:
    def __init__(self, embedding_model: str | None = None, provider: str | None = None):
        self.embedding_service = EmbeddingService(model_name=embedding_model or settings.embedding_model)
        self.vector_store = ChromaVectorStore()
        self.retriever = Retriever(self.vector_store)
        self.generator = UnifiedGenerator(provider=provider or settings.llm_provider)

    def index_document(self, file_path: str, document_id: str | None = None) -> dict[str, Any]:
        record = build_document_record(file_path)
        document_id = document_id or record["document_id"]
        chunks = build_chunks_from_pages(record["pages"], chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
        if not chunks:
            raise ValueError("No valid chunks were produced from the uploaded document.")

        chunk_records: list[dict[str, Any]] = []
        for chunk in chunks:
            chunk_records.append(
                {
                    "document_id": document_id,
                    "filename": record["filename"],
                    "page_number": chunk["page_number"],
                    "chunk_index": chunk["chunk_index"],
                    "chunk_id": f"{document_id}-p{chunk['page_number']}-c{chunk['chunk_index']}",
                    "text": chunk["text"],
                }
            )

        embeddings = self.embedding_service.embed_texts([item["text"] for item in chunk_records])
        self.vector_store.add_documents(chunk_records, embeddings)
        return {
            "document_id": document_id,
            "filename": record["filename"],
            "pages": record["page_count"],
            "chunks": len(chunk_records),
            "file_size": record["file_size"],
        }

    def answer_question(self, question: str, selected_document_ids: list[str] | None = None) -> dict[str, Any]:
        if selected_document_ids is not None and len(selected_document_ids) == 0:
            return {
                "answer": "No documents are currently selected. Please select at least one document from the library or sidebar to query.",
                "citations": [],
                "sources": [],
            }

        query_embedding = self.embedding_service.embed_query(question)
        document_filter = None if not selected_document_ids else selected_document_ids
        hits = self.retriever.retrieve(query_embedding, top_k=settings.top_k, document_filter=document_filter)
        if not hits:
            return {
                "answer": "The uploaded documents do not provide enough information to answer that question reliably.",
                "citations": [],
                "sources": [],
            }

        citations = [
            {
                "document_id": hit.get("document_id"),
                "filename": hit.get("filename"),
                "page_number": hit.get("page_number"),
                "chunk_index": hit.get("chunk_index"),
                "chunk_id": hit.get("chunk_id"),
                "text": hit.get("text"),
                "distance": hit.get("distance"),
            }
            for hit in hits
        ]

        generator_available = False
        if hasattr(self.generator, "is_available"):
            generator_available = self.generator.is_available()
        elif hasattr(self.generator, "generate"):
            generator_available = True

        if generator_available:
            try:
                context_texts = [hit["text"] for hit in hits]
                answer = self.generator.generate(question, context_texts)
            except Exception as exc:
                err_str = str(exc)
                if getattr(self.generator, "api_key", None) and self.generator.api_key in err_str:
                    err_str = err_str.replace(self.generator.api_key, "[API_KEY_HIDDEN]")
                answer = (
                    f"⚠️ **AI Engine Notice**: {err_str}\n\n"
                    f"**Local Passage Retrieval Mode (Active)**:\n"
                    f"Found {len(hits)} matching passage{'s' if len(hits) != 1 else ''} in your indexed documents. "
                    f"Review the exact matching passages and citations below."
                )
        else:
            answer = (
                f"**Local Passage Retrieval Mode (No LLM required)**\n\n"
                f"Found {len(hits)} matching passage{'s' if len(hits) != 1 else ''} for your question in the uploaded document{'s' if len(hits) != 1 else ''}. "
                f"Review the exact source passages with page citations below."
            )

        return {
            "answer": answer,
            "citations": citations,
            "sources": citations,
        }

    def summarize_document(self, document_text: str, title: str = "Document") -> str:
        generator_available = False
        if hasattr(self.generator, "is_available"):
            generator_available = self.generator.is_available()
        elif hasattr(self.generator, "generate"):
            generator_available = True

        if generator_available:
            try:
                return self.generator.summarize_document(document_text, title)
            except Exception:
                pass

        words = document_text.split()
        word_count = len(words)
        preview_text = " ".join(words[:120]) + ("..." if word_count > 120 else "")
        return (
            f"**{title} — Document Overview (Local Mode)**\n\n"
            f"- **Word count**: ~{word_count:,} words\n"
            f"- **Character count**: {len(document_text):,} characters\n\n"
            f"**First Section Excerpt:**\n> {preview_text}\n\n"
            f"*(Start Ollama or configure Gemini API to enable AI-synthesized summaries.)*"
        )

    def compare_documents(self, question: str, summaries: list[str]) -> str:
        generator_available = False
        if hasattr(self.generator, "is_available"):
            generator_available = self.generator.is_available()
        elif hasattr(self.generator, "generate"):
            generator_available = True

        if generator_available:
            try:
                return self.generator.compare_documents(question, summaries)
            except Exception:
                pass

        return (
            f"**Document Comparison (Local Mode)**\n\n"
            f"Comparing {len(summaries)} documents.\n\n"
            f"*(Start Ollama or configure Gemini API to enable AI-powered comparison.)*"
        )
