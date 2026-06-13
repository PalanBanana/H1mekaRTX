#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 16 No-Build Project Generation Preflight Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure non-building generator dry-run and allowlist outputs exist =="
python3 "${ROOT_DIR}/scripts/generate-nonbuilding-project-dryrun.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout/project-generator-dryrun"

python3 "${ROOT_DIR}/scripts/generate-project-generator-output-allowlist.py" \
  --root "${ROOT_DIR}" \
  --out-dir "tools/driverkit-xcode-layout/project-generator-dryrun"

echo "== 4. Run no-build project generation preflight checker =="
python3 "${ROOT_DIR}/scripts/check-no-build-project-generation-preflight.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 5. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 6. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 16 no-build project generation preflight verification passed =="
