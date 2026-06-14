#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 62A RTX 5070 Accelerated Bring-Up Critical Path Gate Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/check-rtx5070-accelerated-bringup-critical-path-gate.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 62A verification passed =="
