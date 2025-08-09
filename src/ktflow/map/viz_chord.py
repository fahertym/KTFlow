from __future__ import annotations

"""Chord-like visualization using matplotlib only."""

from math import cos, sin, pi
from typing import Dict, Tuple

import matplotlib.pyplot as plt


def draw_chord_from_counts(counts: Dict[Tuple[str, str], int], out_png: str) -> None:
    labels = ["S", "L", "R", "St", "G", "M"]
    pos = {
        lab: (cos(2 * pi * i / len(labels)), sin(2 * pi * i / len(labels)))
        for i, lab in enumerate(labels)
    }
    max_count = max(counts.values()) if counts else 1

    plt.figure(figsize=(6, 6), dpi=150)
    # Draw nodes
    for lab, (x, y) in pos.items():
        plt.scatter([x], [y], s=200, color="#E0E0E0", edgecolors="#333333")
        plt.text(x, y, lab, ha="center", va="center")

    # Draw arcs (as straight lines for simplicity)
    for (fr, to), c in counts.items():
        if fr not in pos or to not in pos:
            continue
        x1, y1 = pos[fr]
        x2, y2 = pos[to]
        width = 0.5 + 4.0 * (c / max_count)
        plt.plot([x1, x2], [y1, y2], linewidth=width, alpha=0.6, color="#1f77b4")

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()


