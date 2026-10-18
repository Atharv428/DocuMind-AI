from __future__ import annotations

import pymupdf as fitz
import pytest

from rag.generator import GeminiGenerator
from rag.pipeline import RAGPipeline
from rag.vector_store import ChromaVectorStore


class MockRetriever:
    def __init__(self, hits):
        self.hits = hits

    def retrieve(self, query_embedding, top_k=4, document_filter=None):
        return self.hits


def test_local_rag_mode_without_llm():
    """Verify that when no LLM is configured, RAG returns real citations and clear local notice."""
    pipeline = object.__new__(RAGPipeline)
    pipeline.embedding_service = type(
        "EmbeddingStub",
        (),
        {"embed_query": lambda self, q: [0.1, 0.2]},
    )()
    mock_hits = [
        {
            "text": "Quarterly earnings grew by 15% year-over-year.",
            "document_id": "doc-financial",
            "filename": "q3_report.pdf",
            "page_number": 4,
            "chunk_index": 2,
            "chunk_id": "doc-financial-p4-c2",
            "distance": 0.08,
        }
    ]
    pipeline.retriever = MockRetriever(mock_hits)
    pipeline.generator = GeminiGenerator(api_key="")  # Unconfigured/unavailable

    result = pipeline.answer_question("What was the earnings growth?", ["doc-financial"])

    # 1. Answer clearly states local passage retrieval mode without fake AI claims
    assert "Local Passage Retrieval Mode" in result["answer"]
    assert len(result["citations"]) == 1

    # 2. Authentic citations from document with filename and page number
    citation = result["citations"][0]
    assert citation["filename"] == "q3_report.pdf"
    assert citation["page_number"] == 4
    assert "Quarterly earnings grew" in citation["text"]


def test_local_mode_summary_and_compare_fallback():
    """Verify that document summary and compare succeed locally without crashing."""
    pipeline = object.__new__(RAGPipeline)
    pipeline.generator = GeminiGenerator(api_key="")

    summary = pipeline.summarize_document("This is a test document with several words describing RAG architecture.", "test.pdf")
    assert "test.pdf" in summary
    assert "Local Mode" in summary

    comparison = pipeline.compare_documents("Compare?", ["Summary A", "Summary B"])
    assert "Local Mode" in comparison
    assert "Comparing 2 documents" in comparison


def test_gemini_generator_sanitizes_api_key():
    """Verify that API keys are never exposed in error messages."""
    secret_key = "AIzaSySecretKeyNeverExpose12345"
    generator = GeminiGenerator(api_key=secret_key)

    error_with_key = f"Failed to connect using key {secret_key}: Invalid credentials"
    sanitized = generator._sanitize_error(error_with_key)

    assert secret_key not in sanitized
    assert "[API_KEY_HIDDEN]" in sanitized


def test_gemini_check_access_without_key():
    """Verify that check_access reports cleanly when no key is configured."""
    generator = GeminiGenerator(api_key="")
    success, msg = generator.check_access()
    assert success is False
    assert "No Gemini API key configured" in msg
