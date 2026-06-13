#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.hackintosh_ui_observability_baseline.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_HACKINTOSH_UI_OBSERVABILITY_BASELINE",
    "CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS",
    "CLASSIFICATION_STATIC_CONTRACT",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEVICE_OWNERSHIP_REQUEST: True",
    "NO_BAR_MMIO_MUTATION: True",
    "NO_COMMAND_SUBMISSION: True",
    "NO_GSP_FIRMWARE_LOAD: True",
    "NO_GPU_RESET: True",
    "NO_FRAMEBUFFER_INIT: True",
    "NO_DISPLAY_ENGINE_INIT: True",
    "NO_KERNEL_OR_PROCESS_INJECTION: True",
    "NO_SIP_AMFI_BYPASS: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "OBSERVATION_ONLY: True",
    "HACKINTOSH_UI_BASELINE_EVIDENCE_CHECKLIST",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "IOGraphics",
    "IOAccelerator",
    "IODisplay",
    "Dock",
    "transparency",
    "blur",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "HACKINTOSH_UI_BASELINE_OBSERVATION_ONLY: True",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
]

def run_cmd(args: list[str], timeout: int = 20) -> dict:
    try:
        completed = subprocess.run(
            args,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": args,
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-4000:],
        }
    except FileNotFoundError:
        return {
            "command": args,
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": "timeout",
        }

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def main() -> int:
    parser = argparse.ArgumentParser(description="Check Hackintosh UI compositor observability baseline contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    parser.add_argument("--collect-local", action="store_true", help="Collect safe local host observations")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "hackintosh-ui-compositor-observability-baseline.md"

    checks = [make_check("contract_file_exists", contract_path.exists(), str(contract_path))]
    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    local_observations = {
        "collection_enabled": bool(args.collect_local),
        "observation_only": True,
        "hardware_access_attempted": False,
        "driver_activation_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "gpu_command_submission_attempted": False,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "commands": {},
    }

    if args.collect_local:
        safe_commands = {
            "sw_vers": ["sw_vers"],
            "uname": ["uname", "-a"],
            "csrutil_status": ["csrutil", "status"],
            "windowserver_pgrep": ["pgrep", "-lf", "WindowServer"],
            "system_profiler_displays_json": ["system_profiler", "SPDisplaysDataType", "-json"],
            "system_profiler_hardware_json": ["system_profiler", "SPHardwareDataType", "-json"],
            "ioreg_display": ["ioreg", "-r", "-c", "IODisplayConnect", "-l"],
            "ioreg_accelerator": ["ioreg", "-r", "-c", "IOAccelerator", "-l"],
            "ioreg_pci": ["ioreg", "-r", "-c", "IOPCIDevice", "-l"],
        }
        for name, cmd in safe_commands.items():
            if shutil.which(cmd[0]) is None:
                local_observations["commands"][name] = {
                    "command": cmd,
                    "available": False,
                    "returncode": None,
                    "stdout": "",
                    "stderr": "command not found",
                }
            else:
                local_observations["commands"][name] = run_cmd(cmd)

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_HACKINTOSH_UI_OBSERVABILITY_BASELINE_READY" if failed_count == 0 else "FAIL_HACKINTOSH_UI_OBSERVABILITY_BASELINE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_HACKINTOSH_UI_OBSERVABILITY_BASELINE",
        "secondary_classification": "CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 5 Hackintosh UI compositor observability baseline",
        "observation_only": True,
        "hardware_access_attempted": False,
        "driver_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "target_user_visible_goal": [
            "smooth Dock animation",
            "working transparency",
            "working blur",
            "smooth window movement and resizing",
            "smooth Mission Control",
            "smooth Launchpad",
            "smooth Stage Manager",
        ],
        "graphics_stack_path": [
            "WindowServer",
            "Core Animation",
            "QuartzCore",
            "Metal compositor",
            "IOGraphics",
            "IOAccelerator",
            "IODisplay",
        ],
        "checks": checks,
        "local_observations": local_observations,
    }

    json_path = out_dir / "hackintosh-ui-observability-baseline-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# Hackintosh UI Compositor Observability Baseline Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Observation Only: `{report['observation_only']}`
- Hardware Access Attempted: `{report['hardware_access_attempted']}`
- Driver Activation Attempted: `{report['driver_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- Real GPU Acceleration Claimed: `{report['real_gpu_acceleration_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Target User-Visible UI Goal

This baseline preserves the Hackintosh RTX 5070 macOS UI compositor target:

- Dock animation
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager

No UI acceleration success is claimed in this phase.

## Graphics Stack Observation Path

- WindowServer
- Core Animation
- QuartzCore
- Metal compositor
- IOGraphics
- IOAccelerator
- IODisplay

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Local Observation Mode

Local observation collection enabled: `{args.collect_local}`

When enabled, this checker records only safe command output such as `sw_vers`, `system_profiler`, `ioreg`, and `WindowServer` process visibility. It does not activate drivers, modify BAR/MMIO, submit GPU commands, or claim acceleration.

## Next Phase Recommendation

Next safe step: compare baseline observations across machines/configurations, then prepare read-only PCI provider matching gates. Real RTX 5070 UI compositor proof remains blocked until real workload attribution and compositor routing evidence exist.
"""

    md_path = out_dir / "hackintosh-ui-observability-baseline-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
