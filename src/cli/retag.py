from __future__ import annotations

"""Retag an existing sentences JSONL using rules, ML, or hybrid."""

import argparse
import json
from pathlib import Path
from typing import List

from ktflow.io.model import load_joblib
from ktflow.tag.rules import tag_sentence_rules
from ktflow.tag.hybrid import tag_sentence_hybrid


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Retag sentences JSONL")
    parser.add_argument("--input", required=True, help="Input sentences JSONL")
    parser.add_argument("--model", required=False, help="Model path (.joblib)")
    parser.add_argument("--out", required=True, help="Output sentences JSONL")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--rules-only", action="store_true")
    mode.add_argument("--ml-only", action="store_true")
    parser.add_argument("--gap", type=float, default=0.25, help="Confidence gap for hybrid")
    args = parser.parse_args(argv)

    model = load_joblib(args.model) if (args.model and not args.rules_only) else None

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(args.input, "r", encoding="utf-8") as fin, out_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("text", "")
            if args.rules_only:
                label = tag_sentence_rules(text)
            elif args.ml_only:
                if model is None:
                    raise ValueError("--ml-only requires --model")
                from ktflow.tag.ml import predict

                label = predict(model, [text])[0]
            else:
                label = tag_sentence_hybrid(text, model=model, rules_first=True, confidence_gap=args.gap)

            row["layer"] = label
            fout.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


