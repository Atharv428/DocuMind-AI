from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path
from typing import Iterable

import pymupdf as fitz

from .config import settings


def normalize_text(raw_text: str) -> str:
    """Clean and normalize extracted text: NFC unicode, strip control characters, normalize whitespace."""
    if not raw_text:
        return ""
    # Strip null bytes and non-printable control characters except newline and tab
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw_text)
    # Unicode NFC normalization
    normalized = unicodedata.normalize("NFC", cleaned)
    # Collapse 3+ consecutive newlines into 2
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def validate_pdf(file_path: str | Path, max_size_mb: int | None = None) -> None:
    path = Path(file_path)
    if not path.exists():
        raise ValueError(f"File '{path.name}' does not exist.")
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files (.pdf) are supported.")
    limit = max_size_mb or settings.max_file_size_mb
    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise ValueError("The uploaded PDF is empty (0 bytes).")
    max_bytes = limit * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValueError(f"File size ({size_bytes / (1024 * 1024):.1f} MB) exceeds the {limit} MB size limit.")

    # Check PDF magic bytes (%PDF)
    try:
        with open(path, "rb") as file_obj:
            header = file_obj.read(5)
            if not header.startswith(b"%PDF"):
                raise ValueError("Invalid PDF file: Missing standard '%PDF' file header.")
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError(f"Could not read PDF file header: {exc}") from exc


def compute_sha256(file_path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(file_path, "rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pdf_pages(file_path: str | Path) -> list[dict]:
    path = Path(file_path)
    validate_pdf(path)
    try:
        doc = fitz.open(path)
    except Exception as exc:
        raise ValueError(f"Unable to parse PDF '{path.name}'. The file may be damaged or corrupted: {exc}") from exc

    try:
        if doc.is_encrypted:
            raise ValueError("The PDF document is password-protected. Please decrypt it before uploading.")
        if doc.page_count == 0:
            raise ValueError("The PDF file contains 0 pages.")

        pages: list[dict] = []
        for page_number in range(doc.page_count):
            page = doc.load_page(page_number)
            raw_text = page.get_text("text", sort=True)
            text = normalize_text(raw_text)
            if text:
                pages.append({"page_number": page_number + 1, "text": text})
    finally:
        doc.close()

    if not pages:
        raise ValueError(
            "No extractable text was found in this PDF. The document may be scanned or image-only (OCR is required)."
        )
    return pages


def build_document_record(file_path: str | Path) -> dict:
    path = Path(file_path)
    file_hash = compute_sha256(path)
    page_texts = extract_pdf_pages(path)

    # Get total page count safely
    try:
        doc = fitz.open(path)
        total_pages = doc.page_count
        doc.close()
    except Exception:
        total_pages = len(page_texts)

    return {
        "document_id": file_hash,
        "filename": path.name,
        "file_size": path.stat().st_size,
        "page_count": total_pages,
        "extractable_pages": len(page_texts),
        "hash": file_hash,
        "pages": page_texts,
    }
