#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

cd "$ROOT"

echo "== H1mekaRTX BAR safety gates =="
echo "Repo: $ROOT"
echo "Temp: $TMP_ROOT"

echo
echo "== Python syntax =="
PY_FILES=()
while IFS= read -r -d '' file; do
  PY_FILES+=("$file")
done < <(find scripts -maxdepth 1 -type f -name '*.py' -print0 | sort -z)

if [ "${#PY_FILES[@]}" -eq 0 ]; then
  echo "No Python scripts found under scripts/"
  exit 1
fi

python3 -m py_compile "${PY_FILES[@]}"

echo
echo "== Stage 4 fixture: BAR inventory summary =="
BAR_INV="$TMP_ROOT/bar-inventory-fixture"
mkdir -p "$BAR_INV"

cat > "$BAR_INV/sw_vers.txt" <<'EOF'
ProductName:		macOS
ProductVersion:		27.0
BuildVersion:		26A000
EOF

cat > "$BAR_INV/uname.txt" <<'EOF'
Darwin ci.local 26.0.0 Darwin Kernel Version 26.0.0: root:xnu-0000.0.0~1/RELEASE_ARM64_T8132 arm64
EOF

cat > "$BAR_INV/system_profiler-SPPCIDataType.txt" <<'EOF'
RTX 5070:
  Vendor ID: 0x10de
  Device ID: 0x2f04
  Subsystem Vendor ID: 0x1458
  Subsystem ID: 0x417e
EOF

cat > "$BAR_INV/system_profiler-SPDisplaysDataType.txt" <<'EOF'
Displays:
  No display engine initialized by H1mekaRTX.
EOF

cat > "$BAR_INV/ioreg-IODeviceTree.txt" <<'EOF'
IODeviceTree placeholder
EOF

cat > "$BAR_INV/ioreg-IOService.txt" <<'EOF'
IOService placeholder
EOF

cat > "$BAR_INV/ioreg-rtx5070-filtered.txt" <<'EOF'
"vendor-id" = <de100000>
"device-id" = <042f0000>
"IOPCIMatch" = "0x2f0410de"
"assigned-addresses" = <00000000>
"reg" = <00000000>
"AAPL,slot-name" = "PCI Slot"
"class-code" = <00000300>
"subsystem-vendor-id" = <58140000>
"subsystem-id" = <7e410000>
EOF

cat > "$BAR_INV/logs-driverkit-pci-last30m.txt" <<'EOF'
H1mekaRTX diagnostic placeholder
IOPCIDevice placeholder
DriverKit placeholder
sysextd placeholder
EOF

cat > "$BAR_INV/README.txt" <<'EOF'
Read-only CI fixture.
EOF

./scripts/summarize-bar-inventory.py "$BAR_INV" --out-dir "$BAR_INV/out"
test -s "$BAR_INV/out/bar-inventory-summary.json"
test -s "$BAR_INV/out/bar-inventory-summary.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$BAR_INV/out/bar-inventory-summary.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.bar_inventory_summary.v1"
assert data["likely_target_present"] is True
assert data["target_hits"]["vendor_10de"] >= 1
assert data["target_hits"]["device_2f04"] >= 1
assert data["target_hits"]["iopcimatch_2f0410de"] >= 1
assert data["safety_boundary"]["read_only"] is True
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["driverkit_activation"] is False

print("Stage 4 fixture validation passed")
PY

SUMMARY_JSON="$BAR_INV/out/bar-inventory-summary.json"

echo
echo "== Stage 5 fixture: BAR/MMIO safety boundary =="
./scripts/check-bar-safety-boundary.py "$SUMMARY_JSON" --out-dir "$BAR_INV/out"
test -s "$BAR_INV/out/bar-mmio-safety-check.md"

echo
echo "== Stage 6 fixture: BAR access readiness matrix =="
./scripts/generate-bar-readiness-matrix.py "$SUMMARY_JSON" --out-dir "$BAR_INV/out"
test -s "$BAR_INV/out/bar-access-readiness-matrix.json"
test -s "$BAR_INV/out/bar-access-readiness-matrix.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$BAR_INV/out/bar-access-readiness-matrix.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.bar_access_readiness_matrix.v1"
assert data["readiness"] == "NOT_READY"
assert data["fail_count"] == 0
assert data["blocked_count"] >= 1
assert data["safety_boundary"]["read_only"] is True
assert data["safety_boundary"]["performs_mmio_reads"] is False
assert data["safety_boundary"]["performs_mmio_writes"] is False
assert data["safety_boundary"]["driverkit_activation"] is False

print("Stage 6 readiness validation passed")
PY

MATRIX_JSON="$BAR_INV/out/bar-access-readiness-matrix.json"

