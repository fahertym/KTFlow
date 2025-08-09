from __future__ import annotations

import json
from pathlib import Path

from ktflow.tag.hybrid import tag_sentence_hybrid
from ktflow.tag.ml import train_tfidf_lr


def test_hybrid_rules_first(tmp_path: Path) -> None:
    # Train trivial model
    train_rows = [
        {"text": "A is a thing.", "layer": "L"},
        {"text": "Assume X.", "layer": "M"},
    ]
    train_path = tmp_path / "train.jsonl"
    with train_path.open("w", encoding="utf-8") as f:
        for r in train_rows:
            f.write(json.dumps(r) + "\n")

    model = train_tfidf_lr(str(train_path))

    # Rules dominate when strong cue present
    label = tag_sentence_hybrid(
        "Assume the premise.", model=model, rules_first=True, confidence_gap=0.9
    )
    assert label == "M"

    # No strong rule -> ML used
    label2 = tag_sentence_hybrid(
        "Totally ambiguous.", model=model, rules_first=True, confidence_gap=0.0
    )
    assert label2 in {"L", "M"}
