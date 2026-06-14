#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/release-readiness}"

echo "== H1mekaRTX Phase 45 Compile-Only Failure Sanitizer Summary Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh

echo "== Ensure Phase 44 local compile-only report exists =="
"${ROOT_DIR}/scripts/run-compile-only-target-smoke-test.sh"

echo "== Write sanitized compile-only failure summary =="
python3 "${ROOT_DIR}/scripts/summarize-compile-only-failure-sanitizer.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

echo "== Check sanitized compile-only failure summary =="
python3 "${ROOT_DIR}/scripts/check-compile-only-failure-sanitizer-summary.py" --root "${ROOT_DIR}" --out-dir "${OUT_DIR}"

"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 45 verification passed =="
