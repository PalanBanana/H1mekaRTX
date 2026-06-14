#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

SCHEMA = "h1mekartx.provider_match_without_open_readiness_gate_check.v1"

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json"
doc_path = ROOT / "docs/driverkit/provider-match-without-open-readiness-gate.md"
phase59_summary_path = OUT / "dext-load-provider-match-status-summary.json"
phase59_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json"

manifest = read_json(manifest_path)
phase59_summary = read_json(phase59_summary_path)
phase59_manifest = read_json(phase59_manifest_path)

derived = phase59_summary.get("derived", {}) if phase59_summary else {}
readiness = phase59_summary.get("provider_match_readiness", {}) if phase59_summary else {}

activation_command_completed = bool(derived.get("activation_command_completed"))
extension_status_observed = bool(derived.get("extension_identifier_observed_in_systemextensionsctl"))
rtx_vendor_observed = bool(derived.get("rtx_vendor_10de_observed"))
rtx_device_observed = bool(derived.get("rtx_device_2f04_observed"))
rtx_iopcimatch_observed = bool(derived.get("rtx_iopcimatch_2f0410de_observed"))
provider_open_still_blocked = bool(derived.get("provider_open_still_blocked"))
ioserviceopen_still_blocked = bool(derived.get("ioserviceopen_still_blocked"))
bar_mapping_still_blocked = bool(derived.get("bar_mapping_still_blocked"))
gpu_command_submission_still_blocked = bool(derived.get("gpu_command_submission_still_blocked"))

provider_match_without_open_ready = bool(
    phase59_summary
    and activation_command_completed
    and extension_status_observed
    and rtx_vendor_observed
    and rtx_device_observed
    and provider_open_still_blocked
    and ioserviceopen_still_blocked
    and bar_mapping_still_blocked
    and gpu_command_submission_still_blocked
)

block_reasons = []
if not phase59_summary:
    block_reasons.append("phase59_summary_missing")
if not activation_command_completed:
    block_reasons.append("activation_command_completed_false_or_missing")
if not extension_status_observed:
    block_reasons.append("extension_identifier_not_observed_in_systemextensionsctl")
if not rtx_vendor_observed:
    block_reasons.append("rtx_vendor_0x10de_not_observed")
if not rtx_device_observed:
    block_reasons.append("rtx_device_0x2f04_not_observed")
if not provider_open_still_blocked:
    block_reasons.append("provider_open_boundary_not_blocked")
if not ioserviceopen_still_blocked:
    block_reasons.append("ioserviceopen_boundary_not_blocked")
if not bar_mapping_still_blocked:
    block_reasons.append("bar_mapping_boundary_not_blocked")
if not gpu_command_submission_still_blocked:
    block_reasons.append("gpu_command_submission_boundary_not_blocked")

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "phase59_summary_exists", phase59_summary_path.exists(), str(phase59_summary_path))
add(checks, "phase59_manifest_exists", phase59_manifest_path.exists(), str(phase59_manifest_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_without_open_readiness_gate.v1"), "manifest schema")
add(checks, "phase59_summary_schema", bool(phase59_summary and phase59_summary.get("schema") == "h1mekartx.dext_load_provider_match_status_summary.v1"), "phase59 summary schema")
add(checks, "phase59_manifest_schema", bool(phase59_manifest and phase59_manifest.get("schema") == "h1mekartx.dext_load_provider_match_status_evidence.v1"), "phase59 manifest schema")

for field in [
    "provider_match_without_open_readiness_gate_ready",
    "preflight_gate_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "provider_open_allowed_now",
    "ioserviceopen_allowed_now",
    "bar_mapping_allowed_now",
    "gpu_command_submission_allowed_now",
    "activation_submitted_by_this_phase",
    "deactivation_submitted_by_this_phase",
    "install_attempted",
    "manual_dext_load_attempted",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

add(checks, "phase59_readiness_provider_open_allowed_false", readiness.get("provider_open_allowed") is False if readiness else True, "provider open allowed false")
add(checks, "phase59_derived_provider_open_still_blocked", provider_open_still_blocked, "provider open blocked")
add(checks, "phase59_derived_ioserviceopen_still_blocked", ioserviceopen_still_blocked, "IOServiceOpen blocked")
add(checks, "phase59_derived_bar_mapping_still_blocked", bar_mapping_still_blocked, "BAR mapping blocked")
add(checks, "phase59_derived_gpu_command_submission_still_blocked", gpu_command_submission_still_blocked, "GPU command blocked")

failed = sum(1 for c in checks if not c["passed"])
if failed:
    decision = "FAIL_PROVIDER_MATCH_WITHOUT_OPEN_READINESS_GATE"
elif provider_match_without_open_ready:
    decision = "PASS_PROVIDER_MATCH_WITHOUT_OPEN_READY"
else:
    decision = "PASS_PROVIDER_MATCH_WITHOUT_OPEN_BLOCKED_PENDING_EVIDENCE"

report = {
    "schema": SCHEMA,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "provider_match_without_open_ready": provider_match_without_open_ready,
    "provider_open_allowed_now": False,
    "ioserviceopen_allowed_now": False,
    "bar_mapping_allowed_now": False,
    "gpu_command_submission_allowed_now": False,
    "activation_command_completed": activation_command_completed,
    "extension_identifier_observed_in_systemextensionsctl": extension_status_observed,
    "rtx_vendor_10de_observed": rtx_vendor_observed,
    "rtx_device_2f04_observed": rtx_device_observed,
    "rtx_iopcimatch_2f0410de_observed": rtx_iopcimatch_observed,
    "provider_open_still_blocked": provider_open_still_blocked,
    "ioserviceopen_still_blocked": ioserviceopen_still_blocked,
    "bar_mapping_still_blocked": bar_mapping_still_blocked,
    "gpu_command_submission_still_blocked": gpu_command_submission_still_blocked,
    "block_reasons": block_reasons,
    "next_gate_if_ready": "provider_open_hard_optin_preflight_no_bar_no_gpu_commands",
    "next_gate_if_blocked": "collect or fix Phase 59 dext/provider status evidence",
    "checks": checks,
}

(OUT / "provider-match-without-open-readiness-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
block_rows = "\n".join(f"| `{reason}` |" for reason in block_reasons) or "| `none` |"

md = f"""# Provider Match Without Open Readiness Gate Check

- Decision: `{decision}`
- Provider Match Without Open Ready: `{provider_match_without_open_ready}`
- Provider Open Allowed Now: `False`
- IOServiceOpen Allowed Now: `False`
- BAR Mapping Allowed Now: `False`
- GPU Command Submission Allowed Now: `False`
- Activation Command Completed: `{activation_command_completed}`
- Extension Identifier Observed In Systemextensionsctl: `{extension_status_observed}`
- RTX Vendor 0x10de Observed: `{rtx_vendor_observed}`
- RTX Device 0x2f04 Observed: `{rtx_device_observed}`
- RTX IOPCIMatch 0x2f0410de Observed: `{rtx_iopcimatch_observed}`
- Provider Open Still Blocked: `{provider_open_still_blocked}`
- IOServiceOpen Still Blocked: `{ioserviceopen_still_blocked}`
- BAR Mapping Still Blocked: `{bar_mapping_still_blocked}`
- GPU Command Submission Still Blocked: `{gpu_command_submission_still_blocked}`

## Block Reasons

| Reason |
| --- |
{block_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "provider-match-without-open-readiness-gate-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
