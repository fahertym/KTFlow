PYTHON=python
PIP=$(PYTHON) -m pip

.PHONY: setup lint fmt typecheck test cov run_demo precommit-install gpu-check

setup:
	$(PIP) install -q --upgrade pip
	$(PIP) install -q -r requirements.txt || true
	$(PIP) install -q pdfminer.six scikit-learn matplotlib pydantic-settings pysbd plotly pytest pytest-cov pre-commit ruff black mypy

lint:
	pre-commit run ruff --all-files || true

fmt:
	pre-commit run ruff-format --all-files || true
	pre-commit run black --all-files || true

typecheck:
	mypy src

test:
	PYTHONPATH=src pytest -q

cov:
	PYTHONPATH=src pytest -q --cov=ktflow --cov-report=term-missing

run_demo:
	PYTHONPATH=src $(PYTHON) src/cli/parse_doc.py --input data/raw/kt_control_v1.pdf --out-sentences data/processed/kt_control_v1_sentences.jsonl --out-flows data/processed/kt_control_v1_flows.csv --window 3 --viz data/processed/kt_control_v1_flows.png

precommit-install:
	pre-commit install

gpu-check:
	. .venv/bin/activate; PYTHONPATH=src $(PYTHON) scripts/gpu_check.py || true

torch-nightly:
	. .venv/bin/activate; \
	for CH in cu129 cu128 cu126; do \
	  echo "Trying nightly channel: $$CH"; \
	  if $(PYTHON) -m pip install --pre --upgrade --index-url "https://download.pytorch.org/whl/nightly/$$CH" torch torchvision torchaudio; then \
	    echo "Installed from nightly/$$CH"; exit 0; \
	  fi; \
	done; \
	echo "No suitable torch nightly found" && exit 1


