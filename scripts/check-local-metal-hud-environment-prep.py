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

manifest_path = ROOT / "tools/hackintosh/local-metal-hud-environment-capture-prep.json"
doc_path = ROOT / "docs/hackintosh/local-metal-hud-environment-capture-prep.md"
collector_path = ROOT / "scripts/collect-local-metal-hud-environment-prep.py"
summary_json = OUT / "local-metal-hud-environment-prep-summary.json"
summary_md = OUT / "local-metal-hud-environment-prep-summary.md"
capture_manifest_path = ROOT / "tools/hackintosh/local-metal-hud-capture-manifest.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
capture_manifest = read_json(capture_manifest_path)
collector_text = collector_path.read_text(encoding="utf-8", errors="replace") if collector_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("collector_exists", collector_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("capture_manifest_exists", capture_manifest_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_metal_hud_environment_capture_prep.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_metal_hud_environment_prep_summary.v1"), "summary schema")
if capture_manifest:
    add(checks, "capture_manifest_schema_if_present", capture_manifest.get("schema") == "h1mekartx.local_metal_hud_capture_manifest.v1", "capture manifest schema")
else:
    add(checks, "capture_manifest_schema_if_present", True, "capture manifest absent; prep remains valid")

for field in [
    "local_metal_hud_environment_capture_prep_ready",
    "environment_prep_only",
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "env_values_committed",
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
    "phase61b_allowed_now",
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
    ("next_gate", "phase61b-local-metal-hud-dryrun-launch-command-generator"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for token in [
    "xcodebuild",
    "xcode-select",
    "xcrun",
    "xctrace",
    "metal",
    "metallib",
    "MTL_",
    "METAL_",
    "hud_env_keys_present",
    "env_values_committed",
    "metal_hud_enabled_by_this_phase",
    "metal_workload_run_by_this_phase",
    "metal_performance_report_generated_by_this_phase",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "collector_contains_" + token.replace(" ", "_").replace("/", "_"), token in collector_text, token)

if summary:
    for field in [
        "local_environment_report_present",
        "xcodebuild_available",
        "xcode_select_available",
        "xcrun_available",
        "xctrace_available",
        "metal_tool_available",
        "metallib_tool_available",
        "macosx_sdk_available",
        "hud_env_key_count",
        "env_values_committed",
        "manifest_summary_present",
        "scenario_summary_present",
        "next_gate",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

    add(checks, "summary_next_gate", summary.get("next_gate") == "phase61b-local-metal-hud-dryrun-launch-command-generator", "next gate")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_METAL_HUD_ENVIRONMENT_PREP_READY" if failed == 0 else "FAIL_LOCAL_METAL_HUD_ENVIRONMENT_PREP"

report = {
    "schema": "h1mekartx.local_metal_hud_environment_prep_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "environment_prep_only": True,
    "metal_hud_enabled_by_this_phase": False,
    "metal_workload_run_by_this_phase": False,
    "metal_workload_captured_by_this_phase": False,
    "metal_performance_report_generated_by_this_phase": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "phase61b_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase61b-local-metal-hud-dryrun-launch-command-generator",
    "checks": checks,
}

(OUT / "local-metal-hud-environment-prep-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Local Metal HUD Environment Prep Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Environment Prep Only: `True`
- Metal HUD Enabled By This Phase: `False`
- Metal Workload Run By This Phase: `False`
- Metal Workload Captured By This Phase: `False`
- Metal Performance Report Generated By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61B Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase61b-local-metal-hud-dryrun-launch-command-generator`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "local-metal-hud-environment-prep-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
