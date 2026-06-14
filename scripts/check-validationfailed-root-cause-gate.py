#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone

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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json"
doc_path = ROOT / "docs/driverkit/validationfailed-root-cause-gate.md"
summary_json = OUT / "validationfailed-root-cause-summary.json"
summary_md = OUT / "validationfailed-root-cause-summary.md"
phase60i_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/applications-location-activation-remediation.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60i = read_json(phase60i_manifest_path)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase60i_manifest_exists", phase60i_manifest_path.exists(), str(phase60i_manifest_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.validationfailed_root_cause_gate.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.validationfailed_root_cause_summary.v1"), "summary schema")
add(checks, "phase60i_schema", bool(phase60i and phase60i.get("schema") == "h1mekartx.applications_location_activation_remediation.v1"), "phase60i schema")

for field in [
    "validationfailed_root_cause_gate_ready",
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
    add(checks, "summary_error_domain_code9_recorded", summary.get("delegate_error_domain") == "OSSystemExtensionErrorDomain" and str(summary.get("delegate_error_code")) == "9", "OSSystemExtensionErrorDomain/9")
    add(checks, "summary_applications_staged", summary.get("staged_to_applications") is True, "staged")
    add(checks, "summary_activation_submitted", summary.get("activation_submitted") is True, "activation submitted")
    add(checks, "summary_spctl_host_rejected_recorded", "spctl_host_rejected" in summary, "spctl host")
    add(checks, "summary_spctl_dext_rejected_recorded", "spctl_dext_rejected" in summary, "spctl dext")
    add(checks, "summary_driverkit_entitlement_recorded", "driverkit_entitlement_present" in summary, "driverkit entitlement")
    add(checks, "summary_pci_entitlement_recorded", "pci_transport_entitlement_present" in summary, "pci entitlement")
    add(checks, "summary_xcode_driverkit_binary_proven_recorded", "dext_xcode_driverkit_build_proven" in summary, "real DriverKit binary")
    add(checks, "summary_next_gate_phase60l", summary.get("remediation", {}).get("next_gate") == "phase60l-real-driverkit-dext-build-gate", "phase60l")
    add(checks, "summary_phase61_allowed_false", summary.get("remediation", {}).get("phase61_allowed_now") is False, "phase61 false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_VALIDATIONFAILED_ROOT_CAUSE_GATE_READY" if failed == 0 else "FAIL_VALIDATIONFAILED_ROOT_CAUSE_GATE"

report = {
    "schema": "h1mekartx.validationfailed_root_cause_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "remediation_gate_only": True,
    "phase61_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase60l-real-driverkit-dext-build-gate",
    "checks": checks,
}

(OUT / "validationfailed-root-cause-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# ValidationFailed Root-Cause Gate Check

- Decision: `{decision}`
- Remediation Gate Only: `True`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60l-real-driverkit-dext-build-gate`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "validationfailed-root-cause-gate-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
