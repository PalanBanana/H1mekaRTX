#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 51 Local Unsigned Bundle Manifest Lock Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Ensure unsigned app bundle layout exists =="
python3 "${ROOT_DIR}/scripts/generate-unsigned-local-app-bundle-layout.py" --root "${ROOT_DIR}" --out-dir "host-report-bundle/unsigned-app-bundle"

echo "== Write local-only manifest lock =="
python3 "${ROOT_DIR}/scripts/lock-local-unsigned-bundle-manifest.py" --root "${ROOT_DIR}" --bundle-root "host-report-bundle/unsigned-app-bundle" --out-dir "host-report-bundle/unsigned-app-bundle-manifest-lock"

echo "== Write sanitized release-readiness manifest lock summary =="
python3 "${ROOT_DIR}/scripts/summarize-local-unsigned-bundle-manifest-lock.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

echo "== Check manifest lock summary =="
python3 "${ROOT_DIR}/scripts/check-local-unsigned-bundle-manifest-lock.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 51 verification passed =="
