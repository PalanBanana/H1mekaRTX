#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 49 Unsigned Local App Bundle Layout Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

python3 "${ROOT_DIR}/scripts/generate-unsigned-local-app-bundle-layout.py" --root "${ROOT_DIR}" --out-dir "host-report-bundle/unsigned-app-bundle"
python3 "${ROOT_DIR}/scripts/check-unsigned-local-app-bundle-layout.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 49 verification passed =="
