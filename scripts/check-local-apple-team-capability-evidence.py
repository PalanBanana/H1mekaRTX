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
    "apple_development": re.compile(r"Apple Development:[^\n\r]+"),
    "developer_id_application": re.compile(r"Developer ID Application:[^\n\r]+"),
}

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/local-apple-team-capability-evidence-collector.json"
doc_path = ROOT / "docs/driverkit/local-apple-team-capability-evidence-collector.md"
collector_path = ROOT / "scripts/collect-local-apple-team-capability-evidence.py"
summary_json = OUT / "local-apple-team-capability-evidence-summary.json"
summary_md = OUT / "local-apple-team-capability-evidence-summary.md"
phase60r_manifest = ROOT / "tools/driverkit-buildable-scaffold/apple-developer-entitlement-request-checklist.json"
phase60q_manifest = ROOT / "tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60r = read_json(phase60r_manifest)
phase60q = read_json(phase60q_manifest)
collector = collector_path.read_text(encoding="utf-8", errors="replace") if collector_path.exists() else ""

checks = []
for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("collector_exists", collector_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("phase60r_manifest_exists", phase60r_manifest),
    ("phase60q_manifest_exists", phase60q_manifest),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_apple_team_capability_evidence_collector.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_apple_team_capability_evidence_summary.v1"), "summary schema")
add(checks, "phase60r_schema", bool(phase60r and phase60r.get("schema") == "h1mekartx.apple_developer_entitlement_request_checklist.v1"), "phase60r schema")
add(checks, "phase60q_schema", bool(phase60q and phase60q.get("schema") == "h1mekartx.provisioning_entitlement_hardblock_gate.v1"), "phase60q schema")

for field in [
    "local_apple_team_capability_evidence_collector_ready",
    "local_evidence_only",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "xcodebuild_build_attempted_by_this_phase",
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

for token in [
    "xcodebuild",
    "-showBuildSettings",
    "security",
    "find-identity",
    "Personal development teams",
    "Please enable Driverkit",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "collector_contains_" + token.replace(" ", "_").replace("-", "_").replace(".", "_"), token in collector, token)

if summary:
    for field in [
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
    ]:
        add(checks, f"summary_{field}_true", summary.get(field) is True, field)

    for field in [
        "xcode_present",
        "driverkit_sdk_present",
        "macosx_sdk_present",
        "apple_development_identity_present",
        "xcode_project_present",
        "personal_team_blocker_observed",
        "system_extension_capability_blocker_observed",
        "driverkit_enable_blocker_observed",
        "host_profile_missing_observed",
        "dext_profile_missing_observed",
        "paid_team_proven",
        "driverkit_entitlement_approval_proven",
        "pci_transport_entitlement_approval_proven",
        "system_extension_capability_proven",
        "phase61_allowed_now",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

    add(checks, "summary_phase61_false", summary.get("phase61_allowed_now") is False, "phase61 false")
    add(checks, "summary_provider_open_false", summary.get("provider_open_allowed_now") is False, "provider false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE_READY" if failed == 0 else "FAIL_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE"

report = {
    "schema": "h1mekartx.local_apple_team_capability_evidence_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "local_evidence_only": True,
    "raw_outputs_local_only": True,
    "phase61_allowed_now": False,
    "xcodebuild_build_attempted_by_this_phase": False,
    "activation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "local-apple-team-capability-evidence-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Apple Team Capability Evidence Check

- Decision: `{decision}`
- Local Evidence Only: `True`
- Raw Outputs Local Only: `True`
- Phase 61 Allowed Now: `False`
- Xcodebuild Build Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
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
(OUT / "local-apple-team-capability-evidence-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
