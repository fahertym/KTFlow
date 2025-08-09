from __future__ import annotations

"""EDU-like segmentation using pysbd + simple clause splitting."""

from typing import List
import re


def _split_clauses(sent: str) -> List[str]:
    # Split on commas/conjunctions when safe (keep short fragments together)
    parts = re.split(r"\s*,\s*|\s*(?:and|but|or)\s+", sent)
    edus: List[str] = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        edus.append(p)
    # Merge tiny fragments with neighbors
    merged: List[str] = []
    for frag in edus:
        if merged and (len(frag) < 15):
            merged[-1] = merged[-1] + ", " + frag
        else:
            merged.append(frag)
    return merged


def split_edus(text: str) -> List[str]:
    try:
        import pysbd
    except Exception:
        # Fallback: single segment if pysbd missing
        return [text.strip()] if text.strip() else []

    if not text:
        return []

    seg = pysbd.Segmenter(language="en", clean=True)
    sents = seg.segment(text)
    edus: List[str] = []
    for s in sents:
        edus.extend(_split_clauses(s))
    return [e.strip() for e in edus if e.strip()]


