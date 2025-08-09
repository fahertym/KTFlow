from __future__ import annotations

"""KTFlow CLI: Parse a PDF document, tag sentences, and map flows.

Usage:
    export PYTHONPATH=$PWD/src
    python src/cli/parse_doc.py \
      --input data/raw/kt_control_v1.pdf \
      --out-sentences data/processed/kt_control_v1_sentences.jsonl \
      --out-flows data/processed/kt_control_v1_flows.csv
"""

import argparse
import sys
from pathlib import Path
from typing import List

from ktflow.ingest.pdf import extract_text_from_pdf
from ktflow.segment.sentence import split_sentences
from ktflow.tag.rules import tag_sentence_rules
from ktflow.io.jsonl import write_jsonl
from ktflow.map.graph import build_flow_counts, to_edge_list_csv


def _infer_doc_id(input_path: Path) -> str:
    return input_path.stem


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KTFlow PDF parser")
    parser.add_argument("--input", required=True, help="Path to input PDF")
    parser.add_argument(
        "--out-sentences",
        required=True,
        help="Output JSONL for sentence records",
    )
    parser.add_argument(
        "--out-flows", required=True, help="Output CSV for flow edge list"
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    out_sentences = Path(args.out_sentences)
    out_flows = Path(args.out_flows)

    try:
        if not input_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {input_path}")

        doc_id = _infer_doc_id(input_path)

        text = extract_text_from_pdf(str(input_path))
        sentences = [s for s in split_sentences(text) if s.strip()]

        records = []
        labels: List[str] = []
        for i, s in enumerate(sentences):
            label = tag_sentence_rules(s)
            labels.append(label)
            records.append({
                "doc_id": doc_id,
                "i": i,
                "text": s,
                "layer": label,
            })

        write_jsonl(out_sentences, records)

        counts = build_flow_counts(labels)
        to_edge_list_csv(doc_id=doc_id, counts=counts, path=str(out_flows))

        # Basic acceptance: ensure at least some content
        if len(sentences) == 0:
            print("No sentences produced from input.", file=sys.stderr)
            return 2

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
import typer
from pathlib import Path
from ktflow.ingest.pdf import extract_text_from_pdf
from ktflow.segment.sentence import split_sentences
from ktflow.tag.rules import tag_sentence_rules
from ktflow.io.jsonl import write_jsonl

app = typer.Typer()

@app.command()
def run(input_pdf: Path, out_jsonl: Path = Path("data/processed/parsed.jsonl")):
    text = extract_text_from_pdf(str(input_pdf))
    sents = split_sentences(text)
    rows = []
    for i, s in enumerate(sents):
        rows.append({"i": i, "sentence": s, "label": tag_sentence_rules(s)})
    write_jsonl(out_jsonl, rows)
    typer.echo(f"Wrote {out_jsonl}")

if __name__ == "__main__":
    app()
