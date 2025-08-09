# ruff: noqa: E402
from __future__ import annotations

"""Model persistence helpers for taggers (joblib)."""

from pathlib import Path
from typing import Any

import joblib


def save_joblib(obj: Any, path: str | Path) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(obj, out)


def load_joblib(path: str | Path) -> Any:
    return joblib.load(Path(path))
