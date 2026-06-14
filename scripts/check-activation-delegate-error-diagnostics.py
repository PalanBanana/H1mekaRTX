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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-delegate-error-diagnostics.json"
doc_path = ROOT / "docs/driverkit/activation-delegate-error-diagnostics.md"
swift_path = ROOT / "tools/driverkit-buildable-scaffold/H1mekaRTXActivationDiagnosticsHost.swift"
script_path = ROOT / "scripts/activation-delegate-error-diagnostics.py"
phase60d_path = ROOT / "tools/driverkit-buildable-scaffold/activation-wait-system-extension-visibility-hardening.json"

manifest = read_json(manifest_path)
phase60d = read_json(phase60d_path)
swift_text = swift_path.read_text(encoding="utf-8", errors="replace") if swift_path.exists() else ""
script_text = script_path.read_text(encoding="utf-8", errors="replace") if script_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "swift_diagnostics_host_exists", swift_path.exists(), str(swift_path))
add(checks, "script_exists", script_path.exists(), str(script_path))
add(checks, "phase60d_manifest_exists", phase60d_path.exists(), str(phase60d_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.activation_delegate_error_diagnostics.v1"), "manifest schema")
add(checks, "phase60d_schema", bool(phase60d and phase60d.get("schema") == "h1mekartx.activation_wait_system_extension_visibility_hardening.v1"), "phase60d schema")

for field in [
    "activation_delegate_error_diagnostics_ready",
    "default_refuses_activation",
    "hard_optin_flags_required",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "ci_activation_attempted",
    "activation_submitted_by_default",
    "deactivation_submitted_by_default",
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
    "OSSystemExtensionRequestDelegate",
    "requestNeedsUserApproval",
    "didFinishWithResult",
    "didFailWithError",
    "actionForReplacingExtension",
    "OSSystemExtensionManager.shared.submitRequest",
]:
    add(checks, "swift_contains_" + token.replace(".", "_"), token in swift_text, token)

for token in [
    "--i-understand-activation-delegate-diagnostics",
    "--submit-activation",
    "--signing-identity",
    "--output-under-host-report-bundle",
    "\"log\", \"show\"",
    "sysextd",
    "kernelmanagerd",
    "systemextensionsctl",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "script_contains_" + token.replace("-", "_").replace(" ", "_"), token in script_text, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_ACTIVATION_DELEGATE_ERROR_DIAGNOSTICS_READY" if failed == 0 else "FAIL_ACTIVATION_DELEGATE_ERROR_DIAGNOSTICS"

report = {
    "schema": "h1mekartx.activation_delegate_error_diagnostics_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "activation_delegate_error_diagnostics_ready": failed == 0,
    "default_refuses_activation": True,
    "hard_optin_flags_required": True,
    "ci_activation_attempted": False,
    "activation_submitted_by_default": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "activation-delegate-error-diagnostics-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n", encoding="utf-8")

rows = "\\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Activation Delegate Error Diagnostics Check

- Decision: `{decision}`
- Default Refuses Activation: `True`
- Hard Opt-In Flags Required: `True`
- CI Activation Attempted: `False`
- Activation Submitted By Default: `False`
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
(OUT / "activation-delegate-error-diagnostics-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
