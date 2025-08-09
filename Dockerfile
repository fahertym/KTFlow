FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    MPLBACKEND=Agg \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    graphviz graphviz-dev pandoc poppler-utils tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN python -m pip install --upgrade pip \
    && python -m pip install pdfminer.six scikit-learn matplotlib pydantic-settings pysbd plotly pytest pytest-cov pre-commit ruff black mypy

CMD ["bash"]


