#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 15 Project Generator Output Allowlist Gate Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure non-building project generator dry-run manifest exists =="
python3 "${ROOT_DIR}/scripts/generate-nonbuilding-project-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout/project-generator-dryrun"

echo "== 4. Generate project generator output allowlist =="
python3 "${ROOT_DIR}/scripts/generate-project-generator-output-allowlist.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout/project-generator-dryrun"

echo "== 5. Run project generator output allowlist gate checker =="
python3 "${ROOT_DIR}/scripts/check-project-generator-output-allowlist-gate.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 6. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 7. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 15 project generator output allowlist gate verification passed =="
