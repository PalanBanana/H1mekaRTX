#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-error-remediation-plan.json"
doc_path = ROOT / "docs/driverkit/activation-error-remediation-plan.md"
swift_path = ROOT / "tools/driverkit-buildable-scaffold/H1mekaRTXActivationDiagnosticsHost.swift"
phase60f_summary_path = OUT / "activation-delegate-diagnostics-remediation-summary.json"
phase60f_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-delegate-diagnostics-remediation-gate.json"
phase60e_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-delegate-error-diagnostics.json"

manifest = read_json(manifest_path)
phase60f_summary = read_json(phase60f_summary_path)
phase60f_manifest = read_json(phase60f_manifest_path)
phase60e_manifest = read_json(phase60e_manifest_path)
swift_text = swift_path.read_text(encoding="utf-8", errors="replace") if swift_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "swift_diagnostics_host_exists", swift_path.exists(), str(swift_path))
add(checks, "phase60f_summary_exists", phase60f_summary_path.exists(), str(phase60f_summary_path))
add(checks, "phase60f_manifest_exists", phase60f_manifest_path.exists(), str(phase60f_manifest_path))
add(checks, "phase60e_manifest_exists", phase60e_manifest_path.exists(), str(phase60e_manifest_path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.activation_error_remediation_plan.v1"), "manifest schema")
add(checks, "phase60f_summary_schema", bool(phase60f_summary and phase60f_summary.get("schema") == "h1mekartx.activation_delegate_diagnostics_remediation_summary.v1"), "phase60f summary schema")
add(checks, "phase60f_manifest_schema", bool(phase60f_manifest and phase60f_manifest.get("schema") == "h1mekartx.activation_delegate_diagnostics_remediation_gate.v1"), "phase60f manifest schema")
add(checks, "phase60e_manifest_schema", bool(phase60e_manifest and phase60e_manifest.get("schema") == "h1mekartx.activation_delegate_error_diagnostics.v1"), "phase60e manifest schema")

for field in [
    "activation_error_remediation_plan_ready",
    "diagnostics_patch_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
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

for bad in [
    "\\\\(nsError.domain)",
    "\\\\(nsError.code)",
    "\\\\(nsError.localizedDescription)",
]:
    add(checks, "swift_no_literal_" + bad.replace("\\\\", "backslash_"), bad not in swift_text, bad)

for good in [
    "\\(nsError.domain)",
    "\\(nsError.code)",
    "\\(nsError.localizedDescription)",
    "H1MEKARTX_SYSEXT_ERROR_DOMAIN=",
    "H1MEKARTX_SYSEXT_ERROR_CODE=",
    "H1MEKARTX_SYSEXT_ERROR_DESCRIPTION=",
    "H1MEKARTX_SYSEXT_ERROR_TEXT=",
]:
    add(checks, "swift_contains_" + good.replace("\\", "interp_").replace("=", "_equals"), good in swift_text, good)

if phase60f_summary:
    remediation = phase60f_summary.get("remediation", {})
    add(checks, "phase60f_reason_delegate_did_fail", remediation.get("reason") == "delegate_did_fail", str(remediation))
    add(checks, "phase60f_next_gate_phase60g", remediation.get("next_gate") == "phase60g_activation_error_remediation_plan", str(remediation))
    add(checks, "phase60f_delegate_did_fail_true", phase60f_summary.get("delegate_did_fail") is True, "delegate_did_fail")

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_ACTIVATION_ERROR_REMEDIATION_PLAN_READY" if failed == 0 else "FAIL_ACTIVATION_ERROR_REMEDIATION_PLAN"

report = {
    "schema": "h1mekartx.activation_error_remediation_plan_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "diagnostics_patch_only": True,
    "activation_submitted_by_this_phase": False,
    "deactivation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate_after_merge": "rerun_phase60e_then_phase60f",
    "checks": checks,
}

(OUT / "activation-error-remediation-plan-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Activation Error Remediation Plan Check

- Decision: `{decision}`
- Diagnostics Patch Only: `True`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate After Merge: `rerun_phase60e_then_phase60f`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "activation-error-remediation-plan-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
