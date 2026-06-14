#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

SCHEMA = "h1mekartx.dext_load_provider_match_status_check.v1"

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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json"
doc_path = ROOT / "docs/driverkit/dext-load-provider-match-status-evidence.md"
summary_json = OUT / "dext-load-provider-match-status-summary.json"
summary_md = OUT / "dext-load-provider-match-status-summary.md"
phase58 = ROOT / "tools/driverkit-buildable-scaffold/local-activation-report-status-sanitizer.json"
phase57b = ROOT / "tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase58_manifest = read_json(phase58)
phase57b_manifest = read_json(phase57b)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase58_manifest_exists", phase58.exists(), str(phase58))
add(checks, "phase57b_manifest_exists", phase57b.exists(), str(phase57b))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.dext_load_provider_match_status_evidence.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.dext_load_provider_match_status_summary.v1"), "summary schema")
add(checks, "phase58_schema", bool(phase58_manifest and phase58_manifest.get("schema") == "h1mekartx.local_activation_report_status_sanitizer.v1"), "phase58 schema")
add(checks, "phase57b_schema", bool(phase57b_manifest and phase57b_manifest.get("schema") == "h1mekartx.actual_local_activation_hard_optin.v1"), "phase57b schema")

for field in [
    "read_only_status_evidence_only",
    "raw_stdout_not_committed",
    "raw_stderr_not_committed",
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
    derived = summary.get("derived", {})
    readiness = summary.get("provider_match_readiness", {})
    add(checks, "activation_report_present", bool(derived.get("activation_report_present")), "activation report")
    add(checks, "activation_command_completed_recorded", "activation_command_completed" in derived, "activation command completed")
    add(checks, "systemextensionsctl_available_recorded", "systemextensionsctl_available" in derived, "systemextensionsctl")
    add(checks, "ioreg_available_recorded", "ioreg_available" in derived, "ioreg")
    add(checks, "rtx_vendor_recorded", "rtx_vendor_10de_observed" in derived, "vendor")
    add(checks, "rtx_device_recorded", "rtx_device_2f04_observed" in derived, "device")
    add(checks, "provider_match_readiness_present", bool(readiness), "readiness")
    add(checks, "provider_open_allowed_false", readiness.get("provider_open_allowed") is False, "provider open false")

    for field in [
        "provider_open_still_blocked",
        "ioserviceopen_still_blocked",
        "bar_mapping_still_blocked",
        "gpu_command_submission_still_blocked",
        "dock_transparency_blur_proof_still_blocked",
    ]:
        add(checks, f"derived_{field}_true", bool(derived.get(field)), field)

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE_READY" if failed == 0 else "FAIL_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE"

report = {
    "schema": SCHEMA,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "read_only_status_evidence_only": True,
    "activation_submitted_by_this_phase": False,
    "deactivation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "dext-load-provider-match-status-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Dext Load + Provider Match Status Check

- Decision: `{decision}`
- Read-Only Status Evidence Only: `True`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
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
(OUT / "dext-load-provider-match-status-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
