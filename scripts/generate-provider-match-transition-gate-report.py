#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_transition_gate_report.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_FILES = {
    "validator": "provider-match-ledger-validator-report.json",
    "ledger": "provider-match-evidence-ledger.json",
    "spec": "provider-match-dry-run-spec.json",
    "checklist": "entitlement-evidence-checklist.json",
    "readiness": "no-hardware-activation-readiness-review.json",
}

EXPECTED_DECISIONS = {
    "validator": "PASS_PROVIDER_MATCH_LEDGER_VALIDATION",
    "ledger": "PROVIDER_MATCH_EVIDENCE_LEDGER_READY_BLOCKED_ON_USER_EVIDENCE",
    "spec": "PROVIDER_MATCH_DRY_RUN_SPEC_READY",
    "checklist": "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE",
    "readiness": "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED",
}

FORBIDDEN_NOW = [
    "creating DriverKit target",
    "adding dext provider class",
    "adding Info.plist provider match dictionary",
    "creating activation request objects",
    "creating deactivation request objects",
    "calling extension manager submit",
    "implementing activation controller runtime path",
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


def safety_dict(data: dict[str, Any]) -> dict[str, Any]:
    sb = data.get("safety_boundary", {})
    return sb if isinstance(sb, dict) else {}


def build_gate(name: str, status: str, blocking: bool, source: str, detail: str) -> dict[str, Any]:
    return {
        "gate": name,
        "status": status,
        "blocking": blocking,
        "source": source,
        "detail": detail,
    }


def build_report(input_dir: Path) -> dict[str, Any]:
    validation_checks: list[dict[str, Any]] = []
    loaded: dict[str, dict[str, Any]] = {}

    def add_check(name: str, passed: bool, detail: str) -> None:
        validation_checks.append({"name": name, "passed": bool(passed), "detail": detail})

    for key, filename in INPUT_FILES.items():
        path = input_dir / filename
        data = load_json(path)
        loaded[key] = data

        add_check(f"input_exists:{filename}", path.exists(), "present" if path.exists() else "missing")
        add_check(f"input_loaded:{filename}", bool(data), "loaded" if data else "missing-or-empty")
        add_check(
            f"decision:{key}",
            data.get("decision") == EXPECTED_DECISIONS[key],
            f"decision={data.get('decision')!r}",
        )

    validator = loaded["validator"]
    ledger = loaded["ledger"]
    spec = loaded["spec"]
    checklist = loaded["checklist"]
    readiness = loaded["readiness"]

    for key in ["validator", "ledger", "spec", "checklist", "readiness"]:
        add_check(
            f"target:{key}",
            target_matches(loaded[key]),
            f"target={(loaded[key].get('target') or loaded[key].get('expected_target'))!r}",
        )

    add_check(
        "validator_zero_failed_checks",
        validator.get("failed_count") == 0,
        f"failed_count={validator.get('failed_count')!r}",
    )
    add_check(
        "spec_zero_failed_cases",
        spec.get("failed_case_count") == 0,
        f"failed_case_count={spec.get('failed_case_count')!r}",
    )
    add_check(
        "ledger_transition_blocked",
        ledger.get("provider_match_transition_allowed") is False,
        f"value={ledger.get('provider_match_transition_allowed')!r}",
    )
    add_check(
        "checklist_user_evidence_required",
        checklist.get("required_missing_or_blocked_count", 0) > 0,
        f"value={checklist.get('required_missing_or_blocked_count')!r}",
    )
    add_check(
        "readiness_no_go_required",
        readiness.get("required_no_go_count", 0) > 0,
        f"value={readiness.get('required_no_go_count')!r}",
    )

    for key in [
        "driverkit_target_creation_allowed",
        "activation_request_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add_check(f"ledger_blocks:{key}", ledger.get(key) is False, f"value={ledger.get(key)!r}")

    gates = [
        build_gate(
            "PMT-001 exact RTX 5070 identity",
            "PASS" if all(target_matches(loaded[k]) for k in loaded) else "FAIL",
            False,
            "all local JSON inputs",
            "All local inputs must agree on vendor/device/IOPCIMatch/subsystem identity.",
        ),
        build_gate(
            "PMT-002 provider-match dry-run cases",
            "PASS" if spec.get("failed_case_count") == 0 else "FAIL",
            False,
            "provider-match-dry-run-spec",
            "All dry-run cases must pass and wrong-device cases must reject.",
        ),
        build_gate(
            "PMT-003 ledger validator",
            "PASS" if validator.get("decision") == "PASS_PROVIDER_MATCH_LEDGER_VALIDATION" and validator.get("failed_count") == 0 else "FAIL",
            False,
            "provider-match-ledger-validator",
            "The local provider-match evidence ledger validator must pass.",
        ),
        build_gate(
            "PMT-004 DriverKit entitlement evidence",
            "NO_GO",
            True,
            "entitlement-evidence-checklist",
            "User-private DriverKit entitlement evidence is still required outside the repository.",
        ),
        build_gate(
            "PMT-005 PCI transport entitlement evidence",
            "NO_GO",
            True,
            "entitlement-evidence-checklist",
            "User-private PCI transport entitlement evidence is still required outside the repository.",
        ),
        build_gate(
            "PMT-006 bundle identity evidence",
            "NO_GO",
            True,
            "entitlement-evidence-checklist",
            "Host app and driver extension bundle identity evidence is still required outside the repository.",
        ),
        build_gate(
            "PMT-007 activation boundary",
            "PASS" if ledger.get("activation_request_allowed") is False else "FAIL",
            False,
            "no-hardware-activation-readiness-review",
            "Activation request and manager submit paths remain blocked.",
        ),
        build_gate(
            "PMT-008 provider attach and device ownership boundary",
            "PASS" if ledger.get("provider_attach_allowed") is False and ledger.get("device_ownership_allowed") is False else "FAIL",
            False,
            "provider-match-evidence-ledger",
            "Provider attach and device ownership paths remain blocked.",
        ),
        build_gate(
            "PMT-009 hardware access boundary",
            "PASS" if ledger.get("hardware_access_allowed") is False else "FAIL",
            False,
            "provider-match-evidence-ledger",
            "PCI config, BAR, MMIO, firmware, display, framebuffer, and reset paths remain blocked.",
        ),
    ]

    failed_validation_count = sum(1 for item in validation_checks if not item["passed"])
    passed_validation_count = len(validation_checks) - failed_validation_count

    blocking_gate_count = sum(1 for gate in gates if gate["blocking"])
    failed_gate_count = sum(1 for gate in gates if gate["status"] == "FAIL")
    pass_gate_count = sum(1 for gate in gates if gate["status"] == "PASS")
    no_go_gate_count = sum(1 for gate in gates if gate["status"] == "NO_GO")

    provider_work_transition_allowed = (
        failed_validation_count == 0
        and failed_gate_count == 0
        and blocking_gate_count == 0
        and no_go_gate_count == 0
    )

    decision = (
        "PROVIDER_MATCH_TRANSITION_GATE_GO"
        if provider_work_transition_allowed
        else "PROVIDER_MATCH_TRANSITION_GATE_NO_GO"
    )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "target": EXPECTED_TARGET,
        "decision": decision,
        "plain_answer": "Do not advance to DriverKit/provider work yet.",
        "full_metal_goal": True,
        "research_continues": True,
        "provider_work_transition_allowed": provider_work_transition_allowed,
        "driverkit_target_creation_allowed": False,
        "activation_request_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "passed_validation_count": passed_validation_count,
        "failed_validation_count": failed_validation_count,
        "gate_count": len(gates),
        "pass_gate_count": pass_gate_count,
        "no_go_gate_count": no_go_gate_count,
        "blocking_gate_count": blocking_gate_count,
        "failed_gate_count": failed_gate_count,
        "validation_checks": validation_checks,
        "transition_gates": gates,
        "input_files": INPUT_FILES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 46 should add an activation-controller design stub that remains design-only and does not create request objects, submit manager requests, create DriverKit targets, attach providers, request device ownership, access PCI config space, map BAR memory, or perform MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "local_json_validation_only": True,
            "transition_report_only": True,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "implements_activation_controller_runtime_path": False,
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
    for gate in report["transition_gates"]:
        gate_rows.append(
            f"| `{gate['gate']}` | `{gate['status']}` | `{gate['blocking']}` | `{gate['source']}` | {gate['detail']} |"
        )

    forbidden_lines = [f"- {item}" for item in report["forbidden_now"]]

    return "\n".join(
        [
            "# Provider-match Transition Gate Report",
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
            f"Provider work transition allowed: `{report['provider_work_transition_allowed']}`",
            "",
            f"DriverKit target creation allowed: `{report['driverkit_target_creation_allowed']}`",
            "",
            f"Activation request allowed: `{report['activation_request_allowed']}`",
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
            "It does not create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, create activation request objects, create deactivation request objects, call extension manager submit, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX provider-match transition gate report.")
    parser.add_argument("--input-dir", default=".", help="Directory containing local generated JSON reports.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(input_dir)

    json_path = out_dir / "provider-match-transition-gate-report.json"
    md_path = out_dir / "provider-match-transition-gate-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_validation_count"] == 0 and report["failed_gate_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
