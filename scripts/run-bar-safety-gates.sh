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
echo "== Phase 1 fixture: host + UI compositor diagnostics =="
HOST_UI_OUT="$TMP_ROOT/host-ui-diagnostics-check"
./scripts/check-host-diagnostics-report.py --root "$ROOT" --out-dir "$HOST_UI_OUT"
test -s "$HOST_UI_OUT/host-ui-diagnostics-check.json"
test -s "$HOST_UI_OUT/host-ui-diagnostics-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$HOST_UI_OUT/host-ui-diagnostics-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.host_ui_diagnostics_check.v1"
assert data["decision"] == "PASS_HOST_UI_DIAGNOSTICS_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_static_check"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["ui_compositor_proof"] is False
assert data["safety_boundary"]["metal_proof"] is False

print("Phase 1 host + UI compositor diagnostics validation passed")
PY

echo
echo "== Phase 1 static contract: diagnostics bundle runner =="
PHASE1_RUNNER_OUT="$TMP_ROOT/phase1-diagnostics-bundle-runner-check"
./scripts/check-phase1-diagnostics-bundle-runner.py --root "$ROOT" --out-dir "$PHASE1_RUNNER_OUT"
test -s "$PHASE1_RUNNER_OUT/phase1-diagnostics-bundle-runner-check.json"
test -s "$PHASE1_RUNNER_OUT/phase1-diagnostics-bundle-runner-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$PHASE1_RUNNER_OUT/phase1-diagnostics-bundle-runner-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.phase1_diagnostics_bundle_runner_check.v1"
assert data["decision"] == "PASS_PHASE1_DIAGNOSTICS_BUNDLE_RUNNER_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_static_check"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["bar_mapping"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["ui_compositor_proof"] is False
assert data["safety_boundary"]["metal_proof"] is False

print("Phase 1 diagnostics bundle runner validation passed")
PY

echo
echo "== Phase 2 static contract: UI compositor proof schema =="
UI_SCHEMA_OUT="$TMP_ROOT/ui-compositor-proof-schema-check"
./scripts/check-ui-compositor-proof-schema.py --root "$ROOT" --out-dir "$UI_SCHEMA_OUT"
test -s "$UI_SCHEMA_OUT/ui-compositor-proof-schema-check.json"
test -s "$UI_SCHEMA_OUT/ui-compositor-proof-schema-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$UI_SCHEMA_OUT/ui-compositor-proof-schema-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.ui_compositor_proof_schema_check.v1"
assert data["decision"] == "PASS_UI_COMPOSITOR_PROOF_SCHEMA_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_static_check"] is True
assert data["safety_boundary"]["runs_live_diagnostics"] is False
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["windowserver_injection"] is False
assert data["safety_boundary"]["dock_injection"] is False
assert data["safety_boundary"]["private_framework_patching"] is False
assert data["safety_boundary"]["fake_metal_device_spoofing"] is False
assert data["safety_boundary"]["ui_compositor_proof_claim"] is False
assert data["safety_boundary"]["metal_proof_claim"] is False

print("Phase 2 UI compositor proof schema validation passed")
PY

