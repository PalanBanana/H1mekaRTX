#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_metal_hud_dryrun_launch_command_report.v1"

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
    parser.add_argument("--out-dir", default="host-report-bundle/local-metal-hud-dryrun-launch-command")
    parser.add_argument("--environment-summary", default="release-readiness/local-metal-hud-environment-prep-summary.json")
    parser.add_argument("--capture-summary", default="release-readiness/local-metal-hud-capture-manifest-summary.json")
    parser.add_argument("--scenario-summary", default="release-readiness/scenario-marker-aggregation-summary.json")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    environment_summary = read_json(root / args.environment_summary)
    capture_summary = read_json(root / args.capture_summary)
    scenario_summary = read_json(root / args.scenario_summary)

    xcrun_available = bool(environment_summary and environment_summary.get("xcrun_available"))
    xctrace_available = bool(environment_summary and environment_summary.get("xctrace_available"))
    metal_tool_available = bool(environment_summary and environment_summary.get("metal_tool_available"))
    metallib_tool_available = bool(environment_summary and environment_summary.get("metallib_tool_available"))

    command_templates = [
        {
            "name": "metal_hud_overlay_launch_template",
            "kind": "environment_launch_template",
            "executed": False,
            "template": "MTL_HUD_ENABLED=1 <TARGET_APP>",
            "placeholders": ["<TARGET_APP>"],
            "purpose": "future HUD overlay launch only",
        },
        {
            "name": "metal_hud_overlay_logging_launch_template",
            "kind": "environment_launch_template",
            "executed": False,
            "template": "MTL_HUD_ENABLED=1 MTL_HUD_LOG_ENABLED=1 MTL_HUD_LOG_FILE=<OUTPUT_DIR>/<SCENARIO>.metal-hud.log <TARGET_APP>",
            "placeholders": ["<TARGET_APP>", "<OUTPUT_DIR>", "<SCENARIO>"],
            "purpose": "future HUD overlay plus local log capture only",
        },
        {
            "name": "xctrace_game_performance_dryrun_template",
            "kind": "xctrace_template",
            "executed": False,
            "template": "xcrun xctrace record --template 'Game Performance' --time-limit <DURATION_SECONDS>s --output <OUTPUT_DIR>/<SCENARIO>.trace --launch <TARGET_APP>",
            "placeholders": ["<TARGET_APP>", "<OUTPUT_DIR>", "<SCENARIO>", "<DURATION_SECONDS>"],
            "purpose": "future Instruments trace capture only",
        },
        {
            "name": "xctrace_metal_system_trace_dryrun_template",
            "kind": "xctrace_template",
            "executed": False,
            "template": "xcrun xctrace record --template 'Metal System Trace' --time-limit <DURATION_SECONDS>s --output <OUTPUT_DIR>/<SCENARIO>-metal.trace --launch <TARGET_APP>",
            "placeholders": ["<TARGET_APP>", "<OUTPUT_DIR>", "<SCENARIO>", "<DURATION_SECONDS>"],
            "purpose": "future Metal System Trace capture only",
        },
    ]

    per_scenario_plan = []
    for scenario in SCENARIOS:
        per_scenario_plan.append({
            "scenario": scenario,
            "start_marker_template": f"python3 scripts/record-dock-transparency-blur-scenario-marker.py --root . --i-understand-ui-scenario-marker --scenario {scenario} --event start --session-id <SESSION_ID>",
            "end_marker_template": f"python3 scripts/record-dock-transparency-blur-scenario-marker.py --root . --i-understand-ui-scenario-marker --scenario {scenario} --event end --session-id <SESSION_ID>",
            "hud_template_names": [x["name"] for x in command_templates],
            "executed": False,
        })

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_LOCAL_METAL_HUD_DRYRUN_LAUNCH_COMMANDS_GENERATED",
        "classification": "CLASSIFICATION_LOCAL_METAL_HUD_DRYRUN_LAUNCH_COMMAND_GENERATOR",
        "host_report_bundle_local_only": True,
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "dryrun_command_template_only": True,
        "environment_summary_present": environment_summary is not None,
        "capture_summary_present": capture_summary is not None,
        "scenario_summary_present": scenario_summary is not None,
        "xcrun_available": xcrun_available,
        "xctrace_available": xctrace_available,
        "metal_tool_available": metal_tool_available,
        "metallib_tool_available": metallib_tool_available,
        "command_template_count": len(command_templates),
        "scenario_plan_count": len(per_scenario_plan),
        "command_templates": command_templates,
        "per_scenario_plan": per_scenario_plan,
        "generated_commands_executed_by_this_phase": False,
        "env_values_committed": False,
        "private_paths_committed": False,
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
        "phase61c_allowed_now": False,
        "xcodebuild_build_attempted_by_this_phase": False,
        "activation_submitted_by_this_phase": False,
        "deactivation_submitted_by_this_phase": False,
        "install_attempted": False,
        "manual_dext_load_attempted": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "next_gate": "phase61c-local-metal-hud-hardoptin-capture-wrapper",
    }

    write_json(out_dir / "local-metal-hud-dryrun-launch-command-report.json", report)
    print("Decision: PASS_LOCAL_METAL_HUD_DRYRUN_LAUNCH_COMMANDS_GENERATED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
