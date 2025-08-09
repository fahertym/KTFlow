# ruff: noqa: E402
from __future__ import annotations

"""CSV writing helpers."""

import csv
from collections.abc import Iterable, Mapping
from pathlib import Path


def write_edge_list(path: str | Path, rows: Iterable[Mapping[str, object]]) -> None:
    """Write edge list CSV given pre-built rows with consistent keys.

    Expects rows shaped like:
      {"doc_id": str, "from_layer": str, "to_layer": str, "count": int}
    """
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        # Write only header if no rows
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["doc_id", "from_layer", "to_layer", "count"])
        return

    fieldnames = ["doc_id", "from_layer", "to_layer", "count"]
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer2 = csv.DictWriter(f, fieldnames=fieldnames)
        writer2.writeheader()
        for row in rows:
            writer2.writerow({k: row.get(k) for k in fieldnames})
