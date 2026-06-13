#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_status_capture.v1"

SAFE_COMMANDS = {
    "systemextensionsctl_list": ["systemextensionsctl", "list"],
    "sysextd_recent_log": [
        "log", "show",
        "--style", "compact",
        "--last", "10m",
        "--predicate", 'process == "sysextd" OR subsystem CONTAINS "systemextensions"',
    ],
    "sw_vers": ["sw_vers"],
    "uname": ["uname", "-a"],
}

def run_cmd(cmd: list[str], timeout: int = 25) -> dict:
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
            "stdout": completed.stdout[-20000:],
            "stderr": completed.stderr[-8000:],
        }
    except FileNotFoundError:
        return {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": cmd,
            "available": True,
            "returncode": None,
            "stdout": stdout[-20000:],
            "stderr": (stderr[-8000:] + "\ntimeout").strip(),
        }

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Collect read-only System Extension activation status.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="host-report-bundle/activation-status-capture", help="Local output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    gate = read_json(root / "tools" / "driverkit-activation" / "activation-execution-gate.json")
    ledger = read_json(root / "tools" / "driverkit-activation" / "activation-prerequisites-ledger.json")
    hardblock = read_json(root / "tools" / "driverkit-activation" / "ledger-override-hardblock-audit.json")

    commands = {}
    for name, cmd in SAFE_COMMANDS.items():
        if shutil.which(cmd[0]) is None:
            commands[name] = {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
        else:
            commands[name] = run_cmd(cmd)

    ledger_items = ledger.get("ledger", []) if ledger else []
    required_items = [item for item in ledger_items if item.get("required_for_activation")]
    all_required_ready = bool(required_items) and all(item.get("status") == "READY" for item in required_items)

    capture = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "activation_status_capture_harness_only": True,
        "read_only_status_capture_only": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": gate.get("activation_execution_gate_decision") if gate else "UNKNOWN",
        "all_required_ledger_items_ready": all_required_ready,
        "hardblock_loaded": hardblock is not None,
        "real_activation_not_attempted": True,
        "real_deactivation_not_attempted": True,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
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
        "safe_status_commands": commands,
        "dock_transparency_blur_state": "BLOCKED_UNTIL_REAL_GPU_COMMAND_AND_COMPOSITOR_ATTRIBUTION_EVIDENCE",
    }

    json_path = out_dir / "activation-status-capture.json"
    json_path.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{name}` | `{result.get('available')}` | `{result.get('returncode')}` |"
        for name, result in commands.items()
    )

    md = f"""# Activation Status Capture

- Generated At UTC: `{capture['generated_at_utc']}`
- Classification: `{capture['classification']}`
- Read-Only Status Capture Only: `{capture['read_only_status_capture_only']}`
- Execute Mode Still Blocked: `{capture['execute_mode_still_blocked']}`
- Ledger Ready Required For Execute: `{capture['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{capture['activation_execution_gate_decision']}`
- All Required Ledger Items Ready: `{capture['all_required_ledger_items_ready']}`
- Real Activation Not Attempted: `{capture['real_activation_not_attempted']}`
- Real Deactivation Not Attempted: `{capture['real_deactivation_not_attempted']}`
- DriverKit Activation Attempted: `{capture['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{capture['system_extension_activation_attempted']}`
- System Extension Deactivation Attempted: `{capture['system_extension_deactivation_attempted']}`
- Dext Load Attempted: `{capture['dext_load_attempted']}`
- Provider Open Attempted: `{capture['provider_open_attempted']}`
- BAR Mapping Attempted: `{capture['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{capture['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{capture['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{capture['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{capture['metal_proof_claimed']}`
- Dock / Transparency / Blur State: `{capture['dock_transparency_blur_state']}`

## Safe Status Commands

| Name | Available | Return Code |
| --- | --- | --- |
{command_rows}

## Conclusion

This capture is local read-only status evidence. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "activation-status-capture.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_ACTIVATION_STATUS_CAPTURE_COLLECTED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
