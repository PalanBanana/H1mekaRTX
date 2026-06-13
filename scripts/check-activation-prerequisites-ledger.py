#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_prerequisites_ledger_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "ACTIVATION_PREREQUISITES_LEDGER_ONLY: True",
    "REAL_ACTIVATION_NOT_ATTEMPTED: True",
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
    "REAL_DRIVERKIT_ACTIVATION_START_RULE",
    "ACTIVATION_PREREQUISITES_LEDGER_SCHEMA",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "ACTIVATION_GATE_STATE: BLOCKED_MISSING_PREREQUISITES",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
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

REQUIRED_LEDGER_KEYS = [
    "apple_developer_team_id",
    "approved_driverkit_entitlement",
    "approved_pci_transport_entitlement",
    "valid_signing_identity",
    "buildable_host_app_and_dext_project",
    "signed_artifacts",
    "disposable_rollback_capable_test_install",
    "reversible_activation_implementation",
    "reversible_deactivation_implementation",
    "explicit_user_approval_flow",
    "logs_status_capture_plan",
    "no_provider_open_policy",
    "no_bar_mapping_policy",
    "no_bar_mmio_mutation_policy",
    "no_gpu_command_submission_policy",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check DriverKit activation prerequisites ledger.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "activation-prerequisites-ledger.md"
    ledger_path = root / "tools" / "driverkit-activation" / "activation-prerequisites-ledger.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("ledger_json_exists", ledger_path.exists(), str(ledger_path)),
    ]

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    ledger = read_json(ledger_path)
    checks.append(make_check("ledger_schema_matches", bool(ledger and ledger.get("schema") == "h1mekartx.activation_prerequisites_ledger.v1"), "ledger schema"))
    checks.append(make_check("ledger_only_true", bool(ledger and ledger.get("activation_prerequisites_ledger_only") is True), "activation_prerequisites_ledger_only=true"))
    checks.append(make_check("activation_gate_blocked", bool(ledger and ledger.get("activation_gate_state") == "BLOCKED_MISSING_PREREQUISITES"), "BLOCKED_MISSING_PREREQUISITES"))

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
            f"ledger_{field}_false",
            bool(ledger and ledger.get(field) is False),
            f"{field}=false",
        ))

    items = ledger.get("ledger", []) if ledger else []
    by_key = {item.get("key"): item for item in items}
    for key in REQUIRED_LEDGER_KEYS:
        checks.append(make_check(f"ledger_key_present_{key}", key in by_key, key))

    required_items = [item for item in items if item.get("required_for_activation")]
    all_required_ready = all(item.get("status") == "READY" for item in required_items)
    missing_or_blocked = [item.get("key") for item in required_items if item.get("status") != "READY"]

    checks.append(make_check("required_items_not_all_ready_yet", not all_required_ready, "activation must remain blocked"))
    checks.append(make_check("missing_or_blocked_items_present", bool(missing_or_blocked), ",".join(missing_or_blocked)))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_ACTIVATION_PREREQUISITES_LEDGER_BLOCKED_READY" if failed_count == 0 else "FAIL_ACTIVATION_PREREQUISITES_LEDGER"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
        "secondary_classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 17 activation prerequisites ledger",
        "activation_prerequisites_ledger_only": True,
        "real_activation_not_attempted": True,
        "activation_gate_state": "BLOCKED_MISSING_PREREQUISITES",
        "all_required_items_ready": all_required_ready,
        "missing_or_blocked_items": missing_or_blocked,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
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
        "real_activation_start_rule": "Real activation starts only when all required ledger items are READY.",
        "checks": checks,
    }

    json_path = out_dir / "activation-prerequisites-ledger-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    ledger_rows = "\n".join(
        f"| `{item.get('key')}` | `{item.get('status')}` | `{item.get('required_for_activation')}` | {item.get('blocker_reason', '')} |"
        for item in items
    )

    md = f"""# Activation Prerequisites Ledger Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Activation Gate State: `{report['activation_gate_state']}`
- All Required Items Ready: `{report['all_required_items_ready']}`
- Real Activation Not Attempted: `{report['real_activation_not_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Dext Load Attempted: `{report['dext_load_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## When Real DriverKit/System Extension Activation Starts

Real activation starts only when all required ledger items are `READY`.

Current state: `BLOCKED_MISSING_PREREQUISITES`

## Ledger

| Key | Status | Required | Blocker |
| --- | --- | --- | --- |
{ledger_rows}

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{check_rows}

## Conclusion

This phase creates the activation prerequisites ledger only. It does not activate DriverKit, activate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "activation-prerequisites-ledger-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
