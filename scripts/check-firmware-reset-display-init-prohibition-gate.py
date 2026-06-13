#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.firmware_reset_display_init_prohibition_gate_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE",
    "CLASSIFICATION_GPU_COMMAND_SUBMISSION_PROHIBITION_GATE",
    "CLASSIFICATION_CONFIG_WRITE_PROHIBITION_GATE",
    "CLASSIFICATION_STATIC_CONTRACT",
    "FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_ONLY: True",
    "FIRMWARE_LOAD_FORBIDDEN: True",
    "GPU_RESET_FORBIDDEN: True",
    "FRAMEBUFFER_INIT_FORBIDDEN: True",
    "DISPLAY_ENGINE_INIT_FORBIDDEN: True",
    "MODESET_FORBIDDEN: True",
    "SCANOUT_INIT_FORBIDDEN: True",
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
    "FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_AUDIT_SCOPE",
    "FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_RULE",
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
    "FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_STATE: ENFORCED",
    "GPU_COMMAND_SUBMISSION_PROHIBITION_STATE: ENFORCED",
    "CONFIG_WRITE_PROHIBITION_STATE: ENFORCED",
    "BAR_MAPPING_PROHIBITION_STATE: ENFORCED",
    "PROVIDER_OPEN_PROHIBITION_STATE: ENFORCED",
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
    "CONFIGURATION_WRITES_ATTEMPTED: False",
    "MEMORY_DESCRIPTOR_MAPPING_ATTEMPTED: False",
    "GPU_COMMAND_QUEUE_ATTEMPTED: False",
    "GPU_COMMAND_BUFFER_ATTEMPTED: False",
    "GPU_COMMAND_ENCODER_ATTEMPTED: False",
    "GPU_COMMAND_COMMIT_ATTEMPTED: False",
    "FIRMWARE_LOAD_ATTEMPTED: False",
    "GPU_RESET_ATTEMPTED: False",
    "FRAMEBUFFER_INIT_ATTEMPTED: False",
    "DISPLAY_ENGINE_INIT_ATTEMPTED: False",
    "MODESET_ATTEMPTED: False",
    "SCANOUT_INIT_ATTEMPTED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

FIRMWARE_MARKER_PARTS = [
    ("GSP", "Firmware"),
    ("firmware", "Load"),
    ("load", "Firmware"),
    ("ucode", "Load"),
    ("microcode", "Load"),
    ("boot", "Firmware"),
]

RESET_MARKER_PARTS = [
    ("GPU", "Reset"),
    ("reset", "GPU"),
    ("device", "Reset"),
    ("engine", "Reset"),
    ("graphics", "Reset"),
]

DISPLAY_INIT_MARKER_PARTS = [
    ("framebuffer", "Init"),
    ("init", "Framebuffer"),
    ("display", "EngineInit"),
    ("display", "Engine", "Init"),
    ("display", "Pipe", "Init"),
    ("scanout", "Init"),
    ("mode", "Set"),
    ("modeset", "Init"),
    ("head", "Init"),
    ("crtc", "Init"),
]

FIRMWARE_MARKERS = ["".join(parts) for parts in FIRMWARE_MARKER_PARTS]
RESET_MARKERS = ["".join(parts) for parts in RESET_MARKER_PARTS]
DISPLAY_INIT_MARKERS = ["".join(parts) for parts in DISPLAY_INIT_MARKER_PARTS]

