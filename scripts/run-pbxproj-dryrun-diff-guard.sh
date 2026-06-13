#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 13 PBXProj Dry-Run Diff Guard Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure pbxproj metadata dry-run outputs exist =="
python3 "${ROOT_DIR}/scripts/generate-pbxproj-metadata-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout"

echo "== 4. Run pbxproj dry-run diff guard =="
python3 "${ROOT_DIR}/scripts/run-pbxproj-dryrun-diff-guard.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}" \
  --metadata-dir "tools/driverkit-xcode-layout"

echo "== 5. Run pbxproj dry-run diff guard contract checker =="
python3 "${ROOT_DIR}/scripts/check-pbxproj-dryrun-diff-guard-contract.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 6. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 7. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 13 pbxproj dry-run diff guard verification passed =="
