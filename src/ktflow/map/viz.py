# ruff: noqa: E402
from __future__ import annotations

"""Visualization helpers for KTFlow graphs."""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

Label = str
Edge = tuple[Label, Label]


def draw_flow_graph(counts: dict[Edge, int], path_png: str) -> None:
    """Draw a directed graph PNG of layer transitions.

    - Node labels: S, L, R, St, G, M
    - Edge width proportional to normalized count
    - Edge labels show raw counts
    """
    G = nx.DiGraph()

    nodes = ["S", "L", "R", "St", "G", "M"]
    G.add_nodes_from(nodes)

    if counts:
        max_count = max(counts.values())
        for (u, v), c in counts.items():
            if u not in nodes or v not in nodes:
                continue
            G.add_edge(u, v, weight=c, label=str(c), width=1.0 + 4.0 * (c / max_count))

    # Layout
    pos = nx.circular_layout(G)

    # Draw
    plt.figure(figsize=(6, 6), dpi=150)
    nx.draw_networkx_nodes(G, pos, node_color="#E0E0E0", edgecolors="#333333")
    nx.draw_networkx_labels(G, pos, font_size=10)
    widths = [G[u][v].get("width", 1.0) for u, v in G.edges()]
    nx.draw_networkx_edges(G, pos, width=widths, arrows=True, arrowstyle="-|>")
    edge_labels = {(u, v): G[u][v]["label"] for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    Path(path_png).parent.mkdir(parents=True, exist_ok=True)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path_png)
    plt.close()