echo
echo "== Stage 7 fixture: default-deny BAR access policy =="
./scripts/generate-bar-access-policy.py "$MATRIX_JSON" --out-dir "$BAR_INV/out"
test -s "$BAR_INV/out/bar-access-policy.json"
test -s "$BAR_INV/out/bar-access-policy.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$BAR_INV/out/bar-access-policy.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.bar_access_policy.v1"
assert data["policy_mode"] == "DEFAULT_DENY"
assert data["effective_decision"] == "DENY_ALL_BAR_ACCESS"
assert data["matrix_validation_passed"] is True
assert data["safety_boundary"]["read_only"] is True
assert data["safety_boundary"]["performs_mmio_reads"] is False
assert data["safety_boundary"]["performs_mmio_writes"] is False
assert data["safety_boundary"]["driverkit_activation"] is False
assert len(data["bar_policy"]) >= 7
assert all(item["access"] == "DENY" for item in data["bar_policy"])
assert all(item["read"] is False for item in data["bar_policy"])
assert all(item["write"] is False for item in data["bar_policy"])
assert all(item["map"] is False for item in data["bar_policy"])
assert all(item["poke"] is False for item in data["bar_policy"])

print("Stage 7 policy validation passed")
PY

echo
echo "== Stage 8 fixture: forbidden BAR operation audit =="
SAFE_ROOT="$TMP_ROOT/audit-safe"
UNSAFE_ROOT="$TMP_ROOT/audit-unsafe"

mkdir -p "$SAFE_ROOT/src" "$SAFE_ROOT/docs" "$UNSAFE_ROOT/src"

MR_TOKEN="Memory""Read32"
MW_TOKEN="Memory""Write32"
CW_TOKEN="Configuration""Write32"

cat > "$SAFE_ROOT/src/safe_placeholder.cpp" <<'EOF'
int h1mekartx_safe_placeholder(void) {
    return 0;
}
EOF

cat > "$SAFE_ROOT/docs/allowed_doc_mentions.md" <<EOF
Docs may mention ${MR_TOKEN} and ${CW_TOKEN} without failing because docs are excluded.
EOF

./scripts/audit-forbidden-bar-ops.py --root "$SAFE_ROOT" --out-dir "$SAFE_ROOT/out"
test -s "$SAFE_ROOT/out/forbidden-bar-operation-audit.json"
test -s "$SAFE_ROOT/out/forbidden-bar-operation-audit.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$SAFE_ROOT/out/forbidden-bar-operation-audit.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.forbidden_bar_operation_audit.v1"
assert data["decision"] == "PASS_NO_FORBIDDEN_BAR_OPS"
assert data["block_count"] == 0
assert data["safety_boundary"]["read_only"] is True
assert data["safety_boundary"]["performs_mmio_reads"] is False
assert data["safety_boundary"]["performs_mmio_writes"] is False
assert data["safety_boundary"]["driverkit_activation"] is False

print("Stage 8 safe fixture validation passed")
PY

cat > "$UNSAFE_ROOT/src/unsafe_placeholder.cpp" <<EOF
void unsafe_placeholder(void) {
    ${MW_TOKEN}(0, 0, 0);
}
EOF

set +e
./scripts/audit-forbidden-bar-ops.py --root "$UNSAFE_ROOT" --out-dir "$UNSAFE_ROOT/out"
UNSAFE_EXIT="$?"
set -e

test "$UNSAFE_EXIT" -eq 1

python3 - <<PY
import json
from pathlib import Path

p = Path("$UNSAFE_ROOT/out/forbidden-bar-operation-audit.json")
data = json.loads(p.read_text())

assert data["decision"] == "FAIL_BLOCKED_OPERATION_FOUND"
assert data["block_count"] >= 1

print("Stage 8 unsafe fixture validation passed")
PY

echo
echo "== Stage 8 repo audit =="
REPO_AUDIT_OUT="$TMP_ROOT/repo-audit"
./scripts/audit-forbidden-bar-ops.py --root "$ROOT" --out-dir "$REPO_AUDIT_OUT"
test -s "$REPO_AUDIT_OUT/forbidden-bar-operation-audit.json"
test -s "$REPO_AUDIT_OUT/forbidden-bar-operation-audit.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$REPO_AUDIT_OUT/forbidden-bar-operation-audit.json")
data = json.loads(p.read_text())

assert data["decision"] in {"PASS_NO_FORBIDDEN_BAR_OPS", "REVIEW_REQUIRED"}
assert data["block_count"] == 0
assert data["safety_boundary"]["read_only"] is True
assert data["safety_boundary"]["performs_mmio_reads"] is False
assert data["safety_boundary"]["performs_mmio_writes"] is False
assert data["safety_boundary"]["driverkit_activation"] is False

print("Repo forbidden BAR operation audit validation passed")
PY

rm -rf scripts/__pycache__

echo
echo "== BAR safety gates passed =="
