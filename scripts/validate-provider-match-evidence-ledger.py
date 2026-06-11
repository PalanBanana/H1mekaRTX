#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_ledger_validator.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_FILES = {
    "ledger": "provider-match-evidence-ledger.json",
    "spec": "provider-match-dry-run-spec.json",
    "checklist": "entitlement-evidence-checklist.json",
    "readiness": "no-hardware-activation-readiness-review.json",
}

EXPECTED_DECISIONS = {
    "ledger": "PROVIDER_MATCH_EVIDENCE_LEDGER_READY_BLOCKED_ON_USER_EVIDENCE",
    "spec": "PROVIDER_MATCH_DRY_RUN_SPEC_READY",
    "checklist": "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE",
    "readiness": "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED",
}

REQUIRED_FALSE_KEYS = [
    "creates_driverkit_target",
    "adds_dext_provider_class",
    "adds_info_plist_provider_match",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "driverkit_activation",
    "driverkit_dext_installation",
    "device_ownership_request",
    "pci_provider_attach",
    "live_provider_state_query",
    "live_extension_status_query",
    "live_pci_probing",
    "runs_ioreg",
    "runs_system_profiler",
    "performs_pci_config_reads",
    "performs_pci_config_writes",
    "performs_mmio_reads",
    "performs_mmio_writes",
    "maps_bar_memory",
    "bar_poking",
    "rtx5070_metal_acceleration_implementation",
    "rtx5070_shader_execution",
    "hardware_command_submission_to_rtx5070",
    "resource_allocation_on_rtx5070",
]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def target_matches(data: dict[str, Any]) -> bool:
    target = data.get("target", {})
    if not isinstance(target, dict):
        return False
    return all(target.get(k) == v for k, v in EXPECTED_TARGET.items())


def safety_dict(data: dict[str, Any]) -> dict[str, Any]:
    sb = data.get("safety_boundary", {})
    return sb if isinstance(sb, dict) else {}


def build_report(input_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    loaded: dict[str, dict[str, Any]] = {}
    for key, filename in INPUT_FILES.items():
        path = input_dir / filename
        data = load_json(path)
        loaded[key] = data

        add_check(checks, f"input_exists:{filename}", path.exists(), "present" if path.exists() else "missing")
        add_check(checks, f"input_json:{filename}", bool(data), "loaded" if data else "missing-or-empty")
        add_check(
            checks,
            f"decision:{key}",
            data.get("decision") == EXPECTED_DECISIONS[key],
            f"decision={data.get('decision')!r}",
        )
        add_check(
            checks,
            f"target:{key}",
            target_matches(data),
            f"target={data.get('target')!r}",
        )

    ledger = loaded["ledger"]
    spec = loaded["spec"]
    checklist = loaded["checklist"]
    readiness = loaded["readiness"]

    add_check(
        checks,
        "ledger_transition_blocked",
        ledger.get("provider_match_transition_allowed") is False,
        f"value={ledger.get('provider_match_transition_allowed')!r}",
    )
    add_check(
        checks,
        "ledger_has_blocking_items",
        ledger.get("blocking_ledger_item_count", 0) > 0,
        f"value={ledger.get('blocking_ledger_item_count')!r}",
    )
    add_check(
        checks,
        "ledger_has_blocking_gates",
        ledger.get("blocking_transition_gate_count", 0) > 0,
        f"value={ledger.get('blocking_transition_gate_count')!r}",
    )

    add_check(
        checks,
        "spec_dry_run_passes",
        spec.get("failed_case_count") == 0,
        f"failed_case_count={spec.get('failed_case_count')!r}",
    )
    decisions = {
        item.get("actual_decision")
        for item in spec.get("dry_run_cases", [])
        if isinstance(item, dict)
    }
    for decision in [
        "MATCH_TARGET_SPEC_ONLY",
        "REJECT_WRONG_VENDOR",
        "REJECT_WRONG_DEVICE",
        "REJECT_WRONG_SUBSYSTEM",
        "REJECT_INCOMPLETE_IDENTITY",
    ]:
        add_check(checks, f"spec_decision:{decision}", decision in decisions, "present" if decision in decisions else "missing")

    add_check(
        checks,
        "checklist_requires_user_evidence",
        checklist.get("required_missing_or_blocked_count", 0) > 0,
        f"value={checklist.get('required_missing_or_blocked_count')!r}",
    )
    add_check(
        checks,
        "readiness_requires_evidence",
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
        add_check(
            checks,
            f"ledger_blocks:{key}",
            ledger.get(key) is False,
            f"value={ledger.get(key)!r}",
        )

    for source_key, data in loaded.items():
        sb = safety_dict(data)
        for safety_key in REQUIRED_FALSE_KEYS:
            if safety_key in sb:
                add_check(
                    checks,
                    f"{source_key}_safety_false:{safety_key}",
                    sb.get(safety_key) is False,
                    f"value={sb.get(safety_key)!r}",
                )

    source_names = {
        item.get("artifact")
        for item in ledger.get("source_artifacts", [])
        if isinstance(item, dict)
    }
    for source in [
        "provider-match-dry-run-spec",
        "entitlement-evidence-checklist",
        "no-hardware-activation-readiness-review",
    ]:
        add_check(
            checks,
            f"ledger_source:{source}",
            source in source_names,
            "present" if source in source_names else "missing",
        )

    categories = {
        item.get("category")
        for item in ledger.get("evidence_ledger", [])
        if isinstance(item, dict)
    }
    for category in [
        "target_identity",
        "entitlement",
        "bundle_identity",
        "wrong_device_prevention",
        "activation_boundary",
        "device_ownership_boundary",
        "hardware_access_boundary",
    ]:
        add_check(
            checks,
            f"ledger_category:{category}",
            category in categories,
            "present" if category in categories else "missing",
        )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "decision": "PASS_PROVIDER_MATCH_LEDGER_VALIDATION" if failed_count == 0 else "FAIL_PROVIDER_MATCH_LEDGER_VALIDATION",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "input_files": INPUT_FILES,
        "expected_target": EXPECTED_TARGET,
        "provider_match_transition_allowed": False,
        "driverkit_target_creation_allowed": False,
        "activation_request_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "safety_boundary": {
            "read_only": True,
            "local_json_validation_only": True,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
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
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    files = [f"- `{name}`: `{filename}`" for name, filename in report["input_files"].items()]

    return "\n".join(
        [
            "# Provider-match Ledger Validator Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Input Files",
            "",
            *files,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This validator consumes local JSON reports only.",
            "",
            "It does not create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, create activation requests, create deactivation requests, call extension manager submit, activate DriverKit, install DriverKit dexts, request device ownership, attach to PCI providers, query live provider state, query live extension status, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate H1mekaRTX provider-match evidence ledger against local generated JSON reports.")
    parser.add_argument("--input-dir", default=".", help="Directory containing local generated JSON reports.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(input_dir)

    json_path = out_dir / "provider-match-ledger-validator-report.json"
    md_path = out_dir / "provider-match-ledger-validator-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
