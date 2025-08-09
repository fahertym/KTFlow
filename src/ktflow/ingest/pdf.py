# ruff: noqa: E402
from __future__ import annotations

"""PDF ingestion utilities.

This module provides a robust text extractor for PDF files. It prefers
``pdfminer.six`` and falls back to the ``pdftotext`` CLI when available. If
extracted text is too sparse, it can also attempt Tesseract OCR on rendered
page images. A minimal ingest log with simple density info can be saved.
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path

MIN_TEXT_LEN = 200


def _normalize_text(raw: str) -> str:
    """Normalize unicode and collapse excessive whitespace.

    - Converts Windows/Mac newlines to ``\n`` implicitly via Python strings
    - Replaces non-breaking spaces with regular spaces
    - Collapses runs of whitespace (including newlines) to single spaces
    - Strips leading/trailing spaces
    """
    # Replace non-breaking space and similar with a normal space
    text = raw.replace("\u00a0", " ")
    # Collapse any whitespace run to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_with_pdfminer(path: Path) -> str | None:
    """Try extracting text with pdfminer.six.

    Returns the normalized text on success, or ``None`` if pdfminer is not
    available or extraction fails.
    """
    try:
        from pdfminer.high_level import extract_text
    except Exception:
        return None

    try:
        raw = extract_text(str(path))
        if not isinstance(raw, str):
            return None
        return _normalize_text(raw)
    except Exception:
        return None


def _extract_with_pdftotext(path: Path) -> str | None:
    """Try extracting text with the ``pdftotext`` CLI if available.

    Returns the normalized text on success, otherwise ``None``.
    """
    try:
        # Check availability
        proc = subprocess.run(["which", "pdftotext"], capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return None

        # Run pdftotext, capture to stdout via '-' output
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return None
        return _normalize_text(result.stdout)
    except Exception:
        return None


def _extract_with_tesseract(path: Path, lang: str = "eng") -> str | None:
    """OCR the PDF using Tesseract via pdftoppm -> tesseract pipeline."""
    try:
        if subprocess.run(["which", "pdftoppm"], capture_output=True, check=False).returncode != 0:
            return None
        if subprocess.run(["which", "tesseract"], capture_output=True, check=False).returncode != 0:
            return None

        texts: list[str] = []
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir) / "page"
            subprocess.run(["pdftoppm", "-png", "-r", "300", str(path), str(base)], check=False)
            for img_path in sorted(Path(tmpdir).glob("page-*.png")):
                out_base = img_path.with_suffix("")
                subprocess.run(["tesseract", str(img_path), str(out_base), "-l", lang], check=False)
                txt_path = Path(str(out_base) + ".txt")
                if txt_path.exists():
                    texts.append(txt_path.read_text(encoding="utf-8", errors="ignore"))
        return _normalize_text("\n".join(texts))
    except Exception:
        return None


def extract_text_from_pdf(
    path: str, *, ocr: bool = False, ocr_lang: str = "eng", ingest_log_path: str | None = None
) -> str:
    """Extract text from a PDF file located at ``path``.

    Strategy:
    1. Use ``pdfminer.six`` to extract text.
    2. If the result is too short (< 200 characters), attempt ``pdftotext``.
    3. Normalize unicode and whitespace.

    Raises a ``ValueError`` if extraction fails or yields empty text.

    Parameters
    ----------
    path: str
        Filesystem path to the PDF file.

    Returns
    -------
    str
        Normalized text content of the PDF.
    """
    pdf_path = Path(path)
    if not pdf_path.exists() or not pdf_path.is_file():
        raise ValueError(f"PDF file not found: {pdf_path}")

    # Primary: pdfminer
    text = _extract_with_pdfminer(pdf_path)
    if text is None:
        text = ""

    # Fallback if too short
    if len(text) < MIN_TEXT_LEN:
        alt = _extract_with_pdftotext(pdf_path)
        if alt is not None and len(alt) > len(text):
            text = alt

    # Optional or forced OCR
    if ocr or len(text) < MIN_TEXT_LEN:
        alt_ocr = _extract_with_tesseract(pdf_path, lang=ocr_lang)
        if alt_ocr is not None and len(alt_ocr) > len(text):
            text = alt_ocr

    text = _normalize_text(text)
    if len(text) == 0:
        raise ValueError("Failed to extract text from PDF with available methods.")

    # Ingest log (very simple density metric)
    if ingest_log_path is not None:
        try:
            size_bytes = pdf_path.stat().st_size if pdf_path.exists() else 0
            density = len(text) / max(1, size_bytes)
            Path(ingest_log_path).parent.mkdir(parents=True, exist_ok=True)
            Path(ingest_log_path).write_text(
                json.dumps(
                    {
                        "doc": pdf_path.name,
                        "chars": len(text),
                        "bytes": size_bytes,
                        "density": density,
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except Exception:
            pass
    return text
