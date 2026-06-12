#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.activation_controller_transition_gate_report.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_FILES = {
    "static_contract": "activation-controller-static-contract-report.json",
    "design_stub": "activation-controller-design-stub.json",
    "provider_transition_gate": "provider-match-transition-gate-report.json",
}

EXPECTED_DECISIONS = {
    "static_contract": "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT",
    "design_stub": "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME",
    "provider_transition_gate": "PROVIDER_MATCH_TRANSITION_GATE_NO_GO",
}

FORBIDDEN_NOW = [
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
    "creating DriverKit target",
    "adding dext provider class",
    "adding Info.plist provider match dictionary",
    "installing DriverKit dext",
    "activating DriverKit",
    "requesting device ownership",
    "attaching to PCI provider",
    "querying live provider state",
    "live extension status query",
    "live PCI probing",
    "ioreg collection",
    "system_profiler collection",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission to RTX 5070",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}
    return json.loads(path.read_text())


def target_matches(data: dict[str, Any]) -> bool:
    target = data.get("target") or data.get("expected_target") or {}
    if not isinstance(target, dict):
        return False
    return all(target.get(k) == v for k, v in EXPECTED_TARGET.items())


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def gate(name: str, status: str, blocking: bool, source: str, detail: str) -> dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "blocking": blocking,
        "source": source,
        "detail": detail,
    }


