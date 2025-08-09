# ruff: noqa: E402
from __future__ import annotations

"""Seed and edit a gold answer key for sentence labels."""

import argparse
import csv
import json
from pathlib import Path

from ktflow.io.model import load_joblib
from ktflow.tag.hybrid import tag_sentence_hybrid


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def export_csv(seed_rows: list[dict], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sentence", "layer_suggested", "layer_final"])
        for r in seed_rows:
            writer.writerow([r["text"], r["layer_suggested"], r["layer_suggested"]])


def run_tui(csv_path: Path, out_jsonl: Path) -> None:
    try:
        from prompt_toolkit import PromptSession
    except Exception:  # pragma: no cover - optional UI
        print("prompt_toolkit not available; please edit the CSV manually.")
        return

    import pandas as pd

    df = pd.read_csv(csv_path)
    session: PromptSession = PromptSession()
    labels = ["S", "L", "R", "St", "G", "M", "UNK"]
    for idx, row in df.iterrows():
        print(f"[{idx+1}/{len(df)}] {row['sentence']}")
        print(f"Suggested: {row['layer_suggested']}  Current: {row['layer_final']}")
        ans = session.prompt("Label [S|L|R|St|G|M|UNK] (Enter to keep): ")
        if ans and ans in labels:
            df.at[idx, "layer_final"] = ans
    # Save back
    tmp_csv = csv_path.with_suffix(".edited.csv")
    df.to_csv(tmp_csv, index=False)
    # Emit JSONL answer key
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with out_jsonl.open("w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            obj = {"text": row["sentence"], "layer": row["layer_final"]}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build gold answer key")
    parser.add_argument("--input", required=True, help="Sentences JSONL to seed from")
    parser.add_argument("--model", help="Optional hybrid model path (.joblib)")
    parser.add_argument("--out", required=True, help="Output gold JSONL")
    parser.add_argument(
        "--csv",
        help="Optional CSV path for manual review (sentence,layer_suggested,layer_final)",
    )
    args = parser.parse_args(argv)

    rows = _read_jsonl(Path(args.input))
    model = load_joblib(args.model) if args.model else None

    seed_rows: list[dict] = []
    for r in rows:
        text = r["text"]
        # Seed with rules first, then ML if provided
        label = tag_sentence_hybrid(text, model=model, rules_first=True, confidence_gap=0.25)
        seed_rows.append({"text": text, "layer_suggested": label})

    # Option (a): CSV + TUI
    csv_path = Path(args.csv) if args.csv else Path("data/interim/answer_keys/seed.csv")
    export_csv(seed_rows, csv_path)
    out_path = Path(args.out)
    run_tui(csv_path, out_path)
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
