# ruff: noqa: E402
from __future__ import annotations

"""Preflight evaluation CLI: compare predicted sentence labels to a gold key.

Aligns by exact sentence text and computes accuracy, macro/micro F1, per-label
precision/recall, and a confusion matrix. Writes a human-readable report and
optionally a CSV of the confusion matrix.
"""

import argparse
import json
from pathlib import Path

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


def _align_by_text(pred_rows: list[dict], gold_rows: list[dict]) -> tuple[list[str], list[str]]:
    gold_by_text: dict[str, str] = {r["text"]: r["layer"] for r in gold_rows}
    y_true: list[str] = []
    y_pred: list[str] = []
    for r in pred_rows:
        t = r["text"]
        if t in gold_by_text:
            y_true.append(gold_by_text[t])
            y_pred.append(r["layer"])
    return y_true, y_pred


from typing import Any


def _write_confusion_csv(labels: list[str], cm: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(",".join(["label"] + labels) + "\n")
        for i, label in enumerate(labels):
            row = ",".join(str(x) for x in cm[i])
            f.write(f"{label},{row}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KTFlow preflight evaluation")
    parser.add_argument("--pred", required=True, help="Predicted JSONL path")
    parser.add_argument("--gold", required=True, help="Gold JSONL path")
    parser.add_argument("--report", required=True, help="Path to write report")
    parser.add_argument("--csv", help="Optional CSV path for confusion matrix")
    args = parser.parse_args(argv)

    pred_path = Path(args.pred)
    gold_path = Path(args.gold)
    report_path = Path(args.report)
    csv_path = Path(args.csv) if args.csv else None

    pred_rows = _read_jsonl(pred_path)
    gold_rows = _read_jsonl(gold_path)

    y_true, y_pred = _align_by_text(pred_rows, gold_rows)
    if not y_true:
        report = "No overlapping sentences between pred and gold."
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
        print(report)
        return 2

    labels = sorted(
        {*y_true, *y_pred},
        key=lambda s: (
            ["S", "L", "R", "St", "G", "M", "UNK"].index(s)
            if s in ["S", "L", "R", "St", "G", "M", "UNK"]
            else 999
        ),
    )

    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, labels=labels, average="macro")
    micro_f1 = f1_score(y_true, y_pred, labels=labels, average="micro")

    report_txt = [
        f"Accuracy: {acc:.3f}",
        f"Macro F1: {macro_f1:.3f}",
        f"Micro F1: {micro_f1:.3f}",
        "",
        classification_report(y_true, y_pred, labels=labels, zero_division=0),
    ]
    report_full = "\n".join(report_txt)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_full, encoding="utf-8")
    print(report_full)

    cm = confusion_matrix(y_true, y_pred, labels=labels)
    if csv_path is not None:
        _write_confusion_csv(labels, cm, csv_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
