#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.dock_transparency_blur_scenario_marker_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_json(path: Path):
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
        return obj if isinstance(obj, dict) else None

def read_json_list(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        return data if isinstance(data, list) else []
    except Exception:
        return []

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/dock-transparency-blur-scenario-marker/dock-transparency-blur-scenario-marker-report.json")
    parser.add_argument("--events", default="host-report-bundle/dock-transparency-blur-scenario-marker/scenario-events.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local = read_json(root / args.input)
    events = read_json_list(root / args.events)

    scenarios = sorted({str(e.get("scenario")) for e in events if e.get("scenario")})
    completed = 0
    durations = []
    for scenario in scenarios:
        by_session = {}
        for e in events:
            if e.get("scenario") != scenario:
                continue
            by_session.setdefault(e.get("session_id"), []).append(e)
        for session_id, items in by_session.items():
            starts = [x for x in items if x.get("event") == "start"]
            ends = [x for x in items if x.get("event") == "end"]
            if starts and ends:
                completed += 1
                s = starts[-1].get("monotonic_ns")
                e = ends[-1].get("monotonic_ns")
                if isinstance(s, int) and isinstance(e, int) and e >= s:
                    durations.append((e - s) / 1_000_000_000)

    private_raw_detected = has_private_text(json.dumps(local or {})) or has_private_text(json.dumps(events))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_DOCK_TRANSPARENCY_BLUR_SCENARIO_MARKER",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_marker_report_present": local is not None,
        "local_marker_decision": local.get("decision") if local else "NO_LOCAL_MARKER_REPORT_PRESENT",
        "scenario_marker_events_present": len(events) > 0,
        "scenario_marker_event_count": len(events),
        "scenario_count": len(scenarios),
        "completed_scenario_session_count": completed,
        "duration_seconds_count": len(durations),
        "duration_seconds_min": min(durations) if durations else None,
        "duration_seconds_max": max(durations) if durations else None,
        "duration_seconds_avg": sum(durations) / len(durations) if durations else None,
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
        "scenarios_observed": scenarios,
        "next_gate": "phase60x-scenario-marker-aggregation"
    }

    json_path = out_dir / "dock-transparency-blur-scenario-marker-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary.items() if k not in ["schema", "generated_at_utc", "scenarios_observed"])
    md = f"""# Dock Transparency Blur Scenario Marker Summary

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
- Next Gate: `phase60x-scenario-marker-aggregation`

## Summary

| Key | Value |
| --- | --- |
{rows}
"""
    (out_dir / "dock-transparency-blur-scenario-marker-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'dock-transparency-blur-scenario-marker-summary.md'}")
    print("Decision: PASS_DOCK_TRANSPARENCY_BLUR_SCENARIO_MARKER_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
