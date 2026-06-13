#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 18 Local Entitlement/Signing Evidence Verification =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

echo "== 1. Compile Python scripts =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py

echo "== 2. Validate bash syntax =="
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== 3. Collect local entitlement/signing evidence =="
python3 "${ROOT_DIR}/scripts/collect-local-entitlement-signing-evidence.py" \
  --root "${ROOT_DIR}" \
  --out-dir "host-report-bundle/local-entitlement-signing-evidence"

echo "== 4. Run local entitlement/signing evidence checker =="
python3 "${ROOT_DIR}/scripts/check-local-entitlement-signing-evidence.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}"

echo "== 5. Execute existing BAR safety gates =="
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"

echo "== 6. Execute release readiness no-runtime gate =="
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"

echo "== Phase 18 local entitlement/signing evidence verification passed =="
