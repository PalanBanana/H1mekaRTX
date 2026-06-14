#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== H1mekaRTX Phase 60S Local Apple Team Capability Evidence Verification =="
python3 -m py_compile "${ROOT_DIR}"/scripts/*.py
bash -n "${ROOT_DIR}"/scripts/*.sh
python3 "${ROOT_DIR}/scripts/collect-local-apple-team-capability-evidence.py" --root "${ROOT_DIR}"
python3 "${ROOT_DIR}/scripts/summarize-local-apple-team-capability-evidence.py" --root "${ROOT_DIR}" --out-dir "${ROOT_DIR}/release-readiness"
python3 "${ROOT_DIR}/scripts/check-local-apple-team-capability-evidence.py"
"${ROOT_DIR}/scripts/run-bar-safety-gates.sh"
"${ROOT_DIR}/scripts/run-release-readiness-ci.sh" --out-dir "$(mktemp -d)"
echo "== Phase 60S verification passed =="
