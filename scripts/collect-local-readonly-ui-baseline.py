#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_readonly_ui_baseline_report.v1"

SAFE_COMMANDS = {
    "sw_vers": ["sw_vers"],
    "uname": ["uname", "-a"],
    "system_profiler_displays_json": ["system_profiler", "SPDisplaysDataType", "-json"],
    "system_profiler_hardware_json": ["system_profiler", "SPHardwareDataType", "-json"],
    "ioreg_display_connect": ["ioreg", "-r", "-c", "IODisplayConnect", "-l", "-w0"],
    "ioreg_framebuffer": ["ioreg", "-r", "-c", "IOFramebuffer", "-l", "-w0"],
    "process_table": ["ps", "-axo", "pid,ppid,comm,args"],
    "windowserver_recent_log": ["log", "show", "--last", "5m", "--style", "compact", "--predicate", 'process == "WindowServer"'],
    "dock_recent_log": ["log", "show", "--last", "5m", "--style", "compact", "--predicate", 'process == "Dock"'],
}

def run_cmd(cmd: list[str], timeout: int = 45) -> dict:
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-40000:],
            "stderr": completed.stderr[-12000:],
        }
    except FileNotFoundError:
        return {
            "command": cmd,
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
        }
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": cmd,
            "available": True,
            "returncode": None,
            "stdout": stdout[-40000:],
            "stderr": (stderr[-12000:] + "\ntimeout").strip(),
        }

def parse_json_text(text: str) -> object | None:
    try:
        return json.loads(text)
    except Exception:
        return None

def process_visibility(process_table: str, needle: str) -> dict:
    lines = [line for line in process_table.splitlines() if needle in line]
    return {
        "process_name": needle,
        "visible": bool(lines),
        "matching_line_count": len(lines),
        "redacted_lines": lines[:10],
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Collect local read-only UI baseline.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="host-report-bundle/ui-baseline", help="Local output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}
    for name, cmd in SAFE_COMMANDS.items():
        if shutil.which(cmd[0]) is None:
            commands[name] = {
                "command": cmd,
                "available": False,
                "returncode": None,
                "stdout": "",
                "stderr": "command not found",
            }
        else:
            commands[name] = run_cmd(cmd)

    process_text = commands.get("process_table", {}).get("stdout", "")
    displays_json = parse_json_text(commands.get("system_profiler_displays_json", {}).get("stdout", ""))
    hardware_json = parse_json_text(commands.get("system_profiler_hardware_json", {}).get("stdout", ""))

    baseline = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR",
        "secondary_classification": "CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "local_readonly_ui_baseline_collector_only": True,
        "local_baseline_only": True,
        "host_report_bundle_local_only": True,
        "measurement_not_acceleration_proof": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "mission_control_acceleration_not_claimed": True,
        "launchpad_acceleration_not_claimed": True,
        "stage_manager_acceleration_not_claimed": True,
        "local_readonly_ui_baseline_state": "COLLECTED_OR_UNAVAILABLE",
        "ui_frame_pacing_latency_measurement_state": "NOT_ATTEMPTED",
        "windowserver_attribution_proof_state": "NOT_ATTEMPTED",
        "core_animation_attribution_proof_state": "NOT_ATTEMPTED",
        "quartzcore_attribution_proof_state": "NOT_ATTEMPTED",
        "metal_compositor_attribution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "process_visibility": {
            "WindowServer": process_visibility(process_text, "WindowServer"),
            "Dock": process_visibility(process_text, "Dock"),
        },
        "parsed_system_profiler": {
            "displays_json_parse_ok": displays_json is not None,
            "hardware_json_parse_ok": hardware_json is not None,
            "displays_json_keys": sorted(list(displays_json.keys())) if isinstance(displays_json, dict) else [],
            "hardware_json_keys": sorted(list(hardware_json.keys())) if isinstance(hardware_json, dict) else [],
        },
        "commands": commands,
    }

    json_path = out_dir / "local-readonly-ui-baseline.json"
    json_path.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{name}` | `{result.get('available')}` | `{result.get('returncode')}` |"
        for name, result in commands.items()
    )

    md = f"""# Local Read-Only UI Baseline Report

- Generated At UTC: `{baseline['generated_at_utc']}`
- Classification: `{baseline['classification']}`
- Local Baseline Only: `{baseline['local_baseline_only']}`
- Host Report Bundle Local Only: `{baseline['host_report_bundle_local_only']}`
- Measurement Not Acceleration Proof: `{baseline['measurement_not_acceleration_proof']}`
- UI Compositor Proof Not Claimed: `{baseline['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{baseline['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{baseline['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{baseline['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{baseline['blur_acceleration_not_claimed']}`
- UI Frame Pacing / Latency Measurement State: `{baseline['ui_frame_pacing_latency_measurement_state']}`
- WindowServer Attribution Proof State: `{baseline['windowserver_attribution_proof_state']}`
- UI Compositor Proof State: `{baseline['ui_compositor_proof_state']}`
- Metal Proof State: `{baseline['metal_proof_state']}`
- Real GPU Command Execution Attempted: `{baseline['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{baseline['rtx5070_workload_attribution_claimed']}`

## Process Visibility

| Process | Visible | Matching Lines |
| --- | --- | ---: |
| WindowServer | `{baseline['process_visibility']['WindowServer']['visible']}` | `{baseline['process_visibility']['WindowServer']['matching_line_count']}` |
| Dock | `{baseline['process_visibility']['Dock']['visible']}` | `{baseline['process_visibility']['Dock']['matching_line_count']}` |

## Command Status

| Command Key | Available | Return Code |
| --- | --- | --- |
{command_rows}

## Conclusion

This local report is read-only baseline evidence only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "local-readonly-ui-baseline.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_READONLY_UI_BASELINE_COLLECTED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
