from __future__ import annotations

from rag.chunker import build_chunks_from_pages, chunk_text


def test_chunk_text_creates_overlap():
    text = " ".join([f"word-{index}" for index in range(1, 301)])
    chunks = chunk_text(text, chunk_size=50, overlap=10)
    assert len(chunks) >= 2
    assert chunks[0].startswith("word-1")
    assert chunks[0].split()[-1] == "word-50"


def test_build_chunks_from_pages_preserves_page_metadata():
    pages = [{"page_number": 1, "text": "alpha beta gamma delta epsilon"}]
    chunks = build_chunks_from_pages(pages, chunk_size=3, overlap=1)
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["chunk_index"] == 1
    assert chunks[0]["token_count"] >= 1
