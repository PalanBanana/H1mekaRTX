#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 37 Local UI Baseline Artifact Summary Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Ensure local read-only UI baseline exists =="
python3 "${ROOT_DIR}/scripts/collect-local-readonly-ui-baseline.py" \
  --root "${ROOT_DIR}" \
  --out-dir "host-report-bundle/ui-baseline"

echo "== 4. Summarize local-only UI baseline artifact =="
python3 "${ROOT_DIR}/scripts/summarize-local-ui-baseline-artifact.py" \
  --root "${ROOT_DIR}" \
  --baseline "host-report-bundle/ui-baseline/local-readonly-ui-baseline.json" \
  --out-dir "${OUT_DIR}"

echo "== 5. Run local UI baseline artifact summary checker =="
python3 "${ROOT_DIR}/scripts/check-local-ui-baseline-artifact-summary.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 6. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 7. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 37 local UI baseline artifact summary verification passed =="
