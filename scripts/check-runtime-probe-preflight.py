#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.runtime_probe_preflight.v1"

REQUIRED_TOKENS = [
    "CLASSIFICATION_STATIC_CONTRACT",
    "CLASSIFICATION_RUNTIME_PROBE_PREFLIGHT",
    "READ_ONLY_PREFLIGHT_ONLY: True",
    "NO_BAR_MMIO_MUTATION: True",
    "NO_COMMAND_SUBMISSION: True",
    "NO_GSP_FIRMWARE_LOAD: True",
    "NO_GPU_RESET: True",
    "NO_SYSTEM_MODIFICATION: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_KERNEL_OR_PROCESS_INJECTION: True",
    "NO_SIP_AMFI_BYPASS: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "DRIVERKIT_PREREQUISITES",
    "FUTURE_UI_COMPOSITOR_EVIDENCE_CHECKLIST",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX runtime probe preflight contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "metal" / "runtime-probe-preflight-contract.md"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path))
    ]

    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")

    for token in REQUIRED_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_RUNTIME_PROBE_PREFLIGHT_READY" if failed_count == 0 else "FAIL_RUNTIME_PROBE_PREFLIGHT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_RUNTIME_PROBE_PREFLIGHT",
        "secondary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 3 runtime probe preflight",
        "hardware_access_attempted": False,
        "driver_activation_attempted": False,
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
            "WindowServer",
            "Core Animation",
            "QuartzCore",
            "Metal compositor",
            "UI compositor proof",
            "Metal proof",
        ],
        "safety_boundary": {
            "read_only_preflight_only": True,
            "bar_mmio_mutation_blocked": True,
            "command_submission_blocked": True,
            "gsp_firmware_load_blocked": True,
            "gpu_reset_blocked": True,
            "system_modification_blocked": True,
            "driver_activation_blocked": True,
            "kernel_or_process_injection_blocked": True,
            "sip_amfi_bypass_blocked": True,
            "private_framework_patching_blocked": True,
            "fake_metal_device_spoofing_blocked": True,
        },
        "checks": checks,
    }

    json_path = out_dir / "runtime-probe-preflight-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# Runtime Probe Preflight Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Hardware Access Attempted: `{report['hardware_access_attempted']}`
- Driver Activation Attempted: `{report['driver_activation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- Real GPU Acceleration Claimed: `{report['real_gpu_acceleration_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Target User-Visible UI Goal

This preflight preserves the project goal of eventually validating smooth macOS UI compositor behavior:

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

## Safety Policy Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Safety Boundary

This Phase 3 preflight is non-invasive. It does not attempt hardware access, driver activation, BAR/MMIO mutation, GPU reset, firmware loading, or GPU command submission.

## Next Phase Recommendation

If this preflight passes, the next phase may prepare DriverKit / PCIDriverKit skeleton planning and entitlement documentation. Real runtime access, command execution, UI compositor proof, and Metal proof remain blocked until later evidence gates.
"""

    md_path = out_dir / "runtime-probe-preflight-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Preflight Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
