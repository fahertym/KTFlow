# ruff: noqa: E402
from __future__ import annotations

"""Project-level configuration and logging setup for KTFlow.

Uses pydantic-settings for environment-driven configuration and provides a
helper to configure stdlib logging.
"""

import logging
from pathlib import Path

try:
    from pydantic_settings import BaseSettings
except Exception:  # pragma: no cover - optional at import time for tests
    # Lightweight shim if pydantic-settings is unavailable at import time.
    class BaseSettings:  # type: ignore
        pass


class Settings(BaseSettings):
    """Configuration for KTFlow.

    Environment variables are read with prefix ``KTFLOW_``.
    """

    # Defaults
    default_window: int = 1
    pdf_min_chars_for_ok: int = 200

    # Regex used by sentence splitter (documented here for centralization)
    sentence_split_regex: str = r"(?<=[.!?])\s+(?=[\"'\(\[]?[A-Z0-9])"

    data_dir: Path = Path("data")
    processed_dir: Path = Path("data/processed")
    interim_dir: Path = Path("data/interim")

    class Config:
        env_prefix = "KTFLOW_"


def setup_logging(verbose: bool = False) -> None:
    """Configure root logger with a simple format.

    Parameters
    ----------
    verbose: bool
        If True, set level to DEBUG. Otherwise INFO.
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
