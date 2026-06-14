#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.scenario_marker_aggregation_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

SUPPORTED_SCENARIOS = [
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

def read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

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

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def duration_stats(values: list[float]) -> dict:
    values = [v for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
    if not values:
        return {
            "duration_seconds_count": 0,
            "duration_seconds_min": None,
            "duration_seconds_max": None,
            "duration_seconds_avg": None,
        }
    return {
        "duration_seconds_count": len(values),
        "duration_seconds_min": min(values),
        "duration_seconds_max": max(values),
        "duration_seconds_avg": sum(values) / len(values),
    }

def pair_durations(events: list[dict]) -> list[float]:
    by_session: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        sid = str(e.get("session_id") or "")
        if sid:
            by_session[sid].append(e)

    durations = []
    for sid, items in by_session.items():
        starts = [x for x in items if x.get("event") == "start"]
        ends = [x for x in items if x.get("event") == "end"]
        if not starts or not ends:
            continue
        start_ns = starts[-1].get("monotonic_ns")
        end_ns = ends[-1].get("monotonic_ns")
        if isinstance(start_ns, int) and isinstance(end_ns, int) and end_ns >= start_ns:
            durations.append((end_ns - start_ns) / 1_000_000_000)
    return durations

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--events", default="host-report-bundle/dock-transparency-blur-scenario-marker/scenario-events.json")
    parser.add_argument("--marker-report", default="host-report-bundle/dock-transparency-blur-scenario-marker/dock-transparency-blur-scenario-marker-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    events_path = root / args.events
    report_path = root / args.marker_report

    events = read_json_list(events_path)
    last_report = read_json(report_path)

    scenario_map: dict[str, list[dict]] = defaultdict(list)
    for e in events:
        scenario = str(e.get("scenario") or "")
        if scenario:
            scenario_map[scenario].append(e)

    per_scenario = {}
    all_durations = []
    completed_total = 0

    for scenario in SUPPORTED_SCENARIOS:
        items = scenario_map.get(scenario, [])
        starts = [x for x in items if x.get("event") == "start"]
        ends = [x for x in items if x.get("event") == "end"]
        notes = [x for x in items if x.get("event") == "note"]
        durations = pair_durations(items)
        all_durations.extend(durations)
        completed = len(durations)
        completed_total += completed

        per_scenario[scenario] = {
            "event_count": len(items),
            "start_count": len(starts),
            "end_count": len(ends),
            "note_count": len(notes),
            "completed_session_count": completed,
            **duration_stats(durations),
            "windowserver_observed_any": any(bool(x.get("windowserver_process_observed")) for x in items),
            "dock_observed_any": any(bool(x.get("dock_process_observed")) for x in items),
            "reduce_transparency_returncode_observed_any": any(x.get("reduce_transparency_returncode") is not None for x in items),
        }

    private_raw_detected = has_private_text(json.dumps(events)) or has_private_text(json.dumps(last_report or {}))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_SCENARIO_MARKER_AGGREGATION",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "events_file_present": events_path.exists(),
        "last_marker_report_present": last_report is not None,
        "scenario_marker_events_present": len(events) > 0,
        "scenario_marker_event_count": len(events),
        "supported_scenario_count": len(SUPPORTED_SCENARIOS),
        "observed_scenario_count": len([s for s, items in scenario_map.items() if items]),
        "completed_scenario_session_count": completed_total,
        **duration_stats(all_durations),
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "current_windowserver_attribution_to_rtx5070_proven": False,
        "current_core_animation_attribution_to_rtx5070_proven": False,
        "current_quartzcore_attribution_to_rtx5070_proven": False,
        "current_metal_compositor_attribution_to_rtx5070_proven": False,
        "phase61_allowed_now": False,
        "provider_open_allowed_now": False,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
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
        "per_scenario": per_scenario,
        "next_gate": "phase60y-metal-hud-frame-pacing-capture-plan",
    }

    json_path = out_dir / "scenario-marker-aggregation-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{scenario}` | `{data['event_count']}` | `{data['completed_session_count']}` | `{data['duration_seconds_avg']}` |"
        for scenario, data in per_scenario.items()
    )

    md = f"""# Scenario Marker Aggregation Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Scenario Marker Event Count: `{summary['scenario_marker_event_count']}`
- Observed Scenario Count: `{summary['observed_scenario_count']}`
- Completed Scenario Session Count: `{summary['completed_scenario_session_count']}`
- Duration Seconds Count: `{summary['duration_seconds_count']}`
- Duration Seconds Avg: `{summary['duration_seconds_avg']}`
- Next Gate: `phase60y-metal-hud-frame-pacing-capture-plan`

## Per Scenario

| Scenario | Event Count | Completed Sessions | Avg Duration Seconds |
| --- | ---: | ---: | ---: |
{rows}
"""
    (out_dir / "scenario-marker-aggregation-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'scenario-marker-aggregation-summary.md'}")
    print("Decision: PASS_SCENARIO_MARKER_AGGREGATION_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
