# ruff: noqa: E402
from __future__ import annotations

"""Train a HF classifier for KTFlow labels."""

import argparse

from ktflow.tag.hf import train_hf_classifier


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--train", required=True)
    p.add_argument(
        "--model",
        required=True,
        help="HF model name (e.g., sentence-transformers/all-MiniLM-L6-v2)",
    )
    p.add_argument("--out", required=True)
    p.add_argument("--epochs", type=int, default=3)
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--lr", type=float, default=2e-5)
    p.add_argument("--fp16", action="store_true")
    args = p.parse_args(argv)

    train_hf_classifier(
        train_jsonl=args.train,
        model_name=args.model,
        out_dir=args.out,
        epochs=args.epochs,
        batch_size=args.batch,
        lr=args.lr,
        fp16=bool(args.fp16),
    )
    print(f"Saved {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
