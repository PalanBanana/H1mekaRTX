#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_ui_baseline_artifact_summary.v1"

COMMAND_KEYS = [
    "sw_vers",
    "uname",
    "system_profiler_displays_json",
    "system_profiler_hardware_json",
    "ioreg_display_connect",
    "ioreg_framebuffer",
    "process_table",
    "windowserver_recent_log",
    "dock_recent_log",
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def command_summary(commands: dict) -> dict:
    out = {}
    for key in COMMAND_KEYS:
        item = commands.get(key, {})
        out[key] = {
            "present": key in commands,
            "available": bool(item.get("available")) if key in commands else False,
            "returncode": item.get("returncode") if key in commands else None,
            "stdout_present": bool(item.get("stdout")) if key in commands else False,
            "stderr_present": bool(item.get("stderr")) if key in commands else False,
        }
    return out

def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize local read-only UI baseline artifact.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--baseline", default="host-report-bundle/ui-baseline/local-readonly-ui-baseline.json", help="Local baseline JSON")
    parser.add_argument("--out-dir", default="release-readiness", help="Committed output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    baseline_path = (root / args.baseline).resolve() if not Path(args.baseline).is_absolute() else Path(args.baseline).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline = read_json(baseline_path)

    process_visibility = baseline.get("process_visibility", {}) if baseline else {}
    parsed = baseline.get("parsed_system_profiler", {}) if baseline else {}
    commands = baseline.get("commands", {}) if baseline else {}

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER",
        "secondary_classification": "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "local_ui_baseline_artifact_summarizer_only": True,
        "local_baseline_summary_only": True,
        "host_report_bundle_local_only": True,
        "raw_local_logs_not_committed": True,
        "raw_command_stdout_not_committed": True,
        "raw_command_stderr_not_committed": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "mission_control_acceleration_not_claimed": True,
        "launchpad_acceleration_not_claimed": True,
        "stage_manager_acceleration_not_claimed": True,
        "windowserver_attribution_proof_not_claimed": True,
        "core_animation_attribution_proof_not_claimed": True,
        "quartzcore_attribution_proof_not_claimed": True,
        "metal_compositor_attribution_proof_not_claimed": True,
        "local_ui_baseline_artifact_summary_state": "SUMMARY_ONLY",
        "local_readonly_ui_baseline_state": "COLLECTED_OR_UNAVAILABLE" if baseline else "UNAVAILABLE",
        "baseline_artifact_present": baseline is not None,
        "baseline_schema_valid": bool(baseline and baseline.get("schema") == "h1mekartx.local_readonly_ui_baseline_report.v1"),
        "baseline_generated_at_utc_present": bool(baseline and baseline.get("generated_at_utc")),
        "windowserver_visibility_recorded": "WindowServer" in process_visibility,
        "dock_visibility_recorded": "Dock" in process_visibility,
        "windowserver_visible": bool(process_visibility.get("WindowServer", {}).get("visible")),
        "dock_visible": bool(process_visibility.get("Dock", {}).get("visible")),
        "windowserver_matching_line_count": int(process_visibility.get("WindowServer", {}).get("matching_line_count", 0)) if "WindowServer" in process_visibility else 0,
        "dock_matching_line_count": int(process_visibility.get("Dock", {}).get("matching_line_count", 0)) if "Dock" in process_visibility else 0,
        "displays_json_parse_ok": bool(parsed.get("displays_json_parse_ok")),
        "hardware_json_parse_ok": bool(parsed.get("hardware_json_parse_ok")),
        "command_summary": command_summary(commands),
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "core_animation_attribution_proof_state": "NOT_ATTEMPTED",
        "quartzcore_attribution_proof_state": "NOT_ATTEMPTED",
        "metal_compositor_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
        "rtx5070_workload_attribution_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
    }

    json_path = out_dir / "local-ui-baseline-artifact-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{key}` | `{val['present']}` | `{val['available']}` | `{val['returncode']}` | `{val['stdout_present']}` | `{val['stderr_present']}` |"
        for key, val in summary["command_summary"].items()
    )

    md = f"""# Local UI Baseline Artifact Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Classification: `{summary['classification']}`
- Local Baseline Summary Only: `{summary['local_baseline_summary_only']}`
- Host Report Bundle Local Only: `{summary['host_report_bundle_local_only']}`
- Raw Local Logs Not Committed: `{summary['raw_local_logs_not_committed']}`
- Raw Command Stdout Not Committed: `{summary['raw_command_stdout_not_committed']}`
- Raw Command Stderr Not Committed: `{summary['raw_command_stderr_not_committed']}`
- Measurement Not Acceleration Proof: `{summary['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{summary['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{summary['metal_proof_not_claimed']}`
- Baseline Artifact Present: `{summary['baseline_artifact_present']}`
- Baseline Schema Valid: `{summary['baseline_schema_valid']}`
- Baseline Generated Timestamp Present: `{summary['baseline_generated_at_utc_present']}`
- WindowServer Visibility Recorded: `{summary['windowserver_visibility_recorded']}`
- Dock Visibility Recorded: `{summary['dock_visibility_recorded']}`
- WindowServer Visible: `{summary['windowserver_visible']}`
- Dock Visible: `{summary['dock_visible']}`
- Displays JSON Parse OK: `{summary['displays_json_parse_ok']}`
- Hardware JSON Parse OK: `{summary['hardware_json_parse_ok']}`
- UI Frame Pacing / Latency Measurement State: `{summary['ui_frame_pacing_latency_measurement_state']}`
- WindowServer Attribution Proof State: `{summary['windowserver_attribution_proof_state']}`
- UI Compositor Proof State: `{summary['ui_compositor_proof_state']}`
- Metal Proof State: `{summary['metal_proof_state']}`
- Real GPU Command Execution Attempted: `{summary['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{summary['rtx5070_workload_attribution_claimed']}`

## Command Summary

| Command Key | Present | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- | --- |
{cmd_rows}

## Conclusion

This release-readiness summary intentionally omits raw local command output and local logs. It is not acceleration proof, Metal proof, WindowServer attribution proof, or RTX 5070 workload attribution proof.
"""
    md_path = out_dir / "local-ui-baseline-artifact-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
