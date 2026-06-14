#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 61A Local Metal HUD Environment Prep Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/collect-local-metal-hud-environment-prep.py --root "${ROOT_DIR}"
python3 scripts/summarize-local-metal-hud-environment-prep.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-local-metal-hud-environment-prep.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 61A verification passed =="
