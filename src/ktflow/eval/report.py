# ruff: noqa: E402
from __future__ import annotations

"""Misclassification report generation (HTML)."""

import json
from collections import defaultdict
from pathlib import Path

import plotly.express as px
from jinja2 import Template
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def _align(pred_rows: list[dict], gold_rows: list[dict]) -> tuple[list[str], list[str], list[str]]:
    gold_by_text: dict[str, str] = {r["text"]: r["layer"] for r in gold_rows}
    y_true: list[str] = []
    y_pred: list[str] = []
    texts: list[str] = []
    for r in pred_rows:
        t = r["text"]
        if t in gold_by_text:
            texts.append(t)
            y_true.append(gold_by_text[t])
            y_pred.append(r["layer"])
    return texts, y_true, y_pred


from typing import Any


def _confusion_fig(labels: list[str], y_true: list[str], y_pred: list[str]) -> Any:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig = px.imshow(
        cm,
        x=labels,
        y=labels,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Predicted", y="True", color="Count"),
        title="Confusion Matrix",
    )
    return fig


def _top_confusions(
    texts: list[str], y_true: list[str], y_pred: list[str], top_k: int = 10
) -> list[tuple[tuple[str, str], list[str]]]:
    pairs: dict[tuple[str, str], list[str]] = defaultdict(list)
    for t, yt, yp in zip(texts, y_true, y_pred, strict=False):
        if yt != yp:
            pairs[(yt, yp)].append(t)
    # Sort by frequency
    ranked = sorted(pairs.items(), key=lambda kv: len(kv[1]), reverse=True)
    # Trim examples per pair
    result = [((a, b), exs[:top_k]) for (a, b), exs in ranked]
    return result


_TEMPLATE = Template(
    """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>KTFlow Error Report</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 2rem; }
    h2 { margin-top: 2rem; }
    table { border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 6px 10px; }
    code { background: #f7f7f7; padding: 2px 4px; }
  </style>
  {{ plotly_script|safe }}
</head>
<body>
  <h1>KTFlow Error Report</h1>
  <h2>Metrics</h2>
  <pre>{{ metrics }}</pre>
  <h2>Confusion Matrix</h2>
  {{ confusion_div|safe }}

  <h2>Top Confusions</h2>
  {% for (a,b), exs in top_confusions %}
    <h3>{{ a }} → {{ b }} ({{ exs|length }})</h3>
    <ul>
    {% for s in exs %}
      <li><code>{{ s }}</code></li>
    {% endfor %}
    </ul>
  {% endfor %}
</body>
</html>
"""
)


def build_error_report(pred_path: str, gold_path: str, out_html: str) -> None:
    pred_rows = _read_jsonl(Path(pred_path))
    gold_rows = _read_jsonl(Path(gold_path))

    texts, y_true, y_pred = _align(pred_rows, gold_rows)
    if not y_true:
        Path(out_html).write_text("No overlap between pred and gold.", encoding="utf-8")
        return

    # Labels set
    labels = ["S", "L", "R", "St", "G", "M", "UNK"]

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=labels, average="macro")
    micro_f1 = f1_score(y_true, y_pred, labels=labels, average="micro")
    cls_rep = classification_report(y_true, y_pred, labels=labels, zero_division=0)
    metrics_text = (
        f"Accuracy: {acc:.3f}\nMacro F1: {macro_f1:.3f}\nMicro F1: {micro_f1:.3f}\n\n{cls_rep}"
    )

    # Confusion matrix plot
    fig = _confusion_fig(labels, y_true, y_pred)
    plotly_script = """
<script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
"""
    confusion_div = fig.to_html(full_html=False, include_plotlyjs=False)

    # Top confusions
    confusions = _top_confusions(texts, y_true, y_pred)

    html = _TEMPLATE.render(
        metrics=metrics_text,
        confusion_div=confusion_div,
        plotly_script=plotly_script,
        top_confusions=confusions,
    )
    Path(out_html).write_text(html, encoding="utf-8")
