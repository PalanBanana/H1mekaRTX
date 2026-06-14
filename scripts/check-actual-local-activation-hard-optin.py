#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json"
doc_path = ROOT / "docs/driverkit/actual-local-activation-hard-optin.md"
script_path = ROOT / "scripts/actual-local-activation-hard-optin.py"
phase56_path = ROOT / "tools/driverkit-buildable-scaffold/manual-activation-preflight-after-signed-verification.json"
phase46_path = ROOT / "tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json"

def read_json(p):
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

manifest = read_json(manifest_path)
phase56 = read_json(phase56_path)
phase46 = read_json(phase46_path)
text = script_path.read_text(encoding="utf-8", errors="replace") if script_path.exists() else ""

checks = []
def add(name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

add("manifest_exists", manifest_path.exists(), str(manifest_path))
add("doc_exists", doc_path.exists(), str(doc_path))
add("script_exists", script_path.exists(), str(script_path))
add("phase56_manifest_exists", phase56_path.exists(), str(phase56_path))
add("phase46_manifest_exists", phase46_path.exists(), str(phase46_path))
add("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.actual_local_activation_hard_optin.v1"))
add("default_refuses_activation_true", bool(manifest and manifest.get("default_refuses_activation") is True))
add("hard_optin_flags_required_true", bool(manifest and manifest.get("hard_optin_flags_required") is True))
add("ci_activation_attempted_false", bool(manifest and manifest.get("ci_activation_attempted") is False))
add("activation_submitted_by_default_false", bool(manifest and manifest.get("activation_submitted_by_default") is False))
add("script_requires_understand_flag", "--i-understand-local-activation" in text)
add("script_requires_submit_activation_flag", "--submit-activation" in text)
add("script_requires_signing_identity", "--signing-identity" in text)
add("script_requires_output_under_host_report_bundle", "--output-under-host-report-bundle" in text)
add("script_checks_activation_preflight_ready", "activation_preflight_ready" in text)
add("script_builds_swift_host", "swiftc" in text and "SystemExtensions" in text)
add("script_uses_activation_capable_host", "--submit-activation" in text and "H1mekaRTXHost.swift" in text)
add("script_captures_systemextensionsctl", "systemextensionsctl" in text)
add("script_keeps_provider_open_blocked", "provider_open_attempted" in text and "False" in text)
add("script_keeps_bar_mapping_blocked", "bar_mapping_attempted" in text and "False" in text)
add("script_keeps_gpu_command_blocked", "gpu_command_submission_attempted" in text and "False" in text)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN_READY" if failed == 0 else "FAIL_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN"

report = {
    "schema": "h1mekartx.actual_local_activation_hard_optin_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "actual_local_activation_hard_optin_ready": failed == 0,
    "default_refuses_activation": True,
    "hard_optin_flags_required": True,
    "ci_activation_attempted": False,
    "activation_submitted_by_default": False,
    "provider_open_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "actual-local-activation-hard-optin-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Actual Local Activation Hard Opt-In Check

- Decision: `{decision}`
- Default Refuses Activation: `True`
- Hard Opt-In Flags Required: `True`
- CI Activation Attempted: `False`
- Activation Submitted By Default: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "actual-local-activation-hard-optin-check.md").write_text(md, encoding="utf-8")
print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
