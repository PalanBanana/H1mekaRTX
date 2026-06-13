#!/bin/bash
set -euo pipefail

echo "== H1mekaRTX Phase 3 Runtime Probe Preflight Verification =="
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "1. Compile Python scripts..."
python3 -m py_compile "${ROOT_DIR}/scripts"/*.py

echo "2. Run Runtime Probe Preflight Checker..."
python3 "${ROOT_DIR}/scripts/check-runtime-probe-preflight.py" --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"

echo "3. Validate bash syntax..."
bash -n "${ROOT_DIR}/scripts"/*.sh

echo "4. Execute existing safety gates..."
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "All Phase 3 verification successfully passed."
