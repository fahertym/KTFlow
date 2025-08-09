# ruff: noqa: E402
from __future__ import annotations

"""Flow mapping utilities.

Build transition counts between consecutive labels and optionally export an
edge list CSV.
"""

from collections import Counter

from ktflow.io.csv import write_edge_list as write_edge_list_csv_rows

Label = str
Edge = tuple[Label, Label]


def build_flow_counts(labels: list[Label], window: int = 1) -> dict[Edge, int]:
    """Count transitions between consecutive labels.

    Parameters
    ----------
    labels: list[str]
        Sequence of labels (e.g., ["S", "L", "R"]).
    window: int
        Count transitions i -> i+k for k in [1..window].

    Returns
    -------
    dict[tuple[str, str], int]
        Mapping of (from_label, to_label) to count.
    """
    if window < 1:
        window = 1
    pairs: list[Edge] = []
    n = len(labels)
    for i in range(n):
        for k in range(1, window + 1):
            j = i + k
            if j < n:
                pairs.append((labels[i], labels[j]))
    counts = Counter(pairs)
    return dict(counts)


def to_edge_list_csv(doc_id: str, counts: dict[Edge, int], path: str) -> None:
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


def find_motifs(labels: list[Label]) -> dict[str, int]:
    """Detect 3-step motifs (length-3 sequences) and count their occurrences.

    Example motif label: "L-G-M".
    """
    motifs: dict[str, int] = {}
    for i in range(len(labels) - 2):
        tri = labels[i : i + 3]
        key = f"{tri[0]}-{tri[1]}-{tri[2]}"
        motifs[key] = motifs.get(key, 0) + 1
    return motifs
