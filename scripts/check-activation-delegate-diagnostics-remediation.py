#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

FORBIDDEN_PATTERNS = {
    "raw_stdout_key": re.compile(r'"stdout"\s*:'),
    "raw_stderr_key": re.compile(r'"stderr"\s*:'),
    "command_key": re.compile(r'"command"\s*:'),
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "developer_id_application": re.compile(r"Developer ID Application:[^\n\r]+"),
    "apple_development": re.compile(r"Apple Development:[^\n\r]+"),
}

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-delegate-diagnostics-remediation-gate.json"
doc_path = ROOT / "docs/driverkit/activation-delegate-diagnostics-remediation-gate.md"
summary_json = OUT / "activation-delegate-diagnostics-remediation-summary.json"
summary_md = OUT / "activation-delegate-diagnostics-remediation-summary.md"
phase60e_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/activation-delegate-error-diagnostics.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60e_manifest = read_json(phase60e_manifest_path)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase60e_manifest_exists", phase60e_manifest_path.exists(), str(phase60e_manifest_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.activation_delegate_diagnostics_remediation_gate.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.activation_delegate_diagnostics_remediation_summary.v1"), "summary schema")
add(checks, "phase60e_schema", bool(phase60e_manifest and phase60e_manifest.get("schema") == "h1mekartx.activation_delegate_error_diagnostics.v1"), "phase60e schema")

for field in [
    "remediation_gate_ready",
    "remediation_gate_only",
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
    add(checks, f"summary_{field}_false", bool(summary and summary.get(field) is False), field)

if summary:
    add(checks, "summary_local_delegate_report_present", summary.get("local_delegate_report_present") is True, "local delegate report")
    add(checks, "summary_activation_submitted_recorded", "activation_submitted_locally" in summary, "activation submitted")
    add(checks, "summary_extension_observed_recorded", "extension_identifier_observed" in summary, "extension observed")
    add(checks, "summary_delegate_finish_recorded", "delegate_did_finish" in summary, "delegate finish")
    add(checks, "summary_delegate_fail_recorded", "delegate_did_fail" in summary, "delegate fail")
    add(checks, "summary_delegate_needs_user_recorded", "delegate_needs_user_approval" in summary, "needs user")
    add(checks, "summary_delegate_timeout_recorded", "delegate_timeout" in summary, "timeout")
    remediation = summary.get("remediation", {})
    add(checks, "remediation_present", bool(remediation), "remediation")
    add(checks, "remediation_next_gate_present", bool(remediation.get("next_gate")), "next gate")
    add(checks, "remediation_phase61_allowed_false", remediation.get("phase61_allowed_now") is False, "phase61 false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_ACTIVATION_DELEGATE_REMEDIATION_GATE_READY" if failed == 0 else "FAIL_ACTIVATION_DELEGATE_REMEDIATION_GATE"

report = {
    "schema": "h1mekartx.activation_delegate_diagnostics_remediation_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "remediation_gate_only": True,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "activation-delegate-diagnostics-remediation-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Activation Delegate Diagnostics Remediation Check

- Decision: `{decision}`
- Remediation Gate Only: `True`
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
(OUT / "activation-delegate-diagnostics-remediation-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
