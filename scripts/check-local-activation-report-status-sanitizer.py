#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

SCHEMA = "h1mekartx.local_activation_report_status_sanitizer_check.v1"

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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/local-activation-report-status-sanitizer.json"
doc_path = ROOT / "docs/driverkit/local-activation-report-status-sanitizer.md"
summary_json = OUT / "local-activation-report-status-summary.json"
summary_md = OUT / "local-activation-report-status-summary.md"
phase57b = ROOT / "tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase57b_manifest = read_json(phase57b)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase57b_manifest_exists", phase57b.exists(), str(phase57b))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_activation_report_status_sanitizer.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_activation_report_status_summary.v1"), "summary schema")
add(checks, "phase57b_schema", bool(phase57b_manifest and phase57b_manifest.get("schema") == "h1mekartx.actual_local_activation_hard_optin.v1"), "phase57b schema")

for field in [
    "sanitizer_only",
    "raw_stdout_not_committed",
    "raw_stderr_not_committed",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)
    add(checks, f"summary_{field}_true", bool(summary and summary.get(field) is True), field)

for field in [
    "activation_submitted_by_sanitizer",
    "deactivation_submitted_by_sanitizer",
    "install_attempted",
    "provider_open_attempted",
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
    add(checks, "local_activation_report_present", summary.get("local_activation_report_present") is True, "local activation report")
    add(checks, "activation_submitted_locally_recorded", "activation_submitted_locally" in summary, "activation_submitted_locally")
    add(checks, "activation_command_returncode_recorded", "activation_command_returncode" in summary, "activation_command_returncode")
    add(checks, "systemextensionsctl_status_recorded", "systemextensionsctl_returncode" in summary, "systemextensionsctl")
    derived = summary.get("derived", {})
    for field in [
        "provider_open_still_blocked",
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
decision = "PASS_LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER_READY" if failed == 0 else "FAIL_LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER"

report = {
    "schema": SCHEMA,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "sanitizer_only": True,
    "activation_submitted_by_sanitizer": False,
    "deactivation_submitted_by_sanitizer": False,
    "provider_open_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "local-activation-report-status-sanitizer-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Activation Report Status Sanitizer Check

- Decision: `{decision}`
- Sanitizer Only: `True`
- Activation Submitted By Sanitizer: `False`
- Deactivation Submitted By Sanitizer: `False`
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
(OUT / "local-activation-report-status-sanitizer-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
