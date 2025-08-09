from __future__ import annotations

from ktflow.map.graph import build_flow_counts, find_motifs


def test_build_flow_counts() -> None:
    labels = ["S", "L", "R", "R", "L"]
    counts = build_flow_counts(labels)
    # Expected pairs: S->L, L->R, R->R, R->L
    assert counts.get(("S", "L")) == 1
    assert counts.get(("L", "R")) == 1
    assert counts.get(("R", "R")) == 1
    assert counts.get(("R", "L")) == 1


def test_build_flow_counts_windowed() -> None:
    labels = ["S", "L", "R", "M"]
    counts = build_flow_counts(labels, window=2)
    # Adjacent: S->L, L->R, R->M
    # Window=2 adds: S->R, L->M
    assert counts.get(("S", "L")) == 1
    assert counts.get(("L", "R")) == 1
    assert counts.get(("R", "M")) == 1
    assert counts.get(("S", "R")) == 1
    assert counts.get(("L", "M")) == 1


def test_find_motifs() -> None:
    labels = ["L", "G", "M", "St"]
    motifs = find_motifs(labels)
    # Expected motifs: L-G-M and G-M-St
    assert motifs.get("L-G-M") == 1
    assert motifs.get("G-M-St") == 1
