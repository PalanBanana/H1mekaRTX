#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 38 Baseline Privacy / Redaction Audit Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure local UI baseline artifact summary exists =="
"${ROOT_DIR}/scripts/run-local-ui-baseline-artifact-summary.sh"

echo "== 4. Sanitize committed local UI baseline release-readiness summaries =="
python3 "${ROOT_DIR}/scripts/sanitize-local-ui-baseline-release-readiness.py" \
  --root "${ROOT_DIR}"

echo "== 5. Run baseline privacy/redaction audit =="
python3 "${ROOT_DIR}/scripts/check-baseline-privacy-redaction-audit.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 6. Run baseline privacy/redaction audit contract check =="
python3 "${ROOT_DIR}/scripts/check-baseline-privacy-redaction-audit-contract.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 7. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 8. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 38 baseline privacy/redaction audit verification passed =="
