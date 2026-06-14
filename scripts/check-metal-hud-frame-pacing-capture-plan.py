#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/metal-hud-frame-pacing-capture-plan.json"
doc_path = ROOT / "docs/hackintosh/metal-hud-frame-pacing-capture-plan.md"
aggregation_path = ROOT / "tools/hackintosh/scenario-marker-aggregation.json"
matrix_path = ROOT / "tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json"

manifest = read_json(manifest_path)
aggregation = read_json(aggregation_path)
matrix = read_json(matrix_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("aggregation_manifest_exists", aggregation_path),
    ("matrix_manifest_exists", matrix_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.metal_hud_frame_pacing_capture_plan.v1"), "manifest schema")

if aggregation:
    add(checks, "aggregation_schema_if_present", aggregation.get("schema") == "h1mekartx.scenario_marker_aggregation.v1", "aggregation schema")
else:
    add(checks, "aggregation_schema_if_present", True, "aggregation absent; capture plan remains valid")

if matrix:
    add(checks, "matrix_schema_if_present", matrix.get("schema") == "h1mekartx.rtx5070_ui_smoothness_evidence_matrix.v1", "matrix schema")
else:
    add(checks, "matrix_schema_if_present", True, "matrix absent; capture plan remains valid")

for field in [
    "metal_hud_frame_pacing_capture_plan_ready",
    "rtx5070_target_retained",
    "dock_transparency_blur_scope_retained",
    "capture_plan_only",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "metal_hud_enabled_by_this_phase",
    "metal_workload_run_by_this_phase",
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

for key, value in [
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("next_gate", "phase60z-local-metal-hud-capture-manifest"),
]:
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

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
    add(checks, f"scenario_{scenario}", bool(manifest and scenario in manifest.get("required_scenarios", [])), scenario)

for metric in [
    "gpu_time_avg",
    "cpu_time_avg",
    "frame_time_avg",
    "frame_time_min",
    "frame_time_max",
    "frame_time_p50",
    "frame_time_p95",
    "frame_time_p99",
    "present_delay_avg",
    "dropped_frame_count",
    "hitch_count",
    "encoder_count",
    "shader_compilation_event_count",
    "before_after_delta",
    "scenario_marker_duration_seconds",
]:
    add(checks, f"metric_{metric}", bool(manifest and metric in manifest.get("required_metrics", [])), metric)

for attribution in [
    "scenario_marker_timing",
    "metal_hud_frame_pacing_timing",
    "windowserver_attribution",
    "core_animation_attribution",
    "quartzcore_attribution",
    "metal_compositor_attribution",
    "rtx5070_attribution",
    "fallback_gpu_attribution",
]:
    add(checks, f"attribution_{attribution}", bool(manifest and attribution in manifest.get("required_attribution_fields", [])), attribution)

for token in [
    "Metal HUD / Frame Pacing Capture Plan",
    "The target remains RTX 5070 only",
    "Fallback GPU substitution is not accepted as RTX 5070 proof",
    "This phase does not enable Metal HUD",
    "This phase does not run a Metal workload",
    "gpu_time_avg",
    "frame_time_p95",
    "present_delay_avg",
    "shader_compilation_event_count",
    "WindowServer attribution",
    "Core Animation attribution",
    "QuartzCore attribution",
    "Metal compositor attribution",
    "RTX 5070 attribution",
    "provider open remains blocked",
    "BAR mapping remains blocked",
    "GPU command submission remains blocked",
    "Metal proof remains blocked",
    "Dock/transparency/blur proof remains blocked",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_").replace("/", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_METAL_HUD_FRAME_PACING_CAPTURE_PLAN_READY" if failed == 0 else "FAIL_METAL_HUD_FRAME_PACING_CAPTURE_PLAN"

report = {
    "schema": "h1mekartx.metal_hud_frame_pacing_capture_plan_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "capture_plan_only": True,
    "metal_hud_enabled_by_this_phase": False,
    "metal_workload_run_by_this_phase": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "phase61_allowed_now": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase60z-local-metal-hud-capture-manifest",
    "checks": checks,
}

(OUT / "metal-hud-frame-pacing-capture-plan-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Metal HUD / Frame Pacing Capture Plan Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Capture Plan Only: `True`
- Metal HUD Enabled By This Phase: `False`
- Metal Workload Run By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60z-local-metal-hud-capture-manifest`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "metal-hud-frame-pacing-capture-plan-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
