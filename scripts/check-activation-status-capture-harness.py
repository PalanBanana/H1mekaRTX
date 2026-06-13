#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.activation_status_capture_harness_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS",
    "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_STATIC_CONTRACT",
    "ACTIVATION_STATUS_CAPTURE_HARNESS_ONLY: True",
    "READ_ONLY_STATUS_CAPTURE_ONLY: True",
    "EXECUTE_MODE_STILL_BLOCKED: True",
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
    "SAFE_ACTIVATION_STATUS_COMMANDS",
    "ACTIVATION_STATUS_CAPTURE_HARNESS_FILES",
    "LOCAL_STATUS_OUTPUTS_IGNORED",
    "COMMITTED_CHECK_OUTPUTS",
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
    parser = argparse.ArgumentParser(description="Check activation status capture harness.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "activation-status-capture-harness.md"
    plan_path = root / "tools" / "driverkit-activation" / "activation-status-capture-plan.json"
    local_capture_path = root / "host-report-bundle" / "activation-status-capture" / "activation-status-capture.json"
    local_capture_md_path = root / "host-report-bundle" / "activation-status-capture" / "activation-status-capture.md"
    gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"
    hardblock_path = root / "tools" / "driverkit-activation" / "ledger-override-hardblock-audit.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("plan_json_exists", plan_path.exists(), str(plan_path)),
        make_check("local_capture_json_exists", local_capture_path.exists(), str(local_capture_path)),
        make_check("local_capture_markdown_exists", local_capture_md_path.exists(), str(local_capture_md_path)),
        make_check("activation_execution_gate_exists", gate_path.exists(), str(gate_path)),
        make_check("ledger_override_hardblock_exists", hardblock_path.exists(), str(hardblock_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    plan = read_json(plan_path)
    capture = read_json(local_capture_path)
    gate = read_json(gate_path)

    checks.append(make_check("plan_schema_matches", bool(plan and plan.get("schema") == "h1mekartx.activation_status_capture_plan.v1"), "plan schema"))
    checks.append(make_check("capture_schema_matches", bool(capture and capture.get("schema") == "h1mekartx.activation_status_capture.v1"), "capture schema"))
    checks.append(make_check("capture_read_only_true", bool(capture and capture.get("read_only_status_capture_only") is True), "read_only_status_capture_only=true"))
    checks.append(make_check("gate_blocks_execute", bool(gate and gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))

    for name, obj in [("plan", plan), ("capture", capture)]:
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
                f"{name}_{field}_false",
                bool(obj and obj.get(field) is False),
                f"{name}.{field}=false",
            ))

    commands = capture.get("safe_status_commands", {}) if capture else {}
    checks.append(make_check("systemextensionsctl_status_recorded", "systemextensionsctl_list" in commands, "systemextensionsctl_list"))
    checks.append(make_check("sysextd_log_status_recorded", "sysextd_recent_log" in commands, "sysextd_recent_log"))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_ACTIVATION_STATUS_CAPTURE_HARNESS_READY" if failed_count == 0 else "FAIL_ACTIVATION_STATUS_CAPTURE_HARNESS"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 23 activation status capture harness",
        "activation_status_capture_harness_only": True,
        "read_only_status_capture_only": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
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

    json_path = out_dir / "activation-status-capture-harness-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Activation Status Capture Harness Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Read-Only Status Capture Only: `{report['read_only_status_capture_only']}`
- Execute Mode Still Blocked: `{report['execute_mode_still_blocked']}`
- Ledger Ready Required For Execute: `{report['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
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

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds read-only status capture only. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "activation-status-capture-harness-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
