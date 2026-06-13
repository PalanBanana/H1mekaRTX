#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.reversible_driverkit_activation_dryrun.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN_PLAN",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "DRY_RUN_PLAN_ONLY: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEVICE_OWNERSHIP_REQUEST: True",
    "NO_PROVIDER_OPEN: True",
    "NO_BAR_MAPPING: True",
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
    "REVERSIBLE_DRIVERKIT_ACTIVATION_PREREQUISITES",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "REVERSIBLE_ACTIVATION_DRYRUN_CHECKLIST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "systemextensionsctl",
    "sysextd",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
    "DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False",
    "PROVIDER_OPEN_ATTEMPTED: False",
    "BAR_MAPPING_ATTEMPTED: False",
    "BAR_MMIO_MUTATION_ATTEMPTED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

def run_cmd(args: list[str], timeout: int = 15) -> dict:
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
        return {"command": args, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
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
    parser = argparse.ArgumentParser(description="Check reversible DriverKit activation dry-run contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    parser.add_argument("--collect-local", action="store_true", help="Collect safe local System Extension status only")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "reversible-driverkit-activation-dryrun-plan.md"

    checks = [make_check("contract_file_exists", contract_path.exists(), str(contract_path))]
    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    local_observations = {
        "collection_enabled": bool(args.collect_local),
        "dry_run_plan_only": True,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
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
            "systemextensionsctl_list": ["systemextensionsctl", "list"],
            "sw_vers": ["sw_vers"],
            "uname": ["uname", "-a"],
        }
        for name, cmd in safe_commands.items():
            if shutil.which(cmd[0]) is None:
                result = {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
            else:
                result = run_cmd(cmd)
            local_observations["commands"][name] = result

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN_READY" if failed_count == 0 else "FAIL_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN_PLAN",
        "secondary_classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 8 reversible DriverKit/System Extension activation dry-run plan",
        "dry_run_plan_only": True,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "target_pci_provider_matching_manifest": {
            "target_gpu": "NVIDIA RTX 5070",
            "architecture_family": "NVIDIA Blackwell",
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "io_pci_match": "0x2f0410de",
            "expected_provider_class": "IOPCIDevice",
            "expected_driver_family": "PCIDriverKit",
            "expected_entitlement": "com.apple.developer.driverkit.transport.pci",
            "expected_system_extension_entitlement": "com.apple.developer.system-extension.install",
        },
        "target_user_visible_goal": [
            "smooth Dock animation",
            "working transparency",
            "working blur",
            "smooth window movement and resizing",
            "smooth Mission Control",
            "smooth Launchpad",
            "smooth Stage Manager",
        ],
        "future_evidence_path": [
            "reversible activation/deactivation plan",
            "host app and dext static skeleton",
            "entitlement and signing evidence",
            "local user-approved activation on disposable test install",
            "read-only provider open policy",
            "runtime probe",
            "real GPU command execution",
            "UI compositor proof",
            "Metal proof",
        ],
        "checks": checks,
        "local_observations": local_observations,
    }

    json_path = out_dir / "reversible-driverkit-activation-dryrun-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# Reversible DriverKit Activation Dry-Run Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Dry-Run Plan Only: `{report['dry_run_plan_only']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Device Ownership Request Attempted: `{report['device_ownership_request_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Target PCI Provider Matching Manifest

| Field | Value |
| --- | --- |
| target_gpu | NVIDIA RTX 5070 |
| architecture_family | NVIDIA Blackwell |
| vendor_id | 0x10de |
| device_id | 0x2f04 |
| io_pci_match | 0x2f0410de |
| expected_provider_class | IOPCIDevice |
| expected_driver_family | PCIDriverKit |
| expected_entitlement | com.apple.developer.driverkit.transport.pci |
| expected_system_extension_entitlement | com.apple.developer.system-extension.install |

## Target User-Visible UI Goal

This dry-run plan preserves the Hackintosh RTX 5070 macOS UI compositor target:

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

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Local Status Collection

Local System Extension status collection enabled: `{args.collect_local}`

When enabled, this records safe status-only output such as `systemextensionsctl list`. It does not activate or deactivate anything.

## Conclusion

This phase is a dry-run plan only. It does not activate DriverKit, does not activate a System Extension, does not open a provider, does not map BAR memory, and does not claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: add a non-activating host app + dext skeleton layout with Info.plist static validation only.
"""

    md_path = out_dir / "reversible-driverkit-activation-dryrun-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
