from __future__ import annotations

from pathlib import Path

from cli.preflight import _align_by_text


def test_preflight_align_and_metrics(tmp_path: Path) -> None:
    pred = [
        {"doc_id": "d", "i": 0, "text": "A is a thing.", "layer": "L"},
        {"doc_id": "d", "i": 1, "text": "Assume X.", "layer": "M"},
    ]
    gold = [
        {"doc_id": "d", "i": 0, "text": "A is a thing.", "layer": "L"},
        {"doc_id": "d", "i": 1, "text": "Assume X.", "layer": "M"},
    ]

    y_true, y_pred = _align_by_text(pred, gold)
    assert y_true == ["L", "M"]
    assert y_pred == ["L", "M"]
