#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="${1:-${ROOT_DIR}/host-report-bundle/hackintosh-ui-observability}"

echo "== H1mekaRTX Local Hackintosh UI Observability Capture =="
echo "ROOT_DIR=${ROOT_DIR}"
echo "OUT_DIR=${OUT_DIR}"

mkdir -p "${OUT_DIR}"

python3 "${ROOT_DIR}/scripts/check-hackintosh-ui-observability-baseline.py" \
  --root "${ROOT_DIR}" \
  --out-dir "${OUT_DIR}" \
  --collect-local

echo "== Local Hackintosh UI observability capture complete =="
ls -lh "${OUT_DIR}"/hackintosh-ui-observability-baseline-check.*