AUDIT_SCOPE = [
    "tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift",
    "scripts/collect-provider-match-candidate.py",
    "tools/driverkit-activation/provider-open-prohibition-gate.json",
    "tools/driverkit-activation/bar-mapping-prohibition-gate.json",
    "tools/driverkit-activation/config-write-prohibition-gate.json",
    "tools/driverkit-activation/gpu-command-submission-prohibition-gate.json",
    "tools/driverkit-activation/provider-match-candidate-collector-plan.json",
    "tools/driverkit-activation/provider-match-candidate-summary-gate.json",
    "tools/driverkit-activation/dext-load-provider-match-proof-schema.json",
    "tools/driverkit-activation/activation-execution-gate.json",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def scan_file(path: Path, markers: list[str], family: str) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for marker in markers:
        if marker in text:
            hits.append({"path": str(path), "marker_family": family})
    return hits

def main() -> int:
    parser = argparse.ArgumentParser(description="Check firmware/reset/display-init prohibition gate.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "firmware-reset-display-init-prohibition-gate.md"
    gate_path = root / "tools" / "driverkit-activation" / "firmware-reset-display-init-prohibition-gate.json"
    gpu_gate_path = root / "tools" / "driverkit-activation" / "gpu-command-submission-prohibition-gate.json"
    config_gate_path = root / "tools" / "driverkit-activation" / "config-write-prohibition-gate.json"
    bar_gate_path = root / "tools" / "driverkit-activation" / "bar-mapping-prohibition-gate.json"
    provider_gate_path = root / "tools" / "driverkit-activation" / "provider-open-prohibition-gate.json"
    activation_gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("firmware_reset_display_gate_json_exists", gate_path.exists(), str(gate_path)),
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

    gate = read_json(gate_path)
    gpu_gate = read_json(gpu_gate_path)
    config_gate = read_json(config_gate_path)
    bar_gate = read_json(bar_gate_path)
    provider_gate = read_json(provider_gate_path)
    activation_gate = read_json(activation_gate_path)

    checks.append(make_check("gate_schema_matches", bool(gate and gate.get("schema") == "h1mekartx.firmware_reset_display_init_prohibition_gate.v1"), "gate schema"))
    checks.append(make_check("gate_firmware_forbidden", bool(gate and gate.get("firmware_load_forbidden") is True), "firmware load forbidden"))
    checks.append(make_check("gate_reset_forbidden", bool(gate and gate.get("gpu_reset_forbidden") is True), "GPU reset forbidden"))
    checks.append(make_check("gate_display_init_forbidden", bool(gate and gate.get("display_engine_init_forbidden") is True), "display init forbidden"))
    checks.append(make_check("gate_state_enforced", bool(gate and gate.get("firmware_reset_display_init_prohibition_state") == "ENFORCED"), "ENFORCED"))
    checks.append(make_check("gpu_gate_enforced", bool(gpu_gate and gpu_gate.get("gpu_command_submission_prohibition_state") == "ENFORCED"), "GPU command gate enforced"))
    checks.append(make_check("config_gate_enforced", bool(config_gate and config_gate.get("config_write_prohibition_state") == "ENFORCED"), "config gate enforced"))
    checks.append(make_check("bar_gate_enforced", bool(bar_gate and bar_gate.get("bar_mapping_prohibition_state") == "ENFORCED"), "BAR gate enforced"))
    checks.append(make_check("provider_gate_enforced", bool(provider_gate and provider_gate.get("provider_open_prohibition_state") == "ENFORCED"), "provider open enforced"))
    checks.append(make_check("activation_gate_blocks_execute", bool(activation_gate and activation_gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))

    missing_scope = []
    firmware_hits = []
    reset_hits = []
    display_init_hits = []
    for rel in AUDIT_SCOPE:
        p = root / rel
        if not p.exists():
            missing_scope.append(rel)
            continue
        firmware_hits.extend(scan_file(p, FIRMWARE_MARKERS, "firmware_load"))
        reset_hits.extend(scan_file(p, RESET_MARKERS, "gpu_reset"))
        display_init_hits.extend(scan_file(p, DISPLAY_INIT_MARKERS, "display_init"))

    checks.append(make_check("audit_scope_files_exist", not missing_scope, ",".join(missing_scope)))
    checks.append(make_check("no_forbidden_firmware_markers", not firmware_hits, json.dumps(firmware_hits, sort_keys=True)))
    checks.append(make_check("no_forbidden_reset_markers", not reset_hits, json.dumps(reset_hits, sort_keys=True)))
    checks.append(make_check("no_forbidden_display_init_markers", not display_init_hits, json.dumps(display_init_hits, sort_keys=True)))

    manifest = gate.get("target_pci_provider_matching_manifest", {}) if gate else {}
    checks.extend([
        make_check("target_vendor_id_matches", manifest.get("vendor_id") == "0x10de", "0x10de"),
        make_check("target_device_id_matches", manifest.get("device_id") == "0x2f04", "0x2f04"),
        make_check("target_iopci_match_matches", manifest.get("io_pci_match") == "0x2f0410de", "0x2f0410de"),
        make_check("expected_provider_class_matches", manifest.get("expected_provider_class") == "IOPCIDevice", "IOPCIDevice"),
        make_check("expected_driver_family_matches", manifest.get("expected_driver_family") == "PCIDriverKit", "PCIDriverKit"),
    ])

    for name, obj in [
        ("gate", gate),
        ("gpu_gate", gpu_gate),
        ("config_gate", config_gate),
        ("bar_gate", bar_gate),
        ("provider_gate", provider_gate),
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
        "firmware_load_attempted",
        "gpu_reset_attempted",
        "framebuffer_init_attempted",
        "display_engine_init_attempted",
        "modeset_attempted",
        "scanout_init_attempted",
    ]:
        checks.append(make_check(
            f"gate_{field}_false",
            bool(gate and gate.get(field) is False),
            f"{field}=false",
        ))

    for field in [
        "provider_match_proof_state",
        "dext_load_proof_state",
        "real_gpu_command_execution_proof_state",
        "ui_compositor_proof_state",
        "metal_proof_state",
    ]:
        checks.append(make_check(
            f"gate_{field}_not_attempted",
            bool(gate and gate.get(field) == "NOT_ATTEMPTED"),
            f"{field}=NOT_ATTEMPTED",
        ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_READY" if failed_count == 0 else "FAIL_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE",
        "secondary_classification": "CLASSIFICATION_GPU_COMMAND_SUBMISSION_PROHIBITION_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 31 firmware/reset/display-init prohibition gate",
        "firmware_reset_display_init_prohibition_gate_only": True,
        "firmware_load_forbidden": True,
        "gpu_reset_forbidden": True,
        "framebuffer_init_forbidden": True,
        "display_engine_init_forbidden": True,
        "modeset_forbidden": True,
        "scanout_init_forbidden": True,
        "gpu_command_submission_forbidden": True,
        "configuration_writes_forbidden": True,
        "bar_mapping_forbidden": True,
        "bar_mmio_mutation_forbidden": True,
        "provider_open_forbidden": True,
        "provider_match_proof_not_claimed": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
        "firmware_reset_display_init_prohibition_state": "ENFORCED",
        "gpu_command_submission_prohibition_state": "ENFORCED",
        "config_write_prohibition_state": "ENFORCED",
        "bar_mapping_prohibition_state": "ENFORCED",
        "provider_open_prohibition_state": "ENFORCED",
        "firmware_hits": firmware_hits,
        "reset_hits": reset_hits,
        "display_init_hits": display_init_hits,
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
        "modeset_attempted": False,
        "scanout_init_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_state": "BLOCKED_UNTIL_REAL_GPU_COMMAND_AND_COMPOSITOR_ATTRIBUTION_EVIDENCE",
        "checks": checks,
    }

    json_path = out_dir / "firmware-reset-display-init-prohibition-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Firmware / Reset / Display Init Prohibition Gate Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Firmware Load Forbidden: `{report['firmware_load_forbidden']}`
- GPU Reset Forbidden: `{report['gpu_reset_forbidden']}`
- Framebuffer Init Forbidden: `{report['framebuffer_init_forbidden']}`
- Display Engine Init Forbidden: `{report['display_engine_init_forbidden']}`
- Modeset Forbidden: `{report['modeset_forbidden']}`
- Scanout Init Forbidden: `{report['scanout_init_forbidden']}`
- GPU Command Submission Forbidden: `{report['gpu_command_submission_forbidden']}`
- Configuration Writes Forbidden: `{report['configuration_writes_forbidden']}`
- BAR Mapping Forbidden: `{report['bar_mapping_forbidden']}`
- Provider Open Forbidden: `{report['provider_open_forbidden']}`
- Execute Mode Still Blocked: `{report['execute_mode_still_blocked']}`
- Ledger Ready Required For Execute: `{report['ledger_ready_required_for_execute']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
- Firmware Hits: `{len(firmware_hits)}`
- Reset Hits: `{len(reset_hits)}`
- Display Init Hits: `{len(display_init_hits)}`
- Provider Match Proof State: `{report['provider_match_proof_state']}`
- Dext Load Proof State: `{report['dext_load_proof_state']}`
- Real GPU Command Execution Proof State: `{report['real_gpu_command_execution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Firmware Load Attempted: `{report['firmware_load_attempted']}`
- GPU Reset Attempted: `{report['gpu_reset_attempted']}`
- Framebuffer Init Attempted: `{report['framebuffer_init_attempted']}`
- Display Engine Init Attempted: `{report['display_engine_init_attempted']}`
- Modeset Attempted: `{report['modeset_attempted']}`
- Scanout Init Attempted: `{report['scanout_init_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`
- Dock / Transparency / Blur State: `{report['dock_transparency_blur_state']}`

## Timing

Phase 31 enforces firmware/reset/display-init prohibition.

Firmware/reset/display-init policy remains forbidden until a future separately reviewed phase.

Dock/transparency/blur acceleration proof starts later, after dext load proof, provider match proof, authorized provider access, authorized BAR policy, authorized configuration-write policy, authorized firmware/reset/display-init policy, real GPU command execution, and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase adds firmware/reset/display-init prohibition only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "firmware-reset-display-init-prohibition-gate-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
