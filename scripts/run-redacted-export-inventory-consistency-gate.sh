#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 63G Redacted Export Inventory Consistency Gate Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/build-redacted-export-inventory-consistency-gate.py
python3 scripts/check-redacted-export-inventory-consistency-gate.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 63G verification passed =="
