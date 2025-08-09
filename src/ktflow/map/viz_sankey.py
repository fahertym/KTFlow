from __future__ import annotations

"""Sankey visualization for layer transitions using Plotly."""

from typing import Dict, Tuple


def draw_sankey_from_counts(counts: Dict[Tuple[str, str], int], out_html: str) -> None:
    try:
        import plotly.graph_objects as go
    except Exception as e:  # pragma: no cover - optional dependency
        raise RuntimeError("Plotly is required for Sankey viz. Install plotly.") from e

    labels = ["S", "L", "R", "St", "G", "M"]
    index = {lab: i for i, lab in enumerate(labels)}

    sources = []
    targets = []
    values = []
    for (fr, to), c in counts.items():
        if fr in index and to in index:
            sources.append(index[fr])
            targets.append(index[to])
            values.append(int(c))

    fig = go.Figure(
        go.Sankey(
            node=dict(label=labels, pad=15, thickness=20),
            link=dict(source=sources, target=targets, value=values),
        )
    )
    fig.write_html(out_html)


