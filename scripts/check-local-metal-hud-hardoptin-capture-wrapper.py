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

manifest_path = ROOT / "tools/hackintosh/local-metal-hud-hardoptin-capture-wrapper.json"
doc_path = ROOT / "docs/hackintosh/local-metal-hud-hardoptin-capture-wrapper.md"
wrapper_path = ROOT / "scripts/local-metal-hud-hardoptin-capture-wrapper.py"
summary_json = OUT / "local-metal-hud-hardoptin-capture-summary.json"
summary_md = OUT / "local-metal-hud-hardoptin-capture-summary.md"
dryrun_manifest_path = ROOT / "tools/hackintosh/local-metal-hud-dryrun-launch-command-generator.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
dryrun_manifest = read_json(dryrun_manifest_path)
wrapper_text = wrapper_path.read_text(encoding="utf-8", errors="replace") if wrapper_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("wrapper_exists", wrapper_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("dryrun_manifest_exists", dryrun_manifest_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_metal_hud_hardoptin_capture_wrapper.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_metal_hud_hardoptin_capture_summary.v1"), "summary schema")
if dryrun_manifest:
    add(checks, "dryrun_manifest_schema_if_present", dryrun_manifest.get("schema") == "h1mekartx.local_metal_hud_dryrun_launch_command_generator.v1", "dryrun manifest schema")
else:
    add(checks, "dryrun_manifest_schema_if_present", True, "dryrun manifest absent; wrapper remains valid")

for field in [
    "local_metal_hud_hardoptin_capture_wrapper_ready",
    "hardoptin_capture_wrapper_only",
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "wrapper_executed_by_ci",
    "fallback_gpu_substitution_allowed",
    "env_values_committed",
    "private_paths_committed",
    "metal_hud_enabled_by_this_phase",
    "metal_workload_run_by_this_phase",
    "metal_workload_captured_by_this_phase",
    "metal_performance_report_generated_by_this_phase",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "current_windowserver_attribution_to_rtx5070_proven",
    "current_core_animation_attribution_to_rtx5070_proven",
    "current_quartzcore_attribution_to_rtx5070_proven",
    "current_metal_compositor_attribution_to_rtx5070_proven",
    "phase61d_allowed_now",
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

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("next_gate", "phase61d-sanitized-local-metal-hud-capture-summary-parser"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for token in [
    "--i-understand-local-metal-hud-capture",
    "--execute-capture",
    "--target-app",
    "--scenario",
    "--duration-seconds",
    "--output-under-host-report-bundle",
    "MTL_HUD_ENABLED",
    "MTL_HUD_LOG_ENABLED",
    "MTL_HUD_LOG_SHADER_ENABLED",
    "REFUSE_LOCAL_METAL_HUD_CAPTURE_HARDOPTIN_NOT_SATISFIED",
    "target_app_sanitized",
    "<TARGET_APP>",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "wrapper_contains_" + token.replace(" ", "_").replace("/", "_"), token in wrapper_text, token)

if summary:
    for field in [
        "local_capture_report_present",
        "local_capture_decision",
        "hard_optin_ok",
        "execute_capture_requested",
        "target_app_sanitized",
        "env_values_committed",
        "private_paths_committed",
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
        "next_gate",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

    add(checks, "summary_next_gate", summary.get("next_gate") == "phase61d-sanitized-local-metal-hud-capture-summary-parser", "next gate")
    add(checks, "summary_target_app_sanitized", summary.get("target_app_sanitized") == "<TARGET_APP>", "target app sanitized")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER_READY" if failed == 0 else "FAIL_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER"

report = {
    "schema": "h1mekartx.local_metal_hud_hardoptin_capture_wrapper_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "hardoptin_capture_wrapper_only": True,
    "wrapper_executed_by_ci": False,
    "metal_hud_enabled_by_this_phase": False,
    "metal_workload_run_by_this_phase": False,
    "metal_workload_captured_by_this_phase": False,
    "metal_performance_report_generated_by_this_phase": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "phase61d_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase61d-sanitized-local-metal-hud-capture-summary-parser",
    "checks": checks,
}

(OUT / "local-metal-hud-hardoptin-capture-wrapper-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Metal HUD Hard-Opt-In Capture Wrapper Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Hard-Opt-In Capture Wrapper Only: `True`
- Wrapper Executed By CI: `False`
- Metal HUD Enabled By This Phase: `False`
- Metal Workload Run By This Phase: `False`
- Metal Workload Captured By This Phase: `False`
- Metal Performance Report Generated By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61D Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase61d-sanitized-local-metal-hud-capture-summary-parser`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "local-metal-hud-hardoptin-capture-wrapper-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
