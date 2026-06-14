#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_metal_hud_capture_manifest_local.v1"

SCENARIOS = [
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
]

METRICS = [
    "fps_avg",
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
    "scenario_marker_duration_seconds",
    "before_after_delta",
]

ATTRIBUTION_FIELDS = [
    "scenario_marker_timing",
    "metal_hud_report_timing",
    "windowserver_attribution",
    "core_animation_attribution",
    "quartzcore_attribution",
    "metal_compositor_attribution",
    "rtx5070_attribution",
    "fallback_gpu_attribution",
    "spoofed_metal_support_false",
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/local-metal-hud-capture-manifest")
    parser.add_argument("--scenario-summary", default="release-readiness/scenario-marker-aggregation-summary.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    scenario_summary_path = root / args.scenario_summary
    scenario_summary = read_json(scenario_summary_path)

    observed_scenario_count = scenario_summary.get("observed_scenario_count", 0) if scenario_summary else 0
    completed_scenario_session_count = scenario_summary.get("completed_scenario_session_count", 0) if scenario_summary else 0
    scenario_marker_event_count = scenario_summary.get("scenario_marker_event_count", 0) if scenario_summary else 0

    capture_manifest = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_LOCAL_METAL_HUD_CAPTURE_MANIFEST_CREATED",
        "classification": "CLASSIFICATION_LOCAL_METAL_HUD_CAPTURE_MANIFEST",
        "host_report_bundle_local_only": True,
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "capture_manifest_only": True,
        "scenario_summary_present": scenario_summary is not None,
        "scenario_marker_event_count": scenario_marker_event_count,
        "observed_scenario_count": observed_scenario_count,
        "completed_scenario_session_count": completed_scenario_session_count,
        "required_scenarios": SCENARIOS,
        "required_metrics": METRICS,
        "required_attribution_fields": ATTRIBUTION_FIELDS,
        "future_raw_hud_report_dir": str(out_dir / "raw-metal-hud-reports"),
        "future_sanitized_summary_path": "release-readiness/local-metal-hud-capture-summary.json",
        "metal_hud_enabled_by_this_phase": False,
        "metal_workload_run_by_this_phase": False,
        "metal_workload_captured_by_this_phase": False,
        "metal_performance_report_generated_by_this_phase": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61_allowed_now": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "next_gate": "phase61a-local-metal-hud-environment-capture-prep",
    }

    write_json(out_dir / "local-metal-hud-capture-manifest.json", capture_manifest)
    print("Decision: PASS_LOCAL_METAL_HUD_CAPTURE_MANIFEST_CREATED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
