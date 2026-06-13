#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.provider_match_candidate_summary_gate_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE",
    "CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_COLLECTOR",
    "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA",
    "CLASSIFICATION_STATIC_CONTRACT",
    "PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE_ONLY: True",
    "SUMMARY_GATE_ONLY: True",
    "CANDIDATE_SUMMARY_ONLY: True",
    "PROVIDER_MATCH_PROOF_NOT_CLAIMED: True",
    "PROVIDER_OPEN_FORBIDDEN: True",
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
    "PROVIDER_MATCH_CANDIDATE_SUMMARY_INPUTS",
    "PROVIDER_MATCH_CANDIDATE_SUMMARY_OUTPUTS",
    "PROVIDER_MATCH_CANDIDATE_SUMMARY_RULE",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
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
    "PROVIDER_MATCH_CANDIDATE_SUMMARY_STATE: SUMMARY_ONLY",
    "PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED",
    "DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED",
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

ALLOWED_CANDIDATE_STATES = {
    "CANDIDATE_OBSERVED",
    "NO_TARGET_CANDIDATE_OBSERVED",
    "UNKNOWN",
}

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check provider match candidate summary gate.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "provider-match-candidate-summary-gate.md"
    summary_path = root / "tools" / "driverkit-activation" / "provider-match-candidate-summary-gate.json"
    provider_check_path = root / "release-readiness" / "provider-match-candidate-collector-check.json"
    provider_plan_path = root / "tools" / "driverkit-activation" / "provider-match-candidate-collector-plan.json"
    proof_schema_path = root / "tools" / "driverkit-activation" / "dext-load-provider-match-proof-schema.json"
    gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("summary_gate_json_exists", summary_path.exists(), str(summary_path)),
        make_check("provider_candidate_collector_check_exists", provider_check_path.exists(), str(provider_check_path)),
        make_check("provider_candidate_collector_plan_exists", provider_plan_path.exists(), str(provider_plan_path)),
        make_check("dext_load_provider_match_proof_schema_exists", proof_schema_path.exists(), str(proof_schema_path)),
        make_check("activation_execution_gate_exists", gate_path.exists(), str(gate_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    summary = read_json(summary_path)
    provider_check = read_json(provider_check_path)
    provider_plan = read_json(provider_plan_path)
    proof_schema = read_json(proof_schema_path)
    gate = read_json(gate_path)

    checks.append(make_check("summary_schema_matches", bool(summary and summary.get("schema") == "h1mekartx.provider_match_candidate_summary_gate.v1"), "summary schema"))
    checks.append(make_check("summary_gate_only_true", bool(summary and summary.get("summary_gate_only") is True), "summary_gate_only=true"))
    checks.append(make_check("candidate_summary_only_true", bool(summary and summary.get("candidate_summary_only") is True), "candidate_summary_only=true"))
    checks.append(make_check("provider_match_proof_not_claimed", bool(summary and summary.get("provider_match_proof_not_claimed") is True), "provider_match_proof_not_claimed=true"))
    checks.append(make_check("provider_open_forbidden", bool(summary and summary.get("provider_open_forbidden") is True), "provider_open_forbidden=true"))
    checks.append(make_check("gate_blocks_execute", bool(gate and gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))
    checks.append(make_check("provider_plan_candidate_only", bool(provider_plan and provider_plan.get("candidate_report_only") is True), "provider plan candidate only"))
    checks.append(make_check("proof_schema_only", bool(proof_schema and proof_schema.get("proof_schema_only") is True), "proof schema only"))

    source_candidate_state = provider_check.get("provider_match_candidate_state", "UNKNOWN") if provider_check else "UNKNOWN"
    checks.append(make_check("source_candidate_state_allowed", source_candidate_state in ALLOWED_CANDIDATE_STATES, source_candidate_state))

    manifest = summary.get("target_pci_provider_matching_manifest", {}) if summary else {}
    checks.extend([
        make_check("target_vendor_id_matches", manifest.get("vendor_id") == "0x10de", "0x10de"),
        make_check("target_device_id_matches", manifest.get("device_id") == "0x2f04", "0x2f04"),
        make_check("target_iopci_match_matches", manifest.get("io_pci_match") == "0x2f0410de", "0x2f0410de"),
        make_check("expected_provider_class_matches", manifest.get("expected_provider_class") == "IOPCIDevice", "IOPCIDevice"),
        make_check("expected_driver_family_matches", manifest.get("expected_driver_family") == "PCIDriverKit", "PCIDriverKit"),
    ])

    for name, obj in [
        ("summary", summary),
        ("provider_check", provider_check),
        ("provider_plan", provider_plan),
    ]:
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

    for field in [
        "provider_match_proof_state",
        "dext_load_proof_state",
        "real_gpu_command_execution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
    ]:
        checks.append(make_check(
            f"summary_{field}_not_attempted",
            bool(summary and summary.get(field) == "NOT_ATTEMPTED"),
            f"{field}=NOT_ATTEMPTED",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE_READY" if failed_count == 0 else "FAIL_PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE",
        "secondary_classification": "CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_COLLECTOR",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 26 provider match candidate summary gate",
        "provider_match_candidate_summary_gate_only": True,
        "summary_gate_only": True,
        "candidate_summary_only": True,
        "provider_match_proof_not_claimed": True,
        "provider_open_forbidden": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
        "source_provider_match_candidate_state": source_candidate_state,
        "provider_match_candidate_summary_state": "SUMMARY_ONLY",
        "provider_match_proof_state": "NOT_ATTEMPTED",
        "dext_load_proof_state": "NOT_ATTEMPTED",
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

    json_path = out_dir / "provider-match-candidate-summary-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Provider Match Candidate Summary Gate Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Summary Gate Only: `{report['summary_gate_only']}`
- Candidate Summary Only: `{report['candidate_summary_only']}`
- Provider Match Proof Not Claimed: `{report['provider_match_proof_not_claimed']}`
- Provider Open Forbidden: `{report['provider_open_forbidden']}`
- Execute Mode Still Blocked: `{report['execute_mode_still_blocked']}`
- Ledger Ready Required For Execute: `{report['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
- Source Provider Match Candidate State: `{report['source_provider_match_candidate_state']}`
- Provider Match Candidate Summary State: `{report['provider_match_candidate_summary_state']}`
- Provider Match Proof State: `{report['provider_match_proof_state']}`
- Dext Load Proof State: `{report['dext_load_proof_state']}`
- Real GPU Command Execution Proof State: `{report['real_gpu_command_execution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`
- Dock / Transparency / Blur State: `{report['dock_transparency_blur_state']}`

## Timing

Phase 26 summarizes provider match candidate state only.

Candidate summary is not provider match proof.

Dock/transparency/blur acceleration proof starts later, after real GPU command execution and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds provider match candidate summary gate only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "provider-match-candidate-summary-gate-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
