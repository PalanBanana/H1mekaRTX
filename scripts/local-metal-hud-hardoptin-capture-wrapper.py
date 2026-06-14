#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_metal_hud_hardoptin_capture_report.v1"

SCENARIOS = {
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
}

def safe_relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return "<OUTSIDE_REPO_OR_PRIVATE_PATH>"

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER",
        "host_report_bundle_local_only": True,
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "hardoptin_capture_wrapper_only": False,
        "env_values_committed": False,
        "private_paths_committed": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61d_allowed_now": False,
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
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/local-metal-hud-hardoptin-capture")
    parser.add_argument("--i-understand-local-metal-hud-capture", action="store_true")
    parser.add_argument("--execute-capture", action="store_true")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--target-app", default="")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS))
    parser.add_argument("--duration-seconds", type=int, default=0)
    parser.add_argument("--session-id", default="")
    parser.add_argument("--enable-shader-log", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "local-metal-hud-hardoptin-capture-report.json"

    target_app = Path(args.target_app).expanduser() if args.target_app else None
    target_app_exists = bool(target_app and target_app.exists())

    hard_optin_ok = bool(
        args.i_understand_local_metal_hud_capture
        and args.execute_capture
        and args.output_under_host_report_bundle
        and args.scenario
        and args.duration_seconds > 0
        and target_app_exists
    )

    if not hard_optin_ok:
        report = {
            **base_report(),
            "decision": "REFUSE_LOCAL_METAL_HUD_CAPTURE_HARDOPTIN_NOT_SATISFIED",
            "hard_optin_ok": False,
            "execute_capture_requested": bool(args.execute_capture),
            "output_under_host_report_bundle": bool(args.output_under_host_report_bundle),
            "target_app_supplied": bool(args.target_app),
            "target_app_exists": target_app_exists,
            "scenario_supplied": bool(args.scenario),
            "duration_seconds": args.duration_seconds,
            "metal_hud_enabled_by_this_run": False,
            "metal_workload_run_by_this_run": False,
            "metal_workload_captured_by_this_run": False,
            "metal_performance_report_generated_by_this_run": False,
            "next_gate": "phase61d-sanitized-local-metal-hud-capture-summary-parser",
        }
        write_json(report_path, report)
        print("Decision: REFUSE_LOCAL_METAL_HUD_CAPTURE_HARDOPTIN_NOT_SATISFIED")
        return 2

    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    session_id = args.session_id or f"{args.scenario}-{int(time.time())}"
    hud_log_path = raw_dir / f"{session_id}.metal-hud.log"
    stdout_path = raw_dir / f"{session_id}.stdout.txt"
    stderr_path = raw_dir / f"{session_id}.stderr.txt"

    env = os.environ.copy()
    env["MTL_HUD_ENABLED"] = "1"
    env["MTL_HUD_LOG_ENABLED"] = "1"
    if args.enable_shader_log:
        env["MTL_HUD_LOG_SHADER_ENABLED"] = "1"

    start_time = datetime.now(timezone.utc).isoformat()
    monotonic_start = time.monotonic_ns()

    # Use open for app bundles; use direct execution for non-bundle executable paths.
    cmd: list[str]
    if str(target_app).endswith(".app"):
        cmd = ["open", "-n", str(target_app)]
    else:
        cmd = [str(target_app)]

    # This wrapper intentionally launches only a user-supplied target under hard opt-in.
    # It does not open a DriverKit provider, map BARs, or submit GPU commands directly.
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    time.sleep(max(1, args.duration_seconds))

    # Do not forcibly kill existing GUI app if launched via open; open returns quickly.
    stdout, stderr = "", ""
    try:
        stdout, stderr = proc.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate(timeout=5)

    stdout_path.write_text(stdout[-20000:] if stdout else "", encoding="utf-8")
    stderr_path.write_text(stderr[-20000:] if stderr else "", encoding="utf-8")

    end_time = datetime.now(timezone.utc).isoformat()
    monotonic_end = time.monotonic_ns()
    duration_observed_seconds = (monotonic_end - monotonic_start) / 1_000_000_000

    report = {
        **base_report(),
        "decision": "PASS_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER_RAN",
        "hard_optin_ok": True,
        "execute_capture_requested": True,
        "output_under_host_report_bundle": True,
        "session_id": session_id,
        "scenario": args.scenario,
        "duration_seconds_requested": args.duration_seconds,
        "duration_seconds_observed": duration_observed_seconds,
        "target_app_supplied": True,
        "target_app_exists": True,
        "target_app_sanitized": "<TARGET_APP>",
        "target_app_local_only_rel_hint": safe_relpath(target_app, root),
        "command_kind": "open_app_bundle" if str(target_app).endswith(".app") else "direct_executable",
        "start_time_utc": start_time,
        "end_time_utc": end_time,
        "process_returncode": proc.returncode,
        "hud_env_keys_enabled": ["MTL_HUD_ENABLED", "MTL_HUD_LOG_ENABLED"] + (["MTL_HUD_LOG_SHADER_ENABLED"] if args.enable_shader_log else []),
        "env_values_committed": False,
        "raw_stdout_local_only": safe_relpath(stdout_path, root),
        "raw_stderr_local_only": safe_relpath(stderr_path, root),
        "raw_hud_log_expected_local_only": safe_relpath(hud_log_path, root),
        "metal_hud_enabled_by_this_run": True,
        "metal_workload_run_by_this_run": True,
        "metal_workload_captured_by_this_run": False,
        "metal_performance_report_generated_by_this_run": False,
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
    }

    write_json(report_path, report)
    print("Decision: PASS_LOCAL_METAL_HUD_HARDOPTIN_CAPTURE_WRAPPER_RAN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
