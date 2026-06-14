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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json"
doc_path = ROOT / "docs/driverkit/real-driverkit-dext-build-gate.md"
script_path = ROOT / "scripts/real-driverkit-dext-build-gate.py"
summary_json = OUT / "real-driverkit-dext-build-gate-summary.json"
summary_md = OUT / "real-driverkit-dext-build-gate-summary.md"
phase60k_path = ROOT / "tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60k = read_json(phase60k_path)
script_text = script_path.read_text(encoding="utf-8", errors="replace") if script_path.exists() else ""

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "script_exists", script_path.exists(), str(script_path))
add(checks, "summary_json_exists", summary_json.exists(), str(summary_json))
add(checks, "summary_md_exists", summary_md.exists(), str(summary_md))
add(checks, "phase60k_manifest_exists", phase60k_path.exists(), str(phase60k_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.real_driverkit_dext_build_gate.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.real_driverkit_dext_build_gate_summary.v1"), "summary schema")
add(checks, "phase60k_schema", bool(phase60k and phase60k.get("schema") == "h1mekartx.validationfailed_root_cause_gate.v1"), "phase60k schema")

for field in [
    "real_driverkit_dext_build_gate_ready",
    "default_refuses_build",
    "hard_optin_flags_required",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
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
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

for token in [
    "--i-understand-local-driverkit-build",
    "--output-under-host-report-bundle",
    "--project",
    "--workspace",
    "--scheme",
    "xcodebuild",
    "--sdk",
    "driverkit",
    "*.dext",
    "codesign",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "script_contains_" + token.replace("-", "_").replace("*", "star").replace(".", "_"), token in script_text, token)

if summary:
    for field in [
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
    ]:
        add(checks, f"summary_{field}_true", summary.get(field) is True, field)
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
        add(checks, f"summary_{field}_false", summary.get(field) is False, field)
    add(checks, "summary_real_driverkit_dext_built_recorded", "real_driverkit_dext_built" in summary, "real dext built recorded")
    add(checks, "summary_phase61_allowed_false", summary.get("remediation", {}).get("phase61_allowed_now") is False, "phase61 false")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_REAL_DRIVERKIT_DEXT_BUILD_GATE_READY" if failed == 0 else "FAIL_REAL_DRIVERKIT_DEXT_BUILD_GATE"

report = {
    "schema": "h1mekartx.real_driverkit_dext_build_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "local_build_gate_only": True,
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

(OUT / "real-driverkit-dext-build-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Real DriverKit Dext Build Gate Check

- Decision: `{decision}`
- Local Build Gate Only: `True`
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
(OUT / "real-driverkit-dext-build-gate-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
