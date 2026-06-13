#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_deactivation_dryrun_skeleton_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON",
    "CLASSIFICATION_USER_APPROVAL_ROLLBACK_FLOW",
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_STATIC_CONTRACT",
    "ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_ONLY: True",
    "DEFAULT_MODE_DRY_RUN: True",
    "REAL_ACTIVATION_NOT_ATTEMPTED: True",
    "REAL_DEACTIVATION_NOT_ATTEMPTED: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEXT_LOAD: True",
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
    "NO_DIRECT_DOCK_INJECTION: True",
    "NO_WINDOWSERVER_PATCHING: True",
    "ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_FILES",
    "REAL_EXECUTION_RULE",
    "REAL_UI_COMPOSITOR_ACCELERATION_RULE",
    "Dock",
    "transparency",
    "blur",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False",
    "DEXT_LOAD_ATTEMPTED: False",
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

REQUIRED_SWIFT_TOKENS = [
    "dry-run-activate",
    "dry-run-deactivate",
    "status-plan",
    "realActivationAttempted = false",
    "realDeactivationAttempted = false",
    "providerOpenAttempted = false",
    "barMappingAttempted = false",
    "gpuCommandSubmissionAttempted = false",
    "request is not submitted in Phase 20",
    "Intentionally no top-level activation submit",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check activation/deactivation dry-run skeleton.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "activation-deactivation-dryrun-skeleton.md"
    plan_path = root / "tools" / "driverkit-activation" / "activation-deactivation-dryrun-plan.json"
    swift_path = root / "tools" / "driverkit-activation" / "H1mekaRTXSystemExtensionActivationDryRun.swift"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("plan_json_exists", plan_path.exists(), str(plan_path)),
        make_check("swift_skeleton_exists", swift_path.exists(), str(swift_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    swift_text = swift_path.read_text(encoding="utf-8", errors="replace") if swift_path.exists() else ""
    for token in REQUIRED_SWIFT_TOKENS:
        check_name = "requires_swift_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in swift_text, token))

    plan = read_json(plan_path)
    checks.append(make_check("plan_schema_matches", bool(plan and plan.get("schema") == "h1mekartx.activation_deactivation_dryrun_plan.v1"), "plan schema"))
    checks.append(make_check("plan_default_dry_run_true", bool(plan and plan.get("default_mode_dry_run") is True), "default_mode_dry_run=true"))
    checks.append(make_check("plan_activation_not_attempted", bool(plan and plan.get("system_extension_activation_attempted") is False), "activation=false"))
    checks.append(make_check("plan_deactivation_not_attempted", bool(plan and plan.get("system_extension_deactivation_attempted") is False), "deactivation=false"))

    for field in [
        "driverkit_activation_attempted",
        "system_extension_activation_attempted",
        "system_extension_deactivation_attempted",
        "dext_load_attempted",
        "device_ownership_request_attempted",
        "provider_open_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "real_gpu_command_execution_attempted",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(
            f"plan_{field}_false",
            bool(plan and plan.get(field) is False),
            f"{field}=false",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_READY" if failed_count == 0 else "FAIL_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON",
        "secondary_classification": "CLASSIFICATION_USER_APPROVAL_ROLLBACK_FLOW",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 20 activation/deactivation dry-run skeleton",
        "activation_deactivation_dryrun_skeleton_only": True,
        "default_mode_dry_run": True,
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
        "dock_transparency_blur_state": "BLOCKED_UNTIL_REAL_GPU_COMMAND_AND_COMPOSITOR_ATTRIBUTION_EVIDENCE",
        "checks": checks,
    }

    json_path = out_dir / "activation-deactivation-dryrun-skeleton-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Activation / Deactivation Dry-Run Skeleton Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Default Mode Dry-Run: `{report['default_mode_dry_run']}`
- Real Activation Not Attempted: `{report['real_activation_not_attempted']}`
- Real Deactivation Not Attempted: `{report['real_deactivation_not_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- System Extension Deactivation Attempted: `{report['system_extension_deactivation_attempted']}`
- Dext Load Attempted: `{report['dext_load_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`
- Dock / Transparency / Blur State: `{report['dock_transparency_blur_state']}`

## Timing

Phase 20 introduces the dry-run skeleton only.

First real injection equivalent starts in a future phase through official DriverKit/System Extension activation after ledger READY.

Dock/transparency/blur acceleration proof starts later, after real GPU command execution and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds activation/deactivation dry-run skeleton only. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "activation-deactivation-dryrun-skeleton-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
