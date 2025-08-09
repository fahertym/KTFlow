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

### CI

- Fast defaults skip heavy GPU/HF tests via `pytest.ini` markers (`slow`, `gpu`).
- Make targets:

```bash
make test        # fast tests
make test-all    # includes slow, skips gpu
make test-gpu    # gpu-only (on CUDA machines)
make cov-gate    # enforce coverage ≥ 60%
```

### KT Layers (labels)

| Label | Name       | Summary |
|-------|------------|---------|
| S     | Symbol     | Forms/terms; prompts like "what is"; term lists |
| L     | Literal    | Definitions/naming: "is a", "means", "defined as" |
| R     | Relational | Causal/associative links: "because", "therefore", "if … then" |
| St    | Structural | Systems/feedbacks/interaction/integration |
| G     | Generative | Principles/rules/transfer: "in general", "applies to" |
| M     | Meta       | Assumptions/reframing/hidden premises |

Flows: readers move between layers (e.g., L→G, St→M) rather than strictly bottom-up. We track adjacent and windowed transitions to characterize cognition-in-text and detect motifs (e.g., L→G→M).

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

### Preflight + Answer Key

```bash
python src/cli/build_answer_key.py \
  --input data/processed/kt_control_v1_sentences.jsonl \
  --out data/interim/answer_keys/kt_control_v1_sentences.jsonl \
  --csv data/interim/answer_keys/kt_control_v1_seed.csv

python src/cli/report_errors.py \
  --pred data/processed/kt_control_v1_sentences.jsonl \
  --gold data/interim/answer_keys/kt_control_v1_sentences.jsonl \
  --out data/processed/kt_control_v1_report.html
```

### WSL2 GPU quickstart

- Windows host should show GPU in `nvidia-smi` (native Windows).
- In WSL, absence of `/dev/nvidia*` is normal. WSL uses `/dev/dxg` and `/usr/lib/wsl/lib/libcuda.so*`.
- PyTorch install (CUDA 12.1 wheels):

```bash
. .venv/bin/activate
python -m pip install -U pip
python -m pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu121
make gpu-check  # prints DXG/libcuda status and CUDA availability
```

**WSL2 + CUDA (Ada/Blackwell, compute 12.x):**
PyTorch stable may not yet ship kernels for sm_120. Use nightly cu129 wheels:

```bash
make torch-nightly
python - <<'PY'
import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())
PY
```

Troubleshooting “externally-managed-environment”:

```bash
./tools/venvdoctor.sh
# Or ensure you use the venv python explicitly:
./.venv/bin/python -m pip install -U pip
```

### Hybrid Tagger (TF-IDF + Logistic Regression)

Train:

```bash
python src/cli/train_tagger.py \
  --train data/interim/answer_keys/train_sentences.jsonl \
  --out models/tfidf_lr.joblib
```

Retag using hybrid:

```bash
python src/cli/retag.py \
  --input data/processed/kt_control_v1_sentences.jsonl \
  --model models/tfidf_lr.joblib \
  --out data/processed/kt_control_v1_sentences_hybrid.jsonl
```

### EDU Segmentation

Use `--seg edu` to segment into finer-grained EDUs (requires `pysbd`).

### Corpus Runner

```bash
python src/cli/run_corpus.py \
  --input-dir data/raw --pattern "*.pdf" --out-dir data/processed \
  --seg sentence --window 3
```

### System dependencies (optional)

```bash
sudo apt-get update
sudo apt-get install -y graphviz graphviz-dev pandoc \
  poppler-utils tesseract-ocr
```


