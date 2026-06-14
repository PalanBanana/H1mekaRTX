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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/applications-location-activation-remediation.json"
doc_path = ROOT / "docs/driverkit/applications-location-activation-remediation.md"
script_path = ROOT / "scripts/applications-location-activation-remediation.py"
phase60g_path = ROOT / "tools/driverkit-buildable-scaffold/activation-error-remediation-plan.json"
phase60f_summary_path = OUT / "activation-delegate-diagnostics-remediation-summary.json"

manifest = read_json(manifest_path)
phase60g = read_json(phase60g_path)
phase60f = read_json(phase60f_summary_path)
script_text = script_path.read_text(encoding="utf-8", errors="replace") if script_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "script_exists", script_path.exists(), str(script_path))
add(checks, "phase60g_manifest_exists", phase60g_path.exists(), str(phase60g_path))
add(checks, "phase60f_summary_exists", phase60f_summary_path.exists(), str(phase60f_summary_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.applications_location_activation_remediation.v1"), "manifest schema")
add(checks, "phase60g_schema", bool(phase60g and phase60g.get("schema") == "h1mekartx.activation_error_remediation_plan.v1"), "phase60g schema")
add(checks, "phase60f_summary_schema", bool(phase60f and phase60f.get("schema") == "h1mekartx.activation_delegate_diagnostics_remediation_summary.v1"), "phase60f summary schema")

for field in [
    "applications_location_activation_remediation_ready",
    "default_refuses_staging",
    "default_refuses_activation",
    "hard_optin_flags_required",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "ci_staging_attempted",
    "ci_activation_attempted",
    "activation_submitted_by_default",
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

for token in [
    "--i-understand-applications-staging",
    "--stage-to-applications",
    "--submit-activation",
    "--signing-identity",
    "--output-under-host-report-bundle",
    "--replace-existing",
    "--use-sudo",
    "/Applications/H1mekaRTXHost.app",
    "ditto",
    "systemextensionsctl",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "script_contains_" + token.replace("-", "_").replace("/", "_"), token in script_text, token)

if phase60f:
    add(checks, "phase60f_error_domain_os_system_extension", phase60f.get("delegate_error_domain") == "OSSystemExtensionErrorDomain", str(phase60f.get("delegate_error_domain")))
    add(checks, "phase60f_error_code_3", str(phase60f.get("delegate_error_code")) == "3", str(phase60f.get("delegate_error_code")))

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION_READY" if failed == 0 else "FAIL_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION"

report = {
    "schema": "h1mekartx.applications_location_activation_remediation_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "applications_location_activation_remediation_ready": failed == 0,
    "default_refuses_staging": True,
    "default_refuses_activation": True,
    "ci_staging_attempted": False,
    "ci_activation_attempted": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "applications-location-activation-remediation-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Applications Location Activation Remediation Check

- Decision: `{decision}`
- Default Refuses Staging: `True`
- Default Refuses Activation: `True`
- CI Staging Attempted: `False`
- CI Activation Attempted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "applications-location-activation-remediation-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
