# ruff: noqa: E402
from __future__ import annotations

"""EDU-like segmentation using pysbd + simple clause splitting."""

import re

MIN_FRAGMENT_LEN = 15


def _split_clauses(sent: str) -> list[str]:
    # Split on commas/conjunctions when safe (keep short fragments together)
    parts = re.split(r"\s*,\s*|\s*(?:and|but|or)\s+", sent)
    edus: list[str] = []
    for part in parts:
        part_stripped = part.strip()
        if not part_stripped:
            continue
        edus.append(part_stripped)
    # Merge tiny fragments with neighbors
    merged: list[str] = []
    for frag in edus:
        if merged and (len(frag) < MIN_FRAGMENT_LEN):
            merged[-1] = merged[-1] + ", " + frag
        else:
            merged.append(frag)
    return merged


def split_edus(text: str) -> list[str]:
    try:
        import pysbd
    except Exception:
        # Fallback: single segment if pysbd missing
        return [text.strip()] if text.strip() else []

    if not text:
        return []

    seg = pysbd.Segmenter(language="en", clean=True)
    sents = seg.segment(text)
    edus: list[str] = []
    for s in sents:
        edus.extend(_split_clauses(s))
    return [e.strip() for e in edus if e.strip()]
