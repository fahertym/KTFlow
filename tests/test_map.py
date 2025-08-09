from __future__ import annotations

from ktflow.map.graph import build_flow_counts


def test_build_flow_counts():
    labels = ["S", "L", "R", "R", "L"]
    counts = build_flow_counts(labels)
    # Expected pairs: S->L, L->R, R->R, R->L
    assert counts.get(("S", "L")) == 1
    assert counts.get(("L", "R")) == 1
    assert counts.get(("R", "R")) == 1
    assert counts.get(("R", "L")) == 1


