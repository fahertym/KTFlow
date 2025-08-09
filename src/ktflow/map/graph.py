from __future__ import annotations

"""Flow mapping utilities.

Build transition counts between consecutive labels and optionally export an
edge list CSV.
"""

from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from ktflow.io.csv import write_edge_list as write_edge_list_csv_rows


Label = str
Edge = Tuple[Label, Label]


def build_flow_counts(labels: List[Label]) -> Dict[Edge, int]:
    """Count transitions between consecutive labels.

    Parameters
    ----------
    labels: list[str]
        Sequence of labels (e.g., ["S", "L", "R"]).

    Returns
    -------
    dict[tuple[str, str], int]
        Mapping of (from_label, to_label) to count.
    """
    pairs: Iterable[Edge] = (
        (labels[i], labels[i + 1]) for i in range(0, max(0, len(labels) - 1))
    )
    counts = Counter(pairs)
    return dict(counts)


def to_edge_list_csv(doc_id: str, counts: Dict[Edge, int], path: str) -> None:
    """Write the edge list CSV with header.

    Parameters
    ----------
    doc_id: str
        Document identifier to write on each row.
    counts: dict
        Mapping of (from_label, to_label) -> count.
    path: str
        Output CSV path.
    """
    rows = [
        {
            "doc_id": doc_id,
            "from_layer": from_label,
            "to_layer": to_label,
            "count": cnt,
        }
        for (from_label, to_label), cnt in sorted(counts.items())
    ]
    write_edge_list_csv_rows(path=path, rows=rows)