def build_report(input_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}

    for key, filename in INPUT_FILES.items():
        path = input_dir / filename
        data = load_json(path)
        loaded[key] = data

        add_check(checks, f"input_exists:{filename}", path.exists(), "present" if path.exists() else "missing")
        add_check(checks, f"input_loaded:{filename}", bool(data), "loaded" if data else "missing-or-empty")
        add_check(checks, f"decision:{key}", data.get("decision") == EXPECTED_DECISIONS[key], f"decision={data.get('decision')!r}")
        add_check(checks, f"target:{key}", target_matches(data), f"target={(data.get('target') or data.get('expected_target'))!r}")

    static_contract = loaded["static_contract"]
    design_stub = loaded["design_stub"]
    provider_gate = loaded["provider_transition_gate"]

    top_level_false_keys = [
        "activation_controller_runtime_allowed",
        "activation_request_allowed",
        "deactivation_request_allowed",
        "manager_submit_allowed",
        "driverkit_target_creation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]

    for key in top_level_false_keys:
        if key in static_contract:
            add_check(checks, f"static_contract_blocks:{key}", static_contract.get(key) is False, f"value={static_contract.get(key)!r}")
        if key in design_stub:
            add_check(checks, f"design_stub_blocks:{key}", design_stub.get(key) is False, f"value={design_stub.get(key)!r}")

    for key in [
        "provider_work_transition_allowed",
        "driverkit_target_creation_allowed",
        "activation_request_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add_check(checks, f"provider_gate_blocks:{key}", provider_gate.get(key) is False, f"value={provider_gate.get(key)!r}")

    add_check(checks, "static_contract_zero_failed", static_contract.get("failed_count") == 0, f"failed_count={static_contract.get('failed_count')!r}")
    add_check(checks, "provider_gate_zero_failed_validation", provider_gate.get("failed_validation_count") == 0, f"failed_validation_count={provider_gate.get('failed_validation_count')!r}")
    add_check(checks, "provider_gate_zero_failed_gate", provider_gate.get("failed_gate_count") == 0, f"failed_gate_count={provider_gate.get('failed_gate_count')!r}")
    add_check(checks, "provider_gate_has_no_go", provider_gate.get("no_go_gate_count", 0) > 0, f"no_go_gate_count={provider_gate.get('no_go_gate_count')!r}")
    add_check(checks, "provider_gate_has_blocking", provider_gate.get("blocking_gate_count", 0) > 0, f"blocking_gate_count={provider_gate.get('blocking_gate_count')!r}")
    add_check(checks, "design_stub_has_blocking_preconditions", design_stub.get("blocking_precondition_gate_count", 0) > 0, f"value={design_stub.get('blocking_precondition_gate_count')!r}")

    transition_gates = [
        gate(
            "ACT-001 static contract validator",
            "PASS" if static_contract.get("decision") == "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT" and static_contract.get("failed_count") == 0 else "FAIL",
            False,
            "activation-controller-static-contract",
            "Static contract validator must pass.",
        ),
        gate(
            "ACT-002 design stub no-runtime decision",
            "PASS" if design_stub.get("decision") == "ACTIVATION_CONTROLLER_DESIGN_STUB_READY_NO_RUNTIME" else "FAIL",
            False,
            "activation-controller-design-stub",
            "Design stub must remain no-runtime.",
        ),
        gate(
            "ACT-003 provider-match transition gate",
            "NO_GO",
            True,
            "provider-match-transition-gate-report",
            "Provider-match transition remains NO-GO.",
        ),
        gate(
            "ACT-004 activation runtime",
            "NO_GO",
            True,
            "activation-controller-design-stub",
            "Activation runtime remains blocked.",
        ),
        gate(
            "ACT-005 entitlement and bundle evidence",
            "NO_GO",
            True,
            "provider-match-transition-gate-report",
            "DriverKit, PCI transport, and bundle identity evidence are still required outside the repository.",
        ),
        gate(
            "ACT-006 rollback and recovery evidence",
            "NO_GO",
            True,
            "activation-controller-design-stub",
            "Rollback and recovery runbook review remains required.",
        ),
        gate(
            "ACT-007 hardware access boundary",
            "PASS" if design_stub.get("hardware_access_allowed") is False and provider_gate.get("hardware_access_allowed") is False else "FAIL",
            False,
            "design-stub/provider-transition",
            "PCI/BAR/MMIO and RTX 5070 acceleration paths remain blocked.",
        ),
    ]

    failed_validation_count = sum(1 for item in checks if not item["passed"])
    passed_validation_count = len(checks) - failed_validation_count
    failed_gate_count = sum(1 for item in transition_gates if item["status"] == "FAIL")
    pass_gate_count = sum(1 for item in transition_gates if item["status"] == "PASS")
    no_go_gate_count = sum(1 for item in transition_gates if item["status"] == "NO_GO")
    blocking_gate_count = sum(1 for item in transition_gates if item["blocking"])

    activation_runtime_transition_allowed = (
        failed_validation_count == 0
        and failed_gate_count == 0
        and no_go_gate_count == 0
        and blocking_gate_count == 0
    )

    decision = (
        "ACTIVATION_CONTROLLER_TRANSITION_GATE_GO"
        if activation_runtime_transition_allowed
        else "ACTIVATION_CONTROLLER_TRANSITION_GATE_NO_GO"
    )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "target": EXPECTED_TARGET,
        "decision": decision,
        "plain_answer": "Do not advance to activation runtime yet.",
        "full_metal_goal": True,
        "research_continues": True,
        "activation_runtime_transition_allowed": activation_runtime_transition_allowed,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "passed_validation_count": passed_validation_count,
        "failed_validation_count": failed_validation_count,
        "gate_count": len(transition_gates),
        "pass_gate_count": pass_gate_count,
        "no_go_gate_count": no_go_gate_count,
        "blocking_gate_count": blocking_gate_count,
        "failed_gate_count": failed_gate_count,
        "validation_checks": checks,
        "transition_gates": transition_gates,
        "input_files": INPUT_FILES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 49 should add a host-app activation UI plan that remains UI-only and does not create request objects, submit manager requests, create DriverKit targets, attach providers, request device ownership, access PCI config space, map BAR memory, or perform MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "local_json_validation_only": True,
            "transition_report_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "driverkit_activation": False,
            "driverkit_dext_installation": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
            "live_provider_state_query": False,
            "live_extension_status_query": False,
            "live_pci_probing": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    validation_rows = []
    for item in report["validation_checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        validation_rows.append(f"| `{item['name']}` | {status} | {detail} |")

    gate_rows = []
    for item in report["transition_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | `{item['status']}` | `{item['blocking']}` | `{item['source']}` | {item['detail']} |"
        )

    forbidden_lines = [f"- {item}" for item in report["forbidden_now"]]

    return "\n".join(
        [
            "# Activation-controller Transition Gate Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Plain answer: {report['plain_answer']}",
            "",
            f"Full Metal goal: `{report['full_metal_goal']}`",
            "",
            f"Research continues: `{report['research_continues']}`",
            "",
            f"Activation runtime transition allowed: `{report['activation_runtime_transition_allowed']}`",
            "",
            f"Activation-controller runtime allowed: `{report['activation_controller_runtime_allowed']}`",
            "",
            f"Activation request allowed: `{report['activation_request_allowed']}`",
            "",
            f"Deactivation request allowed: `{report['deactivation_request_allowed']}`",
            "",
            f"Manager submit allowed: `{report['manager_submit_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{report['driverkit_target_creation_allowed']}`",
            "",
            f"Provider attach allowed: `{report['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{report['device_ownership_allowed']}`",
            "",
            f"Hardware access allowed: `{report['hardware_access_allowed']}`",
            "",
            f"Passed validation count: `{report['passed_validation_count']}`",
            "",
            f"Failed validation count: `{report['failed_validation_count']}`",
            "",
            f"Gate count: `{report['gate_count']}`",
            "",
            f"PASS gate count: `{report['pass_gate_count']}`",
            "",
            f"NO-GO gate count: `{report['no_go_gate_count']}`",
            "",
            f"Blocking gate count: `{report['blocking_gate_count']}`",
            "",
            f"Failed gate count: `{report['failed_gate_count']}`",
            "",
            "## Target",
            "",
            f"- Vendor ID: `{report['target']['vendor_id']}`",
            f"- Device ID: `{report['target']['device_id']}`",
            f"- IOPCIMatch: `{report['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{report['target']['subsystem_vendor_id']}`",
            f"- Subsystem ID: `{report['target']['subsystem_id']}`",
            "",
            "## Transition Gates",
            "",
            "| Gate | Status | Blocking | Source | Detail |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Validation Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *validation_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is transition-report-only and local-JSON-validation-only.",
            "",
            "It does not create activation request objects, create deactivation request objects, call extension manager submit, implement an activation controller runtime path, create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate activation-controller transition gate report.")
    parser.add_argument("--input-dir", default=".", help="Directory containing local generated JSON reports.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(input_dir)

    json_path = out_dir / "activation-controller-transition-gate-report.json"
    md_path = out_dir / "activation-controller-transition-gate-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_validation_count"] == 0 and report["failed_gate_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
