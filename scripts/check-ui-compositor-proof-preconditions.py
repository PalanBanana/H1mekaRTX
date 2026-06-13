#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ui_compositor_proof_preconditions_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA",
    "CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE",
    "CLASSIFICATION_GPU_COMMAND_SUBMISSION_PROHIBITION_GATE",
    "CLASSIFICATION_STATIC_CONTRACT",
    "UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA_ONLY: True",
    "UI_COMPOSITOR_PROOF_NOT_CLAIMED: True",
    "METAL_PROOF_NOT_CLAIMED: True",
    "DOCK_ACCELERATION_NOT_CLAIMED: True",
    "TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True",
    "BLUR_ACCELERATION_NOT_CLAIMED: True",
    "MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True",
    "LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True",
    "STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True",
    "FIRMWARE_LOAD_FORBIDDEN: True",
    "GPU_RESET_FORBIDDEN: True",
    "FRAMEBUFFER_INIT_FORBIDDEN: True",
    "DISPLAY_ENGINE_INIT_FORBIDDEN: True",
    "GPU_COMMAND_SUBMISSION_FORBIDDEN: True",
    "CONFIGURATION_WRITES_FORBIDDEN: True",
    "BAR_MAPPING_FORBIDDEN: True",
    "BAR_MMIO_MUTATION_FORBIDDEN: True",
    "MEMORY_DESCRIPTOR_MAPPING_FORBIDDEN: True",
    "PROVIDER_OPEN_FORBIDDEN: True",
    "PROVIDER_MATCH_PROOF_NOT_CLAIMED: True",
    "CANDIDATE_SUMMARY_ONLY: True",
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
    "NO_CONFIGURATION_WRITES: True",
    "NO_MEMORY_DESCRIPTOR_MAPPING: True",
    "NO_COMMAND_SUBMISSION: True",
    "NO_FIRMWARE_LOAD: True",
    "NO_GPU_RESET: True",
    "NO_FRAMEBUFFER_INIT: True",
    "NO_DISPLAY_ENGINE_INIT: True",
    "NO_MODESET: True",
    "NO_SCANOUT_INIT: True",
    "NO_METAL_COMMAND_QUEUE: True",
    "NO_METAL_COMMAND_BUFFER: True",
    "NO_METAL_COMMAND_ENCODER: True",
    "NO_METAL_COMMAND_COMMIT: True",
    "NO_KERNEL_OR_PROCESS_INJECTION: True",
    "NO_SIP_AMFI_BYPASS: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "NO_DIRECT_DOCK_INJECTION: True",
    "NO_WINDOWSERVER_PATCHING: True",
    "UI_COMPOSITOR_PROOF_REQUIRED_PRECONDITIONS",
    "UI_COMPOSITOR_REQUIRED_SCENARIOS",
    "UI_COMPOSITOR_REQUIRED_EVIDENCE_BUCKETS",
    "VALID_UI_COMPOSITOR_PROOF_STATES",
    "UI_COMPOSITOR_PROOF_DEPENDENCY_CHAIN",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock magnification",
    "transparency",
    "blur",
    "Mission Control",
    "Launchpad",
    "Stage Manager",
    "UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
    "DOCK_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "TRANSPARENCY_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "BLUR_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "MISSION_CONTROL_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "LAUNCHPAD_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "STAGE_MANAGER_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

