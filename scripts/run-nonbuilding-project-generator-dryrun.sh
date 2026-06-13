#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 14 Non-Building Project Generator Dry-Run Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure prior pbxproj metadata dry-run outputs exist =="
python3 "${ROOT_DIR}/scripts/generate-pbxproj-metadata-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout"

echo "== 4. Ensure prior sanitizer outputs exist =="
python3 "${ROOT_DIR}/scripts/run-pbxproj-dryrun-diff-guard.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}" \
  --metadata-dir "tools/driverkit-xcode-layout"

echo "== 5. Generate non-building project generator dry-run manifest =="
python3 "${ROOT_DIR}/scripts/generate-nonbuilding-project-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout/project-generator-dryrun"

echo "== 6. Run non-building project generator dry-run checker =="
python3 "${ROOT_DIR}/scripts/check-nonbuilding-project-generator-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 7. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 8. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 14 non-building project generator dry-run verification passed =="