echo
echo "== Phase 2 fixture: UI compositor sample diagnostics =="
UI_SAMPLE_OUT="$TMP_ROOT/ui-compositor-sample-diagnostics-check"
./scripts/check-ui-compositor-sample-diagnostics.py --root "$ROOT" --out-dir "$UI_SAMPLE_OUT"
test -s "$UI_SAMPLE_OUT/ui-compositor-sample-diagnostics-check.json"
test -s "$UI_SAMPLE_OUT/ui-compositor-sample-diagnostics-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$UI_SAMPLE_OUT/ui-compositor-sample-diagnostics-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.ui_compositor_sample_diagnostics_check.v1"
assert data["decision"] == "PASS_UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_fixture_check"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["process_injection"] is False
assert data["safety_boundary"]["windowserver_injection"] is False
assert data["safety_boundary"]["dock_injection"] is False
assert data["safety_boundary"]["private_framework_patching"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["ui_compositor_proof"] is False
assert data["safety_boundary"]["metal_proof"] is False

print("Phase 2 UI compositor sample diagnostics validation passed")
PY

echo
echo "== Phase 2 fixture: UI GPU attribution diagnostics =="
UI_ATTRIBUTION_OUT="$TMP_ROOT/ui-gpu-attribution-diagnostics-check"
./scripts/check-ui-gpu-attribution-diagnostics.py --root "$ROOT" --out-dir "$UI_ATTRIBUTION_OUT"
test -s "$UI_ATTRIBUTION_OUT/ui-gpu-attribution-diagnostics-check.json"
test -s "$UI_ATTRIBUTION_OUT/ui-gpu-attribution-diagnostics-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$UI_ATTRIBUTION_OUT/ui-gpu-attribution-diagnostics-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.ui_gpu_attribution_diagnostics_check.v1"
assert data["decision"] == "PASS_UI_GPU_ATTRIBUTION_DIAGNOSTICS_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_fixture_check"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["process_injection"] is False
assert data["safety_boundary"]["windowserver_injection"] is False
assert data["safety_boundary"]["dock_injection"] is False
assert data["safety_boundary"]["private_framework_patching"] is False
assert data["safety_boundary"]["sip_bypass"] is False
assert data["safety_boundary"]["amfi_bypass"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["bar_mapping"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["trusted_ui_gpu_attribution_claim"] is False
assert data["safety_boundary"]["ui_compositor_proof"] is False
assert data["safety_boundary"]["metal_proof"] is False

print("Phase 2 UI GPU attribution diagnostics validation passed")
PY

echo
echo "== Phase 2 fixture: UI workload correlation report =="
UI_WORKLOAD_OUT="$TMP_ROOT/ui-workload-correlation-report-check"
./scripts/check-ui-workload-correlation-report.py --root "$ROOT" --out-dir "$UI_WORKLOAD_OUT"
test -s "$UI_WORKLOAD_OUT/ui-workload-correlation-report-check.json"
test -s "$UI_WORKLOAD_OUT/ui-workload-correlation-report-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$UI_WORKLOAD_OUT/ui-workload-correlation-report-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.ui_workload_correlation_report_check.v1"
assert data["decision"] == "PASS_UI_WORKLOAD_CORRELATION_REPORT_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_fixture_check"] is True
assert data["safety_boundary"]["uses_existing_reports_only"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["device_ownership_request"] is False
assert data["safety_boundary"]["windowserver_injection"] is False
assert data["safety_boundary"]["dock_injection"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["bar_mapping"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["rtx5070_shader_execution"] is False
assert data["safety_boundary"]["trusted_rtx5070_workload_attribution_claim"] is False
assert data["safety_boundary"]["ui_compositor_proof"] is False
assert data["safety_boundary"]["metal_proof"] is False

print("Phase 2 UI workload correlation report validation passed")
PY

echo
echo "== Phase 2 fixture: UI compositor readiness matrix =="
UI_READINESS_OUT="$TMP_ROOT/ui-compositor-readiness-matrix-check"
./scripts/check-ui-compositor-readiness-matrix.py --root "$ROOT" --out-dir "$UI_READINESS_OUT"
test -s "$UI_READINESS_OUT/ui-compositor-readiness-matrix-check.json"
test -s "$UI_READINESS_OUT/ui-compositor-readiness-matrix-check.md"

python3 - <<PY
import json
from pathlib import Path

p = Path("$UI_READINESS_OUT/ui-compositor-readiness-matrix-check.json")
data = json.loads(p.read_text())

assert data["schema"] == "h1mekartx.ui_compositor_readiness_matrix_check.v1"
assert data["decision"] == "PASS_UI_COMPOSITOR_READINESS_MATRIX_READY"
assert data["failed_count"] == 0
assert data["safety_boundary"]["read_only_fixture_check"] is True
assert data["safety_boundary"]["uses_existing_reports_only"] is True
assert data["safety_boundary"]["driverkit_activation"] is False
assert data["safety_boundary"]["system_extension_activation"] is False
assert data["safety_boundary"]["pci_config_writes"] is False
assert data["safety_boundary"]["mmio_reads"] is False
assert data["safety_boundary"]["mmio_writes"] is False
assert data["safety_boundary"]["gpu_command_submission"] is False
assert data["safety_boundary"]["ui_compositor_proof_claim"] is False
assert data["safety_boundary"]["metal_proof_claim"] is False

print("Phase 2 UI compositor readiness matrix validation passed")
PY

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
