#!/usr/bin/env bash
# run_linters.sh – run all code-quality tools on the web_app source tree
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/../.venv"

cd "$SCRIPT_DIR"

# ── Activate venv ─────────────────────────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "ERROR: virtual environment not found at $VENV_DIR"
    echo "       Run start_web.sh first to create it."
    exit 1
fi
source "$VENV_DIR/bin/activate"

# ── Install linters (once; no-op if already present) ─────────────────────────
echo "Installing / updating linters..."
pip install --quiet black isort flake8 ruff pylint pylint-django mypy django-stubs

# ── Source paths ──────────────────────────────────────────────────────────────
SRC=(domain application infrastructure chat config manage.py)

# ── Helpers ───────────────────────────────────────────────────────────────────
PASS=0
FAIL=0
RESULTS=()

run_linter() {
    local name="$1"; shift
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if "$@"; then
        RESULTS+=("  ✓  $name")
        PASS=$((PASS + 1))
    else
        RESULTS+=("  ✗  $name")
        FAIL=$((FAIL + 1))
    fi
}

# ── Linters ───────────────────────────────────────────────────────────────────

# black – formatting (check only, no auto-fix)
run_linter "black  (format check)" \
    black --check --diff "${SRC[@]}"

# isort – import order (check only)
run_linter "isort  (import order check)" \
    isort --check-only --diff "${SRC[@]}"

# flake8 – PEP-8 / style
run_linter "flake8 (style)" \
    flake8 --max-line-length=100 "${SRC[@]}"

# ruff – fast Python linter (superset of many checks)
run_linter "ruff   (lint)" \
    ruff check --line-length=100 "${SRC[@]}"

# pylint – static analysis (Django plugin aware)
run_linter "pylint (static analysis)" \
    pylint --load-plugins=pylint_django \
           --django-settings-module=config.settings \
           --max-line-length=100 \
           --disable=C0114,C0115,C0116 \
           "${SRC[@]}"

# mypy – type checking
run_linter "mypy   (type check)" \
    mypy --ignore-missing-imports \
         --explicit-package-bases \
         "${SRC[@]}"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for r in "${RESULTS[@]}"; do echo "$r"; done
echo ""
echo "  Passed: $PASS / $((PASS + FAIL))"

if [ "$FAIL" -gt 0 ]; then
    echo "  FAILED: $FAIL linter(s) reported issues."
    exit 1
else
    echo "  All linters passed."
fi
