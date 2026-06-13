#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_execution_gate_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
    "CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON",
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_STATIC_CONTRACT",
    "ACTIVATION_EXECUTION_GATE_ONLY: True",
    "EXECUTE_MODE_BLOCKED_BY_DEFAULT: True",
    "LEDGER_READY_REQUIRED_FOR_EXECUTE: True",
    "REAL_ACTIVATION_NOT_ATTEMPTED: True",
    "REAL_DEACTIVATION_NOT_ATTEMPTED: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_DEACTIVATION: True",
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
    "ACTIVATION_EXECUTION_GATE_RULE",
    "ACTIVATION_EXECUTION_GATE_FILES",
    "REAL_UI_COMPOSITOR_ACCELERATION_RULE",
    "Dock",
    "transparency",
    "blur",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE",
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

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check System Extension activation execution gate.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "activation-execution-gate.md"
    gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"
    ledger_path = root / "tools" / "driverkit-activation" / "activation-prerequisites-ledger.json"
    dryrun_plan_path = root / "tools" / "driverkit-activation" / "activation-deactivation-dryrun-plan.json"
    approval_flow_path = root / "tools" / "driverkit-activation" / "user-approval-rollback-flow.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("gate_json_exists", gate_path.exists(), str(gate_path)),
        make_check("ledger_json_exists", ledger_path.exists(), str(ledger_path)),
        make_check("dryrun_plan_exists", dryrun_plan_path.exists(), str(dryrun_plan_path)),
        make_check("user_approval_flow_exists", approval_flow_path.exists(), str(approval_flow_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    gate = read_json(gate_path)
    ledger = read_json(ledger_path)
    dryrun_plan = read_json(dryrun_plan_path)
    approval_flow = read_json(approval_flow_path)

    checks.append(make_check("gate_schema_matches", bool(gate and gate.get("schema") == "h1mekartx.activation_execution_gate.v1"), "gate schema"))
    checks.append(make_check("gate_blocks_execute", bool(gate and gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))
    checks.append(make_check("gate_default_blocked", bool(gate and gate.get("execute_mode_blocked_by_default") is True), "execute_mode_blocked_by_default=true"))
    checks.append(make_check("gate_requires_ledger_ready", bool(gate and gate.get("ledger_ready_required_for_execute") is True), "ledger_ready_required_for_execute=true"))

    ledger_items = ledger.get("ledger", []) if ledger else []
    required_items = [item for item in ledger_items if item.get("required_for_activation")]
    all_required_ready = bool(required_items) and all(item.get("status") == "READY" for item in required_items)
    missing_or_blocked = [item.get("key") for item in required_items if item.get("status") != "READY"]

    checks.append(make_check("ledger_not_all_required_ready", not all_required_ready, "expected blocked before real activation"))
    checks.append(make_check("ledger_missing_or_blocked_items_present", bool(missing_or_blocked), ",".join(missing_or_blocked)))

    for name, obj in [
        ("gate", gate),
        ("dryrun_plan", dryrun_plan),
        ("approval_flow", approval_flow),
    ]:
        for field in [
            "driverkit_activation_attempted",
            "system_extension_activation_attempted",
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
                f"{name}_{field}_false",
                bool(obj and obj.get(field) is False),
                f"{name}.{field}=false",
            ))

    if gate:
        checks.append(make_check(
            "gate_system_extension_deactivation_false",
            gate.get("system_extension_deactivation_attempted") is False,
            "system_extension_deactivation_attempted=false",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_ACTIVATION_EXECUTION_GATE_BLOCKED_READY" if failed_count == 0 else "FAIL_ACTIVATION_EXECUTION_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 21 activation execution gate",
        "activation_execution_gate_only": True,
        "execute_mode_blocked_by_default": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
        "all_required_ledger_items_ready": all_required_ready,
        "missing_or_blocked_ledger_items": missing_or_blocked,
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

    json_path = out_dir / "activation-execution-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Activation Execution Gate Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Execute Mode Blocked By Default: `{report['execute_mode_blocked_by_default']}`
- Ledger Ready Required For Execute: `{report['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
- All Required Ledger Items Ready: `{report['all_required_ledger_items_ready']}`
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

## Missing Or Blocked Ledger Items

`{", ".join(missing_or_blocked) if missing_or_blocked else "none"}`

## Timing

Phase 21 introduces the execution gate only.

Future `--execute` activation/deactivation remains blocked until the activation prerequisites ledger is fully READY.

Dock/transparency/blur acceleration proof starts later, after real GPU command execution and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds an execution gate only. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "activation-execution-gate-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
