# ruff: noqa: E402
from __future__ import annotations

"""Utilities for writing JSON Lines (JSONL)."""

import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def write_jsonl(path: str | Path, rows: Iterable[Mapping]) -> None:
    """Write an iterable of dictionaries to a JSONL file.

    Ensures the parent directory exists.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
