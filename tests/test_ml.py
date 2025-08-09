from __future__ import annotations

import json
from pathlib import Path

from ktflow.tag.ml import train_tfidf_lr, predict


def test_ml_train_predict(tmp_path: Path):
    train_rows = [
        {"text": "Assume X.", "layer": "M"},
        {"text": "In general, the principle holds.", "layer": "G"},
        {"text": "A photon is a particle.", "layer": "L"},
        {"text": "Because A then B.", "layer": "R"},
    ]
    train_path = tmp_path / "train.jsonl"
    with train_path.open("w", encoding="utf-8") as f:
        for r in train_rows:
            f.write(json.dumps(r) + "\n")

    model = train_tfidf_lr(str(train_path))
    preds = predict(model, ["Assume Y.", "In general, X."])
    assert preds[0] in {"M"}
    assert preds[1] in {"G"}


