#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.dext_load_provider_match_proof_schema_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA",
    "CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS",
    "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
    "CLASSIFICATION_STATIC_CONTRACT",
    "DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_ONLY: True",
    "PROOF_SCHEMA_ONLY: True",
    "READ_ONLY_STATUS_EVIDENCE_ONLY: True",
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
    "FUTURE_DEXT_LOAD_EVIDENCE_REQUIREMENTS",
    "FUTURE_PROVIDER_MATCH_EVIDENCE_REQUIREMENTS",
    "VALID_PROOF_STATES",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_FILES",
    "REAL_UI_COMPOSITOR_ACCELERATION_RULE",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "dev.h1meka.H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "Dock",
    "transparency",
    "blur",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE",
    "DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED",
    "PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED",
    "REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED",
    "UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED",
    "METAL_PROOF_STATE: NOT_ATTEMPTED",
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

VALID_PROOF_STATES = {"NOT_ATTEMPTED", "BLOCKED", "CANDIDATE_OBSERVED", "PROVEN"}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check dext load / provider match proof schema.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "dext-load-provider-match-proof-schema.md"
    schema_path = root / "tools" / "driverkit-activation" / "dext-load-provider-match-proof-schema.json"
    gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"
    status_plan_path = root / "tools" / "driverkit-activation" / "activation-status-capture-plan.json"
    hardblock_path = root / "tools" / "driverkit-activation" / "ledger-override-hardblock-audit.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("proof_schema_json_exists", schema_path.exists(), str(schema_path)),
        make_check("activation_execution_gate_exists", gate_path.exists(), str(gate_path)),
        make_check("activation_status_capture_plan_exists", status_plan_path.exists(), str(status_plan_path)),
        make_check("ledger_override_hardblock_exists", hardblock_path.exists(), str(hardblock_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    proof = read_json(schema_path)
    gate = read_json(gate_path)
    status_plan = read_json(status_plan_path)

    checks.append(make_check("proof_schema_matches", bool(proof and proof.get("schema") == "h1mekartx.dext_load_provider_match_proof_schema.v1"), "proof schema"))
    checks.append(make_check("proof_schema_only_true", bool(proof and proof.get("proof_schema_only") is True), "proof_schema_only=true"))
    checks.append(make_check("read_only_status_evidence_only_true", bool(proof and proof.get("read_only_status_evidence_only") is True), "read_only_status_evidence_only=true"))
    checks.append(make_check("gate_blocks_execute", bool(gate and gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))
    checks.append(make_check("status_plan_read_only", bool(status_plan and status_plan.get("read_only_status_capture_only") is True), "activation status capture read-only"))

    for field in [
        "dext_load_proof_state",
        "provider_match_proof_state",
        "real_gpu_command_execution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
    ]:
        checks.append(make_check(
            f"{field}_not_attempted",
            bool(proof and proof.get(field) == "NOT_ATTEMPTED"),
            f"{field}=NOT_ATTEMPTED",
        ))

    proof_states = set(proof.get("valid_proof_states", [])) if proof else set()
    checks.append(make_check("valid_proof_states_match", proof_states == VALID_PROOF_STATES, ",".join(sorted(proof_states))))

    manifest = proof.get("target_pci_provider_matching_manifest", {}) if proof else {}
    checks.extend([
        make_check("target_vendor_id_matches", manifest.get("vendor_id") == "0x10de", "0x10de"),
        make_check("target_device_id_matches", manifest.get("device_id") == "0x2f04", "0x2f04"),
        make_check("target_iopci_match_matches", manifest.get("io_pci_match") == "0x2f0410de", "0x2f0410de"),
        make_check("expected_provider_class_matches", manifest.get("expected_provider_class") == "IOPCIDevice", "IOPCIDevice"),
        make_check("expected_driver_family_matches", manifest.get("expected_driver_family") == "PCIDriverKit", "PCIDriverKit"),
        make_check("expected_dext_bundle_id_matches", manifest.get("expected_dext_bundle_id") == "dev.h1meka.H1mekaRTXDriver", "dev.h1meka.H1mekaRTXDriver"),
    ])

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
            f"proof_{field}_false",
            bool(proof and proof.get(field) is False),
            f"{field}=false",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_READY" if failed_count == 0 else "FAIL_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 24 dext load / provider match proof schema",
        "dext_load_provider_match_proof_schema_only": True,
        "proof_schema_only": True,
        "read_only_status_evidence_only": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
        "dext_load_proof_state": "NOT_ATTEMPTED",
        "provider_match_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
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

    json_path = out_dir / "dext-load-provider-match-proof-schema-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Dext Load / Provider Match Proof Schema Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Proof Schema Only: `{report['proof_schema_only']}`
- Read-Only Status Evidence Only: `{report['read_only_status_evidence_only']}`
- Execute Mode Still Blocked: `{report['execute_mode_still_blocked']}`
- Ledger Ready Required For Execute: `{report['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
- Dext Load Proof State: `{report['dext_load_proof_state']}`
- Provider Match Proof State: `{report['provider_match_proof_state']}`
- Real GPU Command Execution Proof State: `{report['real_gpu_command_execution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
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

Phase 24 defines the proof schema only.

Dext load proof and provider match proof remain `NOT_ATTEMPTED`.

Dock/transparency/blur acceleration proof starts later, after real GPU command execution and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds dext load / provider match proof schema only. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "dext-load-provider-match-proof-schema-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
