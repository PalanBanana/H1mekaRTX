#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 60X Scenario Marker Aggregation Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/aggregate-scenario-marker-events.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-scenario-marker-aggregation.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 60X verification passed =="
