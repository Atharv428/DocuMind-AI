from __future__ import annotations

import tempfile
from pathlib import Path

import pymupdf as fitz
import pytest

from rag.document_loader import build_document_record, extract_pdf_pages, validate_pdf
from rag.generator import GeminiGenerator
from rag.pipeline import RAGPipeline
from rag.vector_store import ChromaVectorStore
from services.chat_service import ChatService
from services.document_service import DocumentService


def test_validate_pdf_rejects_empty_file(tmp_path):
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    with pytest.raises(ValueError, match="empty"):
        validate_pdf(empty_file)


def test_validate_pdf_rejects_corrupted_header(tmp_path):
    bad_file = tmp_path / "corrupt.pdf"
    bad_file.write_bytes(b"NOT A REAL PDF FILE CONTENTS")
    with pytest.raises(ValueError, match="Invalid PDF file"):
        validate_pdf(bad_file)


def test_extract_pdf_pages_preserves_page_numbers(tmp_path):
    pdf_path = tmp_path / "multipage.pdf"
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "First page content about science.")
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Second page content about mathematics.")
    doc.save(pdf_path)
    doc.close()

    pages = extract_pdf_pages(pdf_path)
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "First page" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Second page" in pages[1]["text"]

    record = build_document_record(pdf_path)
    assert record["page_count"] == 2
    assert record["document_id"] == record["hash"]


def test_vector_store_empty_filter_safety(tmp_path):
    store = ChromaVectorStore(collection_name="test_safety_coll")
    # Empty query should return structured empty dict without exception
    res = store.query([0.1] * 384, k=4, document_filter=[])
    assert res["documents"] == [[]]


def test_document_lifecycle_and_deletion(tmp_path):
    doc_service = DocumentService(storage_path=tmp_path / "documents.json")
    doc_meta = {
        "document_id": "test-doc-id-123",
        "filename": "sample_doc.pdf",
        "file_size": 1024,
        "page_count": 1,
        "status": "Indexed",
        "hash": "test-doc-id-123",
    }
    doc_service.add_document(doc_meta)
    assert len(doc_service.list_documents()) == 1
    assert doc_service.find_by_hash("test-doc-id-123") is not None
    assert doc_service.get_document("test-doc-id-123") is not None

    doc_service.delete_document("test-doc-id-123")
    assert len(doc_service.list_documents()) == 0
    assert doc_service.find_by_hash("test-doc-id-123") is None


def test_chat_service_dynamic_titles_and_cleanup(tmp_path):
    chat_svc = ChatService(storage_path=tmp_path / "chats.json")
    session = chat_svc.create_session("New chat")
    sid = session["session_id"]

    # First user message should rename session title dynamically
    chat_svc.add_message(sid, "user", "What are the sales figures for Q3?")
    updated = chat_svc.get_session(sid)
    assert "sales figures" in updated["title"].lower()

    # Empty sessions cleanup
    empty_s = chat_svc.create_session("New chat")
    assert len(chat_svc.list_sessions()) == 2
    chat_svc.clear_empty_sessions(keep_session_id=sid)
    assert len(chat_svc.list_sessions()) == 1
