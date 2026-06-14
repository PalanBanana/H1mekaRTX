#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 61D Sanitized Local Metal HUD Capture Summary Parser Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/parse-sanitized-local-metal-hud-capture-summary.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-sanitized-local-metal-hud-capture-summary-parser.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 61D verification passed =="
