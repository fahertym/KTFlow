# ruff: noqa: E402
from __future__ import annotations

"""Sentence segmentation utilities.

Provides a simple, deterministic regex-based sentence splitter that is good
enough for well-formed prose. Later, this module can be extended to include
spaCy or EDU-based segmentation.
"""

import re

_SPLIT_REGEX = re.compile(
    # Split on a sentence end punctuation followed by whitespace and a likely
    # sentence starter (capital, quote, parenthesis, or digit).
    r"(?<=[.!?])\s+(?=[\"'\(\[]?[A-Z0-9])"
)


def _normalize_whitespace(text: str) -> str:
    """Collapse excessive whitespace and normalize newlines to spaces."""
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into sentences.

    Rules:
    - Uses punctuation-based boundaries: period, question mark, exclamation.
    - Keeps terminal punctuation attached to the sentence.
    - Collapses internal whitespace and strips leading/trailing spaces.
    - Skips empty outputs.

    Parameters
    ----------
    text: str
        Input text to segment.

    Returns
    -------
    list[str]
        List of sentence strings.
    """
    if not text:
        return []

    normalized = _normalize_whitespace(text)
    # Quick return when no sentence end markers are present
    if not re.search(r"[.!?]", normalized):
        return [normalized] if normalized else []

    parts = _SPLIT_REGEX.split(normalized)
    sentences: list[str] = []
    for part in parts:
        s = part.strip()
        if not s:
            continue
        sentences.append(s)
    return sentences
