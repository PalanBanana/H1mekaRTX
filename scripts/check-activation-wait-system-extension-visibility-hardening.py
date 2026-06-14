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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-wait-system-extension-visibility-hardening.json"
doc_path = ROOT / "docs/driverkit/activation-wait-system-extension-visibility-hardening.md"
script_path = ROOT / "scripts/activation-wait-system-extension-visibility-hardening.py"
phase60c_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-personality-entitlement-fix-plan.json"
phase57b_path = ROOT / "tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json"

manifest = read_json(manifest_path)
phase60c = read_json(phase60c_path)
phase57b = read_json(phase57b_path)
script = script_path.read_text(encoding="utf-8", errors="replace") if script_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "script_exists", script_path.exists(), str(script_path))
add(checks, "phase60c_manifest_exists", phase60c_path.exists(), str(phase60c_path))
add(checks, "phase57b_manifest_exists", phase57b_path.exists(), str(phase57b_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.activation_wait_system_extension_visibility_hardening.v1"), "manifest schema")
add(checks, "phase60c_schema", bool(phase60c and phase60c.get("schema") == "h1mekartx.provider_match_personality_entitlement_fix_plan.v1"), "phase60c schema")
add(checks, "phase57b_schema", bool(phase57b and phase57b.get("schema") == "h1mekartx.actual_local_activation_hard_optin.v1"), "phase57b schema")

for field in [
    "activation_wait_visibility_hardening_ready",
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
    "--i-understand-local-activation-visibility",
    "--submit-activation",
    "--signing-identity",
    "--output-under-host-report-bundle",
    "--wait-seconds",
    "--poll-interval-seconds",
    "systemextensionsctl",
    "dev.h1meka.H1mekaRTXDriver",
    "visibility_poll_attempted",
    "extension_identifier_observed",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "script_contains_" + token.replace("-", "_").replace(".", "_"), token in script, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_ACTIVATION_WAIT_VISIBILITY_HARDENING_READY" if failed == 0 else "FAIL_ACTIVATION_WAIT_VISIBILITY_HARDENING"

report = {
    "schema": "h1mekartx.activation_wait_visibility_hardening_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "activation_wait_visibility_hardening_ready": failed == 0,
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

(OUT / "activation-wait-system-extension-visibility-hardening-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Activation Wait System Extension Visibility Hardening Check

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
(OUT / "activation-wait-system-extension-visibility-hardening-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