VALID_STATES = {
    "NOT_ATTEMPTED",
    "BLOCKED",
    "PRECONDITIONS_INCOMPLETE",
    "CANDIDATE_OBSERVED",
    "PROVEN",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check UI compositor proof preconditions schema.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "hackintosh" / "ui-compositor-proof-preconditions.md"
    schema_path = root / "tools" / "driverkit-activation" / "ui-compositor-proof-preconditions.json"
    firmware_gate_path = root / "tools" / "driverkit-activation" / "firmware-reset-display-init-prohibition-gate.json"
    gpu_gate_path = root / "tools" / "driverkit-activation" / "gpu-command-submission-prohibition-gate.json"
    config_gate_path = root / "tools" / "driverkit-activation" / "config-write-prohibition-gate.json"
    bar_gate_path = root / "tools" / "driverkit-activation" / "bar-mapping-prohibition-gate.json"
    provider_gate_path = root / "tools" / "driverkit-activation" / "provider-open-prohibition-gate.json"
    activation_gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("ui_compositor_preconditions_json_exists", schema_path.exists(), str(schema_path)),
        make_check("firmware_reset_display_gate_json_exists", firmware_gate_path.exists(), str(firmware_gate_path)),
        make_check("gpu_command_gate_json_exists", gpu_gate_path.exists(), str(gpu_gate_path)),
        make_check("config_write_gate_json_exists", config_gate_path.exists(), str(config_gate_path)),
        make_check("bar_mapping_gate_json_exists", bar_gate_path.exists(), str(bar_gate_path)),
        make_check("provider_open_gate_json_exists", provider_gate_path.exists(), str(provider_gate_path)),
        make_check("activation_execution_gate_exists", activation_gate_path.exists(), str(activation_gate_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    schema = read_json(schema_path)
    firmware_gate = read_json(firmware_gate_path)
    gpu_gate = read_json(gpu_gate_path)
    config_gate = read_json(config_gate_path)
    bar_gate = read_json(bar_gate_path)
    provider_gate = read_json(provider_gate_path)
    activation_gate = read_json(activation_gate_path)

    checks.append(make_check("schema_matches", bool(schema and schema.get("schema") == "h1mekartx.ui_compositor_proof_preconditions.v1"), "schema"))
    checks.append(make_check("precondition_schema_only_true", bool(schema and schema.get("ui_compositor_proof_precondition_schema_only") is True), "schema only"))
    checks.append(make_check("ui_compositor_not_claimed", bool(schema and schema.get("ui_compositor_proof_not_claimed") is True), "UI compositor proof not claimed"))
    checks.append(make_check("metal_not_claimed", bool(schema and schema.get("metal_proof_not_claimed") is True), "Metal proof not claimed"))
    checks.append(make_check("precondition_state_incomplete", bool(schema and schema.get("ui_compositor_proof_precondition_state") == "PRECONDITIONS_INCOMPLETE"), "PRECONDITIONS_INCOMPLETE"))

    states = set(schema.get("valid_ui_compositor_proof_states", [])) if schema else set()
    checks.append(make_check("valid_states_match", states == VALID_STATES, ",".join(sorted(states))))

    checks.append(make_check("firmware_gate_enforced", bool(firmware_gate and firmware_gate.get("firmware_reset_display_init_prohibition_state") == "ENFORCED"), "firmware gate enforced"))
    checks.append(make_check("gpu_gate_enforced", bool(gpu_gate and gpu_gate.get("gpu_command_submission_prohibition_state") == "ENFORCED"), "GPU command gate enforced"))
    checks.append(make_check("config_gate_enforced", bool(config_gate and config_gate.get("config_write_prohibition_state") == "ENFORCED"), "config gate enforced"))
    checks.append(make_check("bar_gate_enforced", bool(bar_gate and bar_gate.get("bar_mapping_prohibition_state") == "ENFORCED"), "BAR gate enforced"))
    checks.append(make_check("provider_gate_enforced", bool(provider_gate and provider_gate.get("provider_open_prohibition_state") == "ENFORCED"), "provider gate enforced"))
    checks.append(make_check("activation_gate_blocks_execute", bool(activation_gate and activation_gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))

    required_preconditions = schema.get("required_preconditions", []) if schema else []
    required_scenarios = schema.get("required_ui_scenarios", []) if schema else []
    checks.append(make_check("required_preconditions_present", len(required_preconditions) >= 12, str(len(required_preconditions))))
    checks.append(make_check("required_ui_scenarios_present", len(required_scenarios) >= 8, str(len(required_scenarios))))

    for field in [
        "ui_compositor_proof_state",
        "metal_proof_state",
        "dock_acceleration_proof_state",
        "transparency_acceleration_proof_state",
        "blur_acceleration_proof_state",
        "mission_control_acceleration_proof_state",
        "launchpad_acceleration_proof_state",
        "stage_manager_acceleration_proof_state",
        "provider_match_proof_state",
        "dext_load_proof_state",
        "real_gpu_command_execution_proof_state",
    ]:
        checks.append(make_check(
            f"schema_{field}_not_attempted",
            bool(schema and schema.get(field) == "NOT_ATTEMPTED"),
            f"{field}=NOT_ATTEMPTED",
        ))

    for field in [
        "driverkit_activation_attempted",
        "system_extension_activation_attempted",
        "system_extension_deactivation_attempted",
        "dext_load_attempted",
        "device_ownership_request_attempted",
        "provider_open_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "memory_descriptor_mapping_attempted",
        "gpu_command_queue_attempted",
        "gpu_command_buffer_attempted",
        "gpu_command_encoder_attempted",
        "gpu_command_commit_attempted",
        "firmware_load_attempted",
        "gpu_reset_attempted",
        "framebuffer_init_attempted",
        "display_engine_init_attempted",
        "real_gpu_command_execution_attempted",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(
            f"schema_{field}_false",
            bool(schema and schema.get(field) is False),
            f"{field}=false",
        ))

    manifest = schema.get("target_pci_provider_matching_manifest", {}) if schema else {}
    checks.extend([
        make_check("target_vendor_id_matches", manifest.get("vendor_id") == "0x10de", "0x10de"),
        make_check("target_device_id_matches", manifest.get("device_id") == "0x2f04", "0x2f04"),
        make_check("target_iopci_match_matches", manifest.get("io_pci_match") == "0x2f0410de", "0x2f0410de"),
        make_check("expected_provider_class_matches", manifest.get("expected_provider_class") == "IOPCIDevice", "IOPCIDevice"),
        make_check("expected_driver_family_matches", manifest.get("expected_driver_family") == "PCIDriverKit", "PCIDriverKit"),
    ])

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA_READY" if failed_count == 0 else "FAIL_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA",
        "secondary_classification": "CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 32 UI compositor proof precondition schema",
        "ui_compositor_proof_precondition_schema_only": True,
        "ui_compositor_proof_not_claimed": True,
        "metal_proof_not_claimed": True,
        "dock_acceleration_not_claimed": True,
        "transparency_acceleration_not_claimed": True,
        "blur_acceleration_not_claimed": True,
        "mission_control_acceleration_not_claimed": True,
        "launchpad_acceleration_not_claimed": True,
        "stage_manager_acceleration_not_claimed": True,
        "ui_compositor_proof_precondition_state": "PRECONDITIONS_INCOMPLETE",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "dock_acceleration_proof_state": "NOT_ATTEMPTED",
        "transparency_acceleration_proof_state": "NOT_ATTEMPTED",
        "blur_acceleration_proof_state": "NOT_ATTEMPTED",
        "mission_control_acceleration_proof_state": "NOT_ATTEMPTED",
        "launchpad_acceleration_proof_state": "NOT_ATTEMPTED",
        "stage_manager_acceleration_proof_state": "NOT_ATTEMPTED",
        "firmware_reset_display_init_prohibition_state": "ENFORCED",
        "gpu_command_submission_prohibition_state": "ENFORCED",
        "config_write_prohibition_state": "ENFORCED",
        "bar_mapping_prohibition_state": "ENFORCED",
        "provider_open_prohibition_state": "ENFORCED",
        "provider_match_proof_state": "NOT_ATTEMPTED",
        "dext_load_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
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
        "configuration_writes_attempted": False,
        "memory_descriptor_mapping_attempted": False,
        "gpu_command_queue_attempted": False,
        "gpu_command_buffer_attempted": False,
        "gpu_command_encoder_attempted": False,
        "gpu_command_commit_attempted": False,
        "firmware_load_attempted": False,
        "gpu_reset_attempted": False,
        "framebuffer_init_attempted": False,
        "display_engine_init_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "ui-compositor-proof-preconditions-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# UI Compositor Proof Precondition Schema Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- UI Compositor Proof Not Claimed: `{report['ui_compositor_proof_not_claimed']}`
- Metal Proof Not Claimed: `{report['metal_proof_not_claimed']}`
- Dock Acceleration Not Claimed: `{report['dock_acceleration_not_claimed']}`
- Transparency Acceleration Not Claimed: `{report['transparency_acceleration_not_claimed']}`
- Blur Acceleration Not Claimed: `{report['blur_acceleration_not_claimed']}`
- Mission Control Acceleration Not Claimed: `{report['mission_control_acceleration_not_claimed']}`
- Launchpad Acceleration Not Claimed: `{report['launchpad_acceleration_not_claimed']}`
- Stage Manager Acceleration Not Claimed: `{report['stage_manager_acceleration_not_claimed']}`
- UI Compositor Proof Precondition State: `{report['ui_compositor_proof_precondition_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Dock Acceleration Proof State: `{report['dock_acceleration_proof_state']}`
- Transparency Acceleration Proof State: `{report['transparency_acceleration_proof_state']}`
- Blur Acceleration Proof State: `{report['blur_acceleration_proof_state']}`
- Firmware/Reset/Display Gate: `{report['firmware_reset_display_init_prohibition_state']}`
- GPU Command Gate: `{report['gpu_command_submission_prohibition_state']}`
- Provider Open Gate: `{report['provider_open_prohibition_state']}`
- Provider Match Proof State: `{report['provider_match_proof_state']}`
- Dext Load Proof State: `{report['dext_load_proof_state']}`
- Real GPU Command Execution Proof State: `{report['real_gpu_command_execution_proof_state']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Timing

Phase 32 defines UI compositor proof preconditions only.

Dock/transparency/blur/Mission Control/Launchpad/Stage Manager acceleration proof remains `NOT_ATTEMPTED`.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds UI compositor proof precondition schema only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ui-compositor-proof-preconditions-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
