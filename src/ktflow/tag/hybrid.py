# ruff: noqa: E402
from __future__ import annotations

"""Hybrid rules+ML tagger."""


import numpy as np

from ktflow.tag.ml import ModelBundle, predict_proba
from ktflow.tag.rules import tag_sentence_rules


def tag_sentence_hybrid(
    s: str,
    model: ModelBundle | None = None,
    rules_first: bool = True,
    confidence_gap: float = 0.25,
) -> str:
    """Hybrid tagging strategy.

    - If rules_first, run rules. If rules returns a non-UNK label with strong
      indicators, immediately return it.
    - Otherwise, use the ML model (if provided). If probability gap between top
      two classes exceeds ``confidence_gap``, return the top label; else fall
      back to rules. If still UNK, return ML top.
    """
    # Strong-rule shortcut
    rule_label = tag_sentence_rules(s)
    if rules_first and rule_label != "UNK":
        # Treat any non-UNK hit as high confidence for now
        return rule_label

    if model is None:
        return rule_label

    probs = predict_proba(model, [s])[0]
    order = np.argsort(probs)[::-1]
    top_idx, second_idx = order[0], order[1] if len(order) > 1 else (order[0], order[0])
    gap = probs[top_idx] - probs[second_idx]
    top_label = model.label_encoder.inverse_transform([top_idx])[0]

    if gap >= confidence_gap:
        return top_label

    # fallback to rules
    if rule_label != "UNK":
        return rule_label

    return top_label
