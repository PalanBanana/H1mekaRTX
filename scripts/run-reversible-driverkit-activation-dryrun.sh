#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 8 Reversible DriverKit Activation Dry-Run Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Run reversible DriverKit activation dry-run checker =="
python3 "${ROOT_DIR}/scripts/check-reversible-driverkit-activation-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 4. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 5. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 8 reversible DriverKit activation dry-run verification passed =="
