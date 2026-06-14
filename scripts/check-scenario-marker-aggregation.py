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

manifest_path = ROOT / "tools/hackintosh/scenario-marker-aggregation.json"
doc_path = ROOT / "docs/hackintosh/scenario-marker-aggregation.md"
aggregator_path = ROOT / "scripts/aggregate-scenario-marker-events.py"
summary_json = OUT / "scenario-marker-aggregation-summary.json"
summary_md = OUT / "scenario-marker-aggregation-summary.md"
phase60w_manifest_path = ROOT / "tools/hackintosh/dock-transparency-blur-scenario-marker.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
phase60w_manifest = read_json(phase60w_manifest_path)
aggregator_text = aggregator_path.read_text(encoding="utf-8", errors="replace") if aggregator_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("aggregator_exists", aggregator_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("phase60w_manifest_exists", phase60w_manifest_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.scenario_marker_aggregation.v1"), "manifest schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.scenario_marker_aggregation_summary.v1"), "summary schema")
if phase60w_manifest:
    add(checks, "phase60w_schema_if_present", phase60w_manifest.get("schema") == "h1mekartx.dock_transparency_blur_scenario_marker.v1", "phase60w schema")
else:
    add(checks, "phase60w_schema_if_present", True, "phase60w absent; aggregation remains valid")

for field in [
    "scenario_marker_aggregation_ready",
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

for token in [
    "scenario-events.json",
    "dock_magnification",
    "dock_hide_show",
    "menu_bar_transparency",
    "window_transparency",
    "mission_control",
    "launchpad",
    "stage_manager",
    "duration_seconds_avg",
    "rtx5070_target_retained",
    "fallback_gpu_substitution_allowed",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "gpu_command_submission_attempted",
]:
    add(checks, "aggregator_contains_" + token.replace(" ", "_").replace("/", "_"), token in aggregator_text, token)

if summary:
    for field in [
        "scenario_marker_events_present",
        "scenario_marker_event_count",
        "supported_scenario_count",
        "observed_scenario_count",
        "completed_scenario_session_count",
        "duration_seconds_count",
        "duration_seconds_min",
        "duration_seconds_max",
        "duration_seconds_avg",
        "per_scenario",
        "next_gate",
    ]:
        add(checks, f"summary_{field}_recorded", field in summary, field)

    add(checks, "summary_next_gate", summary.get("next_gate") == "phase60y-metal-hud-frame-pacing-capture-plan", "next gate")
    add(checks, "summary_per_scenario_dict", isinstance(summary.get("per_scenario"), dict), "per_scenario dict")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_SCENARIO_MARKER_AGGREGATION_READY" if failed == 0 else "FAIL_SCENARIO_MARKER_AGGREGATION"

report = {
    "schema": "h1mekartx.scenario_marker_aggregation_check.v1",
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
    "next_gate": "phase60y-metal-hud-frame-pacing-capture-plan",
    "checks": checks,
}

(OUT / "scenario-marker-aggregation-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Scenario Marker Aggregation Check

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
- Next Gate: `phase60y-metal-hud-frame-pacing-capture-plan`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "scenario-marker-aggregation-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
