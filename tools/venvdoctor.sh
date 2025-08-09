#!/usr/bin/env bash
set -euo pipefail

echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-<empty>}"
echo "which python3: $(which python3 || true)"
echo "which pip: $(which pip || true)"
echo "pip version: $(python3 -m pip --version || true)"

if [[ -z "${VIRTUAL_ENV:-}" ]]; then
  echo "[FAIL] Not in a virtualenv (.venv expected)" >&2
  exit 1
fi

if [[ "$VIRTUAL_ENV" != *".venv"* ]]; then
  echo "[FAIL] VIRTUAL_ENV is not .venv: $VIRTUAL_ENV" >&2
  exit 1
fi

if [[ "$(which python3)" != *".venv"* ]] || [[ "$(python3 -m pip --version)" != *".venv"* ]]; then
  echo "[FAIL] python3/pip not from .venv; use ./.venv/bin/python -m pip ..." >&2
  exit 1
fi

echo "[OK] Virtualenv seems healthy (.venv active)."


