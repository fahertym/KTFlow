## Knowledge Topology Flow (KTFlow)

Pipeline to parse PDFs, segment into sentences, tag each sentence with a Knowledge Topology (KT) layer, and compute flows (transitions) between adjacent sentences.

### Quickstart

Prereqs:
- Python 3.12
- Optional: `pdftotext` CLI for fallback PDF extraction

Set up environment (using the repo's venv if present):

```bash
export PYTHONPATH=$PWD/src
```

Run the CLI on the control document:

```bash
python src/cli/parse_doc.py \
  --input data/raw/kt_control_v1.pdf \
  --out-sentences data/processed/kt_control_v1_sentences.jsonl \
  --out-flows data/processed/kt_control_v1_flows.csv
```

Outputs:
- `data/processed/kt_control_v1_sentences.jsonl` – one JSON object per sentence with fields: `doc_id`, `i`, `text`, `layer`
- `data/processed/kt_control_v1_flows.csv` – edge list with columns: `doc_id,from_layer,to_layer,count`

### Testing

```bash
pytest -q
# with coverage
pytest -q --cov=ktflow --cov-report=term-missing
```

### KT Layers (labels)

- S — Symbol: forms/terms, lists of terms, prompts like "what is".
- L — Literal: definitions and naming ("is a", "means", "defined as").
- R — Relational: causal/associative links ("because", "therefore", "if … then").
- St — Structural: systems, components, feedbacks, integration.
- G — Generative: principles/rules/transfer ("in general", "applies to").
- M — Meta: assumptions, reframing, hidden premises.

### Modules

- `ktflow.ingest.pdf.extract_text_from_pdf(path: str) -> str`
- `ktflow.segment.sentence.split_sentences(text: str) -> list[str]`
- `ktflow.tag.rules.tag_sentence_rules(s: str) -> str`
- `ktflow.map.graph.build_flow_counts(labels: list[str], window: int = 1) -> dict[tuple[str,str], int]`
- `ktflow.map.graph.to_edge_list_csv(doc_id: str, counts: dict, path: str) -> None`
- `ktflow.map.graph.find_motifs(labels: list[str]) -> dict[str, int]`
- `ktflow.io.csv.write_edge_list(path: str, rows: list[dict]) -> None`

### Preflight evaluation

```bash
python src/cli/preflight.py \
  --pred data/processed/kt_control_v1_sentences.jsonl \
  --gold data/interim/answer_keys/kt_control_v1_sentences.jsonl \
  --report data/processed/kt_control_v1_preflight.txt
```

### Windowed flows, motifs, and viz

```bash
python src/cli/parse_doc.py \
  --input data/raw/kt_control_v1.pdf \
  --out-sentences data/processed/kt_control_v1_sentences.jsonl \
  --out-flows data/processed/kt_control_v1_flows.csv \
  --window 3 \
  --viz data/processed/kt_control_v1_flows.png
```

Motifs CSV can be requested with `--motifs data/processed/kt_control_v1_motifs.csv`.


