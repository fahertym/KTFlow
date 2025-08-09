# ruff: noqa: E402
from __future__ import annotations

"""CLI to generate an HTML error report comparing predictions to gold."""

import argparse

from ktflow.eval.report import build_error_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KTFlow error report")
    parser.add_argument("--pred", required=True)
    parser.add_argument("--gold", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    build_error_report(args.pred, args.gold, args.out)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
