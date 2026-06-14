#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 60Z Local Metal HUD Capture Manifest Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/generate-local-metal-hud-capture-manifest.py --root "${ROOT_DIR}"
python3 scripts/summarize-local-metal-hud-capture-manifest.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-local-metal-hud-capture-manifest.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 60Z verification passed =="
