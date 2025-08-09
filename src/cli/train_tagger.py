# ruff: noqa: E402
from __future__ import annotations

"""Train a TF-IDF + Logistic Regression tagger and save it via joblib."""

import argparse

from ktflow.io.model import save_joblib
from ktflow.tag.ml import train_tfidf_lr


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train TF-IDF LR tagger")
    parser.add_argument("--train", required=True, help="JSONL of labeled sentences")
    parser.add_argument("--out", required=True, help="Output model path (.joblib)")
    args = parser.parse_args(argv)

    model = train_tfidf_lr(args.train)
    save_joblib(model, args.out)
    print(f"Saved model to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
