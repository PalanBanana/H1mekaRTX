#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 60Y Metal HUD / Frame Pacing Capture Plan Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/check-metal-hud-frame-pacing-capture-plan.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 60Y verification passed =="
