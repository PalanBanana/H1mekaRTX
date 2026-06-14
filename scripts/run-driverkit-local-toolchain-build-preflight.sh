#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 43 DriverKit Local Toolchain Build Preflight Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh
python3 "${ROOT_DIR}/scripts/collect-driverkit-local-toolchain-build-preflight.py" --root "${ROOT_DIR}" --out-dir "host-report-bundle/driverkit-toolchain-preflight"
python3 "${ROOT_DIR}/scripts/check-driverkit-local-toolchain-build-preflight.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 43 verification passed =="
