#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.readonly_pci_provider_matching_gate.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_READONLY_PCI_PROVIDER_MATCHING_GATE",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "READ_ONLY_PROVIDER_MATCHING_ONLY: True",
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
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "READONLY_PCI_PROVIDER_MATCHING_REQUIREMENTS",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
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

def run_cmd(args: list[str], timeout: int = 25) -> dict:
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
            "stdout": completed.stdout[-16000:],
            "stderr": completed.stderr[-4000:],
        }
    except FileNotFoundError:
        return {"command": args, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[-16000:] if isinstance(exc.stdout, str) else "",
            "stderr": "timeout",
        }

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def find_tokens(text: str, tokens: list[str]) -> dict:
    lower = text.lower()
    return {token: (token.lower() in lower) for token in tokens}

def main() -> int:
    parser = argparse.ArgumentParser(description="Check read-only PCI provider matching gate contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    parser.add_argument("--collect-local", action="store_true", help="Collect safe local IORegistry observations")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "readonly-pci-provider-matching-gate.md"

    checks = [make_check("contract_file_exists", contract_path.exists(), str(contract_path))]
    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    local_observations = {
        "collection_enabled": bool(args.collect_local),
        "read_only_provider_matching_only": True,
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
        "candidate_text_hits": {},
    }

    if args.collect_local:
        safe_commands = {
            "ioreg_iopci": ["ioreg", "-r", "-c", "IOPCIDevice", "-l"],
            "ioreg_iographics": ["ioreg", "-r", "-c", "IOAccelerator", "-l"],
            "system_profiler_displays_json": ["system_profiler", "SPDisplaysDataType", "-json"],
        }
        combined = ""
        for name, cmd in safe_commands.items():
            if shutil.which(cmd[0]) is None:
                result = {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
            else:
                result = run_cmd(cmd)
            local_observations["commands"][name] = result
            combined += "\n" + result.get("stdout", "") + "\n" + result.get("stderr", "")
        local_observations["candidate_text_hits"] = find_tokens(
            combined,
            ["10de", "0x10de", "2f04", "0x2f04", "2f0410de", "NVIDIA", "NVDA", "IOPCIDevice"],
        )

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_READONLY_PCI_PROVIDER_MATCHING_GATE_READY" if failed_count == 0 else "FAIL_READONLY_PCI_PROVIDER_MATCHING_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_READONLY_PCI_PROVIDER_MATCHING_GATE",
        "secondary_classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 7 read-only PCI provider matching gate",
        "read_only_provider_matching_only": True,
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
            "read-only PCI provider matching",
            "reversible DriverKit/System Extension activation planning",
            "read-only provider open policy",
            "runtime probe",
            "real GPU command execution",
            "UI compositor proof",
            "Metal proof",
        ],
        "checks": checks,
        "local_observations": local_observations,
    }

    json_path = out_dir / "readonly-pci-provider-matching-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    hits = local_observations["candidate_text_hits"]
    hit_rows = "\n".join(
        f"| `{key}` | `{value}` |"
        for key, value in hits.items()
    ) if hits else "| local collection | disabled |"

    md_content = f"""# Read-Only PCI Provider Matching Gate Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Read-Only Provider Matching Only: `{report['read_only_provider_matching_only']}`
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

## Target User-Visible UI Goal

This gate preserves the Hackintosh RTX 5070 macOS UI compositor target:

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

## Local Candidate Text Hits

| Token | Seen |
| --- | --- |
{hit_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

Read-only PCI provider matching remains a preflight gate. It does not activate DriverKit, does not open a provider, does not map BAR memory, and does not claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: define a reversible DriverKit activation dry-run plan. Real provider open, BAR mapping, command execution, UI compositor proof, and Metal proof remain blocked.
"""

    md_path = out_dir / "readonly-pci-provider-matching-gate-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
