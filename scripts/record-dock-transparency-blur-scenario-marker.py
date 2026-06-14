#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.dock_transparency_blur_scenario_marker_report.v1"

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

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "returncode": p.returncode,
            "stdout": p.stdout[-10000:] if p.stdout else "",
            "stderr": p.stderr[-10000:] if p.stderr else "",
        }
    except Exception as exc:
        return {
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/dock-transparency-blur-scenario-marker")
    parser.add_argument("--i-understand-ui-scenario-marker", action="store_true")
    parser.add_argument("--scenario", choices=sorted(SCENARIOS))
    parser.add_argument("--event", choices=["start", "end", "note"], default="note")
    parser.add_argument("--note", default="")
    parser.add_argument("--session-id", default="")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "dock-transparency-blur-scenario-marker-report.json"

    hard_optin_ok = bool(args.i_understand_ui_scenario_marker and args.scenario)

    if not hard_optin_ok:
        report = {
            "schema": SCHEMA,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "decision": "REFUSE_SCENARIO_MARKER_HARDOPTIN_OR_SCENARIO_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "scenario": args.scenario,
            "event": args.event,
            "scenario_marker_event_recorded": False,
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
        }
        write_json(report_path, report)
        print("Decision: REFUSE_SCENARIO_MARKER_HARDOPTIN_OR_SCENARIO_NOT_SATISFIED")
        return 2

    session_id = args.session_id or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    mono = time.monotonic_ns()

    ps = run_cmd(["ps", "ax", "-o", "pid,comm"])
    reduce_transparency = run_cmd(["defaults", "read", "com.apple.universalaccess", "reduceTransparency"])

    event = {
        "session_id": session_id,
        "scenario": args.scenario,
        "event": args.event,
        "note": args.note,
        "timestamp_utc": now,
        "monotonic_ns": mono,
        "windowserver_process_observed": "WindowServer" in ps.get("stdout", ""),
        "dock_process_observed": "Dock" in ps.get("stdout", ""),
        "reduce_transparency_returncode": reduce_transparency.get("returncode"),
        "reduce_transparency_stdout_present": bool(reduce_transparency.get("stdout")),
        "rtx5070_acceleration_claim_valid": False,
        "rtx5070_ui_smoothness_claim_valid": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
    }

    events_path = out_dir / "scenario-events.json"
    events = load_events(events_path)
    events.append(event)
    write_json(events_path, events)

    same_session = [x for x in events if x.get("session_id") == session_id and x.get("scenario") == args.scenario]
    starts = [x for x in same_session if x.get("event") == "start"]
    ends = [x for x in same_session if x.get("event") == "end"]

    duration_seconds = None
    if starts and ends:
        start_ns = starts[-1].get("monotonic_ns")
        end_ns = ends[-1].get("monotonic_ns")
        if isinstance(start_ns, int) and isinstance(end_ns, int) and end_ns >= start_ns:
            duration_seconds = (end_ns - start_ns) / 1_000_000_000

    report = {
        "schema": SCHEMA,
        "generated_at_utc": now,
        "decision": "PASS_SCENARIO_MARKER_EVENT_RECORDED",
        "hard_optin_ok": True,
        "scenario_marker_event_recorded": True,
        "session_id": session_id,
        "scenario": args.scenario,
        "event": args.event,
        "event_count_total": len(events),
        "event_count_same_session": len(same_session),
        "start_count_same_session": len(starts),
        "end_count_same_session": len(ends),
        "duration_seconds_if_complete": duration_seconds,
        "windowserver_process_observed": event["windowserver_process_observed"],
        "dock_process_observed": event["dock_process_observed"],
        "reduce_transparency_returncode": event["reduce_transparency_returncode"],
        "reduce_transparency_stdout_present": event["reduce_transparency_stdout_present"],
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61_allowed_now": False,
        "xcodebuild_build_attempted_by_this_phase": False,
        "activation_submitted_by_this_phase": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "next_gate": "phase60x-scenario-marker-aggregation"
    }

    write_json(report_path, report)
    print("Decision: PASS_SCENARIO_MARKER_EVENT_RECORDED")
    print("session_id =", session_id)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
