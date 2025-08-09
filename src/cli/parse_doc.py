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
import logging
import sys
from pathlib import Path
from typing import List

from ktflow.config import Settings, setup_logging
from ktflow.ingest.pdf import extract_text_from_pdf
from ktflow.segment.sentence import split_sentences
from ktflow.tag.rules import tag_sentence_rules
from ktflow.io.jsonl import write_jsonl
from ktflow.map.graph import build_flow_counts, to_edge_list_csv, find_motifs
from ktflow.map.viz import draw_flow_graph


def _infer_doc_id(input_path: Path) -> str:
    return input_path.stem


def main(argv: List[str] | None = None) -> int:
    settings = Settings()

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
    parser.add_argument(
        "--window",
        type=int,
        default=settings.default_window,
        help="Window size for flow counting (i->i+k, k in [1..window])",
    )
    parser.add_argument(
        "--seg",
        choices=["sentence", "edu"],
        default="sentence",
        help="Segmentation mode",
    )
    parser.add_argument(
        "--viz",
        help="Optional path to write a PNG of the flow graph",
    )
    parser.add_argument(
        "--sankey",
        help="Optional path to write a Sankey HTML",
    )
    parser.add_argument(
        "--chord",
        help="Optional path to write a chord-like PNG",
    )
    parser.add_argument(
        "--motifs",
        help="Optional path to write motifs CSV (doc_id,motif,count)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    out_sentences = Path(args.out_sentences)
    out_flows = Path(args.out_flows)
    window: int = max(1, int(args.window))

    try:
        setup_logging(verbose=bool(args.verbose))
        log = logging.getLogger("ktflow.cli.parse_doc")
        if not input_path.exists():
            raise FileNotFoundError(f"Input PDF not found: {input_path}")

        doc_id = _infer_doc_id(input_path)

        text = extract_text_from_pdf(str(input_path))
        if args.seg == "edu":
            from ktflow.segment.edu import split_edus

            sentences = [s for s in split_edus(text) if s.strip()]
        else:
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

        counts = build_flow_counts(labels, window=window)
        to_edge_list_csv(doc_id=doc_id, counts=counts, path=str(out_flows))

        if args.viz:
            try:
                draw_flow_graph(counts, args.viz)
            except Exception as e:
                log.warning("Failed to render viz: %s", e)

        if args.sankey:
            try:
                from ktflow.map.viz_sankey import draw_sankey_from_counts

                draw_sankey_from_counts(counts, args.sankey)
            except Exception as e:
                log.warning("Failed to render sankey: %s", e)

        if args.chord:
            try:
                from ktflow.map.viz_chord import draw_chord_from_counts

                draw_chord_from_counts(counts, args.chord)
            except Exception as e:
                log.warning("Failed to render chord: %s", e)

        if args.motifs:
            from ktflow.io.csv import write_edge_list as write_csv

            motif_counts = find_motifs(labels)
            motif_rows = [
                {"doc_id": doc_id, "motif": k, "count": v}
                for k, v in sorted(motif_counts.items())
            ]
            # Write a simple CSV header + rows
            out_path = Path(args.motifs)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            import csv

            with out_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["doc_id", "motif", "count"])
                for row in motif_rows:
                    writer.writerow([row["doc_id"], row["motif"], row["count"]])

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
