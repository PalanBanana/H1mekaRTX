#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== H1mekaRTX Phase 60V Local Read-Only RTX 5070 UI Baseline Verification =="
python3 -m py_compile scripts/*.py
bash -n scripts/*.sh
python3 scripts/collect-local-readonly-rtx5070-ui-baseline.py --root "${ROOT_DIR}"
python3 scripts/summarize-local-readonly-rtx5070-ui-baseline.py --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 scripts/check-local-readonly-rtx5070-ui-baseline.py
./scripts/run-bar-safety-gates.sh
./scripts/run-release-readiness-ci.sh --out-dir "$(mktemp -d)"
echo "== Phase 60V verification passed =="
