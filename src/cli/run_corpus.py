# ruff: noqa: E402
from __future__ import annotations

"""Run KTFlow over a corpus of PDFs and aggregate results."""

import argparse
from pathlib import Path
from typing import TypedDict

import pandas as pd
from ktflow.ingest.pdf import extract_text_from_pdf
from ktflow.io.jsonl import write_jsonl
from ktflow.map.graph import build_flow_counts, to_edge_list_csv
from ktflow.segment.edu import split_edus
from ktflow.segment.sentence import split_sentences
from ktflow.tag.rules import tag_sentence_rules


class Row(TypedDict):
    doc_id: str
    src: str
    dst: str
    count: int


def run_doc(input_pdf: Path, out_dir: Path, seg: str, window: int) -> Path:
    doc_id = input_pdf.stem
    text = extract_text_from_pdf(str(input_pdf))
    if seg == "edu":
        units = split_edus(text)
    else:
        units = split_sentences(text)
    labels = [tag_sentence_rules(u) for u in units]
    rows = [{"doc_id": doc_id, "i": i, "text": u, "layer": labels[i]} for i, u in enumerate(units)]

    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / f"{doc_id}_sentences.jsonl"
    flows_path = out_dir / f"{doc_id}_flows.csv"
    write_jsonl(jsonl_path, rows)
    counts = build_flow_counts([str(lbl) for lbl in labels], window=window)
    to_edge_list_csv(doc_id, counts, str(flows_path))
    return flows_path


def main(argv: list[str] | None = None) -> int:  # noqa: PLR0915
    parser = argparse.ArgumentParser(description="KTFlow corpus runner")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--pattern", default="*.pdf")
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--seg", choices=["sentence", "edu"], default="sentence")
    parser.add_argument("--window", type=int, default=1)
    parser.add_argument("--parquet", action="store_true")
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    out_dir = Path(args.out_dir)

    pdf_paths = sorted(Path(input_dir).glob(args.pattern))

    flow_files: list[Path] = []
    if args.jobs <= 1:
        for path in pdf_paths:
            flow_files.append(run_doc(path, out_dir, args.seg, args.window))
    else:
        from concurrent.futures import ProcessPoolExecutor, as_completed

        from rich.progress import Progress

        with Progress() as progress:
            task = progress.add_task("Processing PDFs", total=len(pdf_paths))
            with ProcessPoolExecutor(max_workers=args.jobs) as ex:
                fut_to_path = {
                    ex.submit(run_doc, p, out_dir, args.seg, args.window): p for p in pdf_paths
                }
                for fut in as_completed(fut_to_path):
                    flow_files.append(fut.result())
                    progress.update(task, advance=1)

    # Aggregate
    import csv

    totals: dict[tuple[str, str], int] = {}
    per_doc_rows: list[dict[str, int | str]] = []
    for fp in sorted(flow_files):
        with fp.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            doc_id = None
            doc_total = 0
            for row in reader:
                # Enforce types via Row to help mypy
                doc_id = row["doc_id"]
                r: Row = {
                    "doc_id": str(row["doc_id"]),
                    "src": str(row["from_layer"]),
                    "dst": str(row["to_layer"]),
                    "count": int(row["count"]),
                }
                key = (r["src"], r["dst"])
                count = r["count"]
                totals[key] = totals.get(key, 0) + count
                doc_total += count
            if doc_id is not None:
                per_doc_rows.append({"doc_id": str(doc_id), "total_edges": int(doc_total)})

    # Save aggregates
    import csv

    matrix_path = out_dir / "_flow_matrix.csv"
    matrix_path.parent.mkdir(parents=True, exist_ok=True)
    labels = ["S", "L", "R", "St", "G", "M"]
    with matrix_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from\\to"] + labels)
        for fr in labels:
            row_out: list[str | int] = [fr]
            for to in labels:
                row_out.append(totals.get((fr, to), 0))
            writer.writerow(row_out)

    summary_path = out_dir / "_corpus_summary.csv"
    pd.DataFrame(per_doc_rows).to_csv(summary_path, index=False)

    # Optional parquet persistence of sentence rows is left to pipeline stage
    print(f"Wrote {summary_path} and {matrix_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
