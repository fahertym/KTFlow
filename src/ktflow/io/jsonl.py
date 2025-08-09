from __future__ import annotations

"""Utilities for writing JSON Lines (JSONL)."""

import json
from pathlib import Path
from typing import Iterable, Mapping


def write_jsonl(path: str | Path, rows: Iterable[Mapping]) -> None:
    """Write an iterable of dictionaries to a JSONL file.

    Ensures the parent directory exists.
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

import json
from pathlib import Path
def write_jsonl(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
