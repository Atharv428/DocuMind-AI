from __future__ import annotations

import pymupdf as fitz

from rag.document_loader import build_document_record


def test_build_document_record_extracts_pages(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page_1 = doc.new_page()
    page_1.insert_text((72, 72), "Alpha beta gamma.")
    page_2 = doc.new_page()
    page_2.insert_text((72, 72), "Delta epsilon zeta.")
    doc.save(pdf_path)
    doc.close()

    record = build_document_record(pdf_path)

    assert record["filename"] == "sample.pdf"
    assert record["page_count"] == 2
    assert record["pages"][0]["page_number"] == 1
    assert "Alpha" in record["pages"][0]["text"]
    assert "Delta" in record["pages"][1]["text"]
