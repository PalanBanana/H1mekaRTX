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
}

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-xcode-materialization/xcodeproj-materialization-helper.json"
doc_path = ROOT / "docs/driverkit/xcodeproj-materialization-helper.md"
helper_path = ROOT / "scripts/xcodeproj-materialization-helper.py"
summary_json = OUT / "xcodeproj-materialization-helper-summary.json"
summary_md = OUT / "xcodeproj-materialization-helper-summary.md"
phase60m_manifest = ROOT / "tools/driverkit-xcode-materialization/xcode-driverkit-project-materialization-plan.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60m = read_json(phase60m_manifest)
helper_text = helper_path.read_text(encoding="utf-8", errors="replace") if helper_path.exists() else ""

checks = []
for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("helper_exists", helper_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("phase60m_manifest_exists", phase60m_manifest),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.xcodeproj_materialization_helper.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.xcodeproj_materialization_helper_summary.v1"), "summary schema")
add(checks, "phase60m_schema", bool(phase60m and phase60m.get("schema") == "h1mekartx.xcode_driverkit_project_materialization_plan.v1"), "phase60m schema")

if manifest:
    for field in [
        "xcodeproj_materialization_helper_ready",
        "default_refuses_generation",
        "hard_optin_flags_required",
    ]:
        add(checks, f"manifest_{field}_true", manifest.get(field) is True, field)

    for field in [
        "ci_project_generation_attempted",
        "ci_xcodebuild_attempted",
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
        add(checks, f"manifest_{field}_false", manifest.get(field) is False, field)

for token in [
    "--i-understand-xcodeproj-materialization",
    "--output-under-host-report-bundle",
    "--emit-xcodegen-spec",
    "--materialize-with-xcodegen",
    "--replace-existing",
    "xcodegen",
    "project.yml",
    "H1mekaRTXHost",
    "H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXDriver",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "helper_contains_" + token.replace("-", "_").replace(".", "_"), token in helper_text, token)

if summary:
    for field in [
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
    ]:
        add(checks, f"summary_{field}_true", summary.get(field) is True, field)
    for field in [
        "xcodebuild_attempted_by_this_phase",
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
        add(checks, f"summary_{field}_false", summary.get(field) is False, field)
    add(checks, "summary_project_exists_after_recorded", "project_exists_after" in summary, "project_exists_after")
    add(checks, "summary_phase61_allowed_false", summary.get("remediation", {}).get("phase61_allowed_now") is False, "phase61 false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_XCODEPROJ_MATERIALIZATION_HELPER_READY" if failed == 0 else "FAIL_XCODEPROJ_MATERIALIZATION_HELPER"

report = {
    "schema": "h1mekartx.xcodeproj_materialization_helper_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "local_project_helper_only": True,
    "ci_project_generation_attempted": False,
    "ci_xcodebuild_attempted": False,
    "phase61_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "xcodeproj-materialization-helper-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# XcodeProj Materialization Helper Check

- Decision: `{decision}`
- Local Project Helper Only: `True`
- CI Project Generation Attempted: `False`
- CI Xcodebuild Attempted: `False`
- Phase 61 Allowed Now: `False`
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
(OUT / "xcodeproj-materialization-helper-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
