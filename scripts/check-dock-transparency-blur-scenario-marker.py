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

manifest_path = ROOT / "tools/hackintosh/dock-transparency-blur-scenario-marker.json"
doc_path = ROOT / "docs/hackintosh/dock-transparency-blur-scenario-marker.md"
marker_path = ROOT / "scripts/record-dock-transparency-blur-scenario-marker.py"
summary_json = OUT / "dock-transparency-blur-scenario-marker-summary.json"
summary_md = OUT / "dock-transparency-blur-scenario-marker-summary.md"
baseline_path = ROOT / "tools/hackintosh/local-readonly-rtx5070-ui-baseline-collector.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
baseline = read_json(baseline_path)
marker_text = marker_path.read_text(encoding="utf-8", errors="replace") if marker_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("marker_exists", marker_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("baseline_manifest_exists", baseline_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.dock_transparency_blur_scenario_marker.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.dock_transparency_blur_scenario_marker_summary.v1"), "summary schema")
if baseline:
    add(checks, "baseline_schema_if_present", baseline.get("schema") == "h1mekartx.local_readonly_rtx5070_ui_baseline_collector.v1", "baseline schema")
else:
    add(checks, "baseline_schema_if_present", True, "baseline absent; scenario marker remains valid")

for field in [
    "scenario_marker_ready",
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "current_windowserver_attribution_to_rtx5070_proven",
    "current_core_animation_attribution_to_rtx5070_proven",
    "current_quartzcore_attribution_to_rtx5070_proven",
    "current_metal_compositor_attribution_to_rtx5070_proven",
    "phase61_allowed_now",
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

for scenario in [
    "dock_magnification",
    "dock_hide_show",
    "dock_launch_animation",
    "menu_bar_transparency",
    "window_transparency",
    "sheet_blur",
    "sidebar_blur",
    "window_movement",
    "window_resize",
    "mission_control",
    "launchpad",
    "stage_manager",
    "desktop_space_switching",
]:
    add(checks, f"manifest_scenario_{scenario}", bool(manifest and scenario in manifest.get("supported_scenarios", [])), scenario)
    add(checks, f"marker_contains_{scenario}", scenario in marker_text, scenario)

for token in [
    "--i-understand-ui-scenario-marker",
    "--scenario",
    "--event",
    "start",
    "end",
    "WindowServer",
    "Dock",
    "reduceTransparency",
    "rtx5070_acceleration_claim_valid",
    "rtx5070_ui_smoothness_claim_valid",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "marker_contains_" + token.replace(" ", "_").replace("/", "_").replace("-", "_"), token in marker_text, token)

if summary:
    for field in [
        "scenario_marker_events_present",
        "scenario_marker_event_count",
        "scenario_count",
        "completed_scenario_session_count",
        "duration_seconds_count",
        "rtx5070_target_retained",
        "raw_stdout_not_committed",
        "raw_stderr_not_committed",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_DOCK_TRANSPARENCY_BLUR_SCENARIO_MARKER_READY" if failed == 0 else "FAIL_DOCK_TRANSPARENCY_BLUR_SCENARIO_MARKER"

report = {
    "schema": "h1mekartx.dock_transparency_blur_scenario_marker_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "phase61_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase60x-scenario-marker-aggregation",
    "checks": checks,
}

(OUT / "dock-transparency-blur-scenario-marker-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Dock Transparency Blur Scenario Marker Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60x-scenario-marker-aggregation`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "dock-transparency-blur-scenario-marker-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
