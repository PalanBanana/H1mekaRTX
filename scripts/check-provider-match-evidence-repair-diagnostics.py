#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

SCHEMA = "h1mekartx.provider_match_evidence_repair_diagnostics_check.v1"

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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-evidence-repair-diagnostics.json"
doc_path = ROOT / "docs/driverkit/provider-match-evidence-repair-diagnostics.md"
summary_json = OUT / "provider-match-evidence-repair-diagnostics-summary.json"
summary_md = OUT / "provider-match-evidence-repair-diagnostics-summary.md"
phase60_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json"
phase59_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60_manifest = read_json(phase60_manifest_path)
phase59_manifest = read_json(phase59_manifest_path)

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase60_manifest_exists", phase60_manifest_path.exists(), str(phase60_manifest_path))
add(checks, "phase59_manifest_exists", phase59_manifest_path.exists(), str(phase59_manifest_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_evidence_repair_diagnostics.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.provider_match_evidence_repair_diagnostics_summary.v1"), "summary schema")
add(checks, "phase60_schema", bool(phase60_manifest and phase60_manifest.get("schema") == "h1mekartx.provider_match_without_open_readiness_gate.v1"), "phase60 schema")
add(checks, "phase59_schema", bool(phase59_manifest and phase59_manifest.get("schema") == "h1mekartx.dext_load_provider_match_status_evidence.v1"), "phase59 schema")

for field in [
    "read_only_diagnostics_only",
    "raw_stdout_not_committed",
    "raw_stderr_not_committed",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)
    add(checks, f"summary_{field}_true", bool(summary and summary.get(field) is True), field)

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
    repair = summary.get("repair_decision", {})
    for field in [
        "host_bundle_exists",
        "dext_bundle_exists",
        "host_info_parse_ok",
        "dext_info_parse_ok",
        "host_bundle_id_matches",
        "dext_bundle_id_matches",
        "dext_personalities_present",
        "dext_personality_provider_class_matches",
        "dext_personality_iopcimatch_matches",
        "systemextensionsctl_available",
        "ioreg_available",
        "provider_open_still_blocked",
        "ioserviceopen_still_blocked",
        "bar_mapping_still_blocked",
        "gpu_command_submission_still_blocked",
        "dock_transparency_blur_proof_still_blocked",
    ]:
        add(checks, f"derived_{field}_recorded", field in derived, field)

    add(checks, "repair_decision_present", bool(repair), "repair decision")
    add(checks, "repair_provider_open_allowed_false", repair.get("provider_open_allowed") is False if repair else False, "provider open false")
    add(checks, "repair_ready_recorded", "repaired_provider_match_ready" in repair if repair else False, "repair ready")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS_READY" if failed == 0 else "FAIL_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS"

report = {
    "schema": SCHEMA,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "read_only_diagnostics_only": True,
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

(OUT / "provider-match-evidence-repair-diagnostics-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Provider Match Evidence Repair Diagnostics Check

- Decision: `{decision}`
- Read-Only Diagnostics Only: `True`
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
(OUT / "provider-match-evidence-repair-diagnostics-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
