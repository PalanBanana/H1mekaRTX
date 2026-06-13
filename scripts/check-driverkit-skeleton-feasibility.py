#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.driverkit_skeleton_feasibility.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_STATIC_CONTRACT",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
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
    "TARGET_PCI_MATCHING_MANIFEST",
    "DRIVERKIT_SKELETON_PRECONDITIONS",
    "FUTURE_UI_COMPOSITOR_EVIDENCE_PATH",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "PCIDriverKit",
    "System Extension",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Dock",
    "transparency",
    "blur",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX DriverKit skeleton feasibility contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "driverkit-skeleton-feasibility-contract.md"

    checks = [make_check("contract_file_exists", contract_path.exists(), str(contract_path))]
    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_DRIVERKIT_SKELETON_FEASIBILITY_READY" if failed_count == 0 else "FAIL_DRIVERKIT_SKELETON_FEASIBILITY"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "secondary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 4 DriverKit / PCIDriverKit skeleton feasibility",
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "device_ownership_request_attempted": False,
        "hardware_access_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
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
        "future_evidence_path": [
            "DriverKit feasibility",
            "reversible System Extension activation planning",
            "read-only PCI provider matching",
            "runtime probe",
            "real GPU command execution",
            "UI compositor proof",
            "Metal proof",
        ],
        "checks": checks,
    }

    json_path = out_dir / "driverkit-skeleton-feasibility-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# DriverKit Skeleton Feasibility Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Device Ownership Request Attempted: `{report['device_ownership_request_attempted']}`
- Hardware Access Attempted: `{report['hardware_access_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- Real GPU Acceleration Claimed: `{report['real_gpu_acceleration_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Target User-Visible UI Goal

This feasibility preflight preserves the RTX 5070 macOS UI compositor goal:

- Dock animation
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager

No success is claimed in this phase.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Safety Boundary

This Phase 4 feasibility contract does not activate DriverKit, does not activate a System Extension, does not request device ownership, does not mutate BAR/MMIO, and does not submit GPU commands.

## Next Phase Recommendation

If this contract passes, the next safe step is a DriverKit skeleton planning PR that creates a non-activating template layout and entitlement documentation only. Real runtime access, UI compositor proof, and Metal proof remain blocked.
"""

    md_path = out_dir / "driverkit-skeleton-feasibility-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
