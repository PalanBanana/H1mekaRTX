#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.ledger_override_hardblock_audit_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_LEDGER_OVERRIDE_HARDBLOCK_AUDIT",
    "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
    "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
    "CLASSIFICATION_STATIC_CONTRACT",
    "LEDGER_OVERRIDE_HARDBLOCK_AUDIT_ONLY: True",
    "OVERRIDE_PATHS_FORBIDDEN: True",
    "FORCE_EXECUTE_FORBIDDEN: True",
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
    "FORBIDDEN_LEDGER_OVERRIDE_MARKERS",
    "FORBIDDEN_RUNTIME_SUBMIT_MARKERS",
    "LEDGER_OVERRIDE_HARDBLOCK_AUDIT_SCOPE",
    "ACTIVATION_EXECUTION_GATE_RULE",
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

FORBIDDEN_OVERRIDE_MARKERS = [
    "--execute",
    "--force",
    "--force-activate",
    "--force-deactivate",
    "--allow-unsafe",
    "--bypass-ledger",
    "--override-ledger",
    "H1MEKARTX_FORCE_EXECUTE",
    "H1MEKARTX_ALLOW_UNSAFE",
    "H1MEKARTX_BYPASS_LEDGER",
    "H1MEKARTX_OVERRIDE_LEDGER",
    "FORCE_ACTIVATION",
    "FORCE_DEACTIVATION",
    "BYPASS_ACTIVATION_GATE",
    "OVERRIDE_ACTIVATION_GATE",
]

FORBIDDEN_RUNTIME_SUBMIT_MARKERS = [
    "OSSystemExtensionManager.shared.submitRequest",
    "submitRequest(",
    "submitRequest:",
    "provider.open",
    "IOServiceOpen",
    "mapDeviceMemory",
    "mapMemory",
    "writeMemory",
    "commandSubmission",
    "submitCommands",
]

AUDIT_SCOPE = [
    # Runtime activation artifacts only.
    # Static checker scripts/reports are excluded because they may contain explanatory
    # blocked execute wording without creating an executable activation path.
    "tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift",
    "tools/driverkit-activation/activation-deactivation-dryrun-plan.json",
    "tools/driverkit-activation/activation-execution-gate.json",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def scan_file(path: Path, markers: list[str]) -> list[dict]:
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for marker in markers:
        if marker in text:
            hits.append({"path": str(path), "marker": marker})
    return hits

def main() -> int:
    parser = argparse.ArgumentParser(description="Audit activation tooling for override or unsafe execute markers.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "ledger-override-hardblock-audit.md"
    audit_manifest_path = root / "tools" / "driverkit-activation" / "ledger-override-hardblock-audit.json"
    gate_path = root / "tools" / "driverkit-activation" / "activation-execution-gate.json"
    ledger_path = root / "tools" / "driverkit-activation" / "activation-prerequisites-ledger.json"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("audit_manifest_exists", audit_manifest_path.exists(), str(audit_manifest_path)),
        make_check("activation_execution_gate_exists", gate_path.exists(), str(gate_path)),
        make_check("activation_prerequisites_ledger_exists", ledger_path.exists(), str(ledger_path)),
    ]

    contract_text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_contract_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in contract_text, token))

    manifest = read_json(audit_manifest_path)
    gate = read_json(gate_path)
    ledger = read_json(ledger_path)

    checks.append(make_check("manifest_schema_matches", bool(manifest and manifest.get("schema") == "h1mekartx.ledger_override_hardblock_audit.v1"), "manifest schema"))
    checks.append(make_check("manifest_audit_only_true", bool(manifest and manifest.get("ledger_override_hardblock_audit_only") is True), "ledger_override_hardblock_audit_only=true"))
    checks.append(make_check("manifest_execute_blocked_true", bool(manifest and manifest.get("execute_mode_still_blocked") is True), "execute_mode_still_blocked=true"))
    checks.append(make_check("gate_decision_block_execute", bool(gate and gate.get("activation_execution_gate_decision") == "BLOCK_EXECUTE"), "BLOCK_EXECUTE"))

    ledger_items = ledger.get("ledger", []) if ledger else []
    required_items = [item for item in ledger_items if item.get("required_for_activation")]
    all_required_ready = bool(required_items) and all(item.get("status") == "READY" for item in required_items)
    checks.append(make_check("ledger_not_all_required_ready", not all_required_ready, "expected hard-block until ledger READY"))

    missing_scope = []
    override_hits = []
    runtime_hits = []
    for rel in AUDIT_SCOPE:
        p = root / rel
        if not p.exists():
            missing_scope.append(rel)
            continue
        override_hits.extend(scan_file(p, FORBIDDEN_OVERRIDE_MARKERS))
        runtime_hits.extend(scan_file(p, FORBIDDEN_RUNTIME_SUBMIT_MARKERS))

    checks.append(make_check("audit_scope_files_exist", not missing_scope, ",".join(missing_scope)))
    checks.append(make_check("no_forbidden_override_markers_in_activation_tooling", not override_hits, json.dumps(override_hits, sort_keys=True)))
    checks.append(make_check("no_forbidden_runtime_submit_markers_in_activation_tooling", not runtime_hits, json.dumps(runtime_hits, sort_keys=True)))

    for name, obj in [("manifest", manifest), ("gate", gate)]:
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

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_LEDGER_OVERRIDE_HARDBLOCK_AUDIT_READY" if failed_count == 0 else "FAIL_LEDGER_OVERRIDE_HARDBLOCK_AUDIT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_LEDGER_OVERRIDE_HARDBLOCK_AUDIT",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_EXECUTION_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 22 ledger override hard-block audit",
        "audit_scope_mode": "runtime_activation_artifacts_only",
        "ledger_override_hardblock_audit_only": True,
        "override_paths_forbidden": True,
        "force_execute_forbidden": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": "BLOCK_EXECUTE",
        "all_required_ledger_items_ready": all_required_ready,
        "override_hits": override_hits,
        "runtime_submit_hits": runtime_hits,
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

    json_path = out_dir / "ledger-override-hardblock-audit-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# Ledger Override Hard-Block Audit Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Scope: `{report['scope']}`
- Execute Mode Still Blocked: `{report['execute_mode_still_blocked']}`
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

## Audit Results

- Override Hits: `{len(override_hits)}`
- Runtime Submit Hits: `{len(runtime_hits)}`

## Timing

Phase 22 adds the hard-block audit only.

Future activation/deactivation execute mode remains blocked until the activation prerequisites ledger is fully READY.

Dock/transparency/blur acceleration proof starts later, after real GPU command execution and compositor attribution evidence.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase audits for ledger override and unsafe execute markers only. It does not activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "ledger-override-hardblock-audit-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
