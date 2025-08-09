from __future__ import annotations

"""PDF ingestion utilities.

This module provides a robust text extractor for PDF files. It prefers
``pdfminer.six`` and falls back to the ``pdftotext`` command-line tool when
available if the primary approach yields too little text (e.g., for scanned
PDFs or unusual encodings).

Public API:
- extract_text_from_pdf(path: str) -> str
"""

from pathlib import Path
import re
import subprocess
import sys
from typing import Optional


def _normalize_text(raw: str) -> str:
    """Normalize unicode and collapse excessive whitespace.

    - Converts Windows/Mac newlines to ``\n`` implicitly via Python strings
    - Replaces non-breaking spaces with regular spaces
    - Collapses runs of whitespace (including newlines) to single spaces
    - Strips leading/trailing spaces
    """
    # Replace non-breaking space and similar with a normal space
    text = raw.replace("\u00A0", " ")
    # Collapse any whitespace run to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_with_pdfminer(path: Path) -> Optional[str]:
    """Try extracting text with pdfminer.six.

    Returns the normalized text on success, or ``None`` if pdfminer is not
    available or extraction fails.
    """
    try:
        from pdfminer.high_level import extract_text  # type: ignore
    except Exception:
        return None

    try:
        raw = extract_text(str(path))
        if not isinstance(raw, str):
            return None
        return _normalize_text(raw)
    except Exception:
        return None


def _extract_with_pdftotext(path: Path) -> Optional[str]:
    """Try extracting text with the ``pdftotext`` CLI if available.

    Returns the normalized text on success, otherwise ``None``.
    """
    try:
        # Check availability
        proc = subprocess.run(["which", "pdftotext"], capture_output=True, text=True)
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


def extract_text_from_pdf(path: str) -> str:
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
    if len(text) < 200:
        alt = _extract_with_pdftotext(pdf_path)
        if alt is not None and len(alt) > len(text):
            text = alt

    text = _normalize_text(text)
    if len(text) == 0:
        raise ValueError(
            "Failed to extract text from PDF with both pdfminer and pdftotext."
        )
    return text

from pdfminer.high_level import extract_text
def extract_text_from_pdf(path: str) -> str:
    return extract_text(path)
