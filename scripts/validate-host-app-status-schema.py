#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_status_schema_validator.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

INPUT_FILES = {
    "status_schema": "host-app-status-schema.json",
    "ui_plan": "host-app-activation-ui-plan.json",
    "activation_transition": "activation-controller-transition-gate-report.json",
    "activation_contract": "activation-controller-static-contract-report.json",
    "provider_transition": "provider-match-transition-gate-report.json",
    "entitlement_checklist": "entitlement-evidence-checklist.json",
    "readiness_review": "no-hardware-activation-readiness-review.json",
}

EXPECTED_DECISIONS = {
    "status_schema": "HOST_APP_STATUS_SCHEMA_READY_LOCAL_REPORT_ONLY",
    "ui_plan": "HOST_APP_ACTIVATION_UI_PLAN_READY_UI_ONLY",
    "activation_transition": "ACTIVATION_CONTROLLER_TRANSITION_GATE_NO_GO",
    "activation_contract": "PASS_ACTIVATION_CONTROLLER_STATIC_CONTRACT",
    "provider_transition": "PROVIDER_MATCH_TRANSITION_GATE_NO_GO",
    "entitlement_checklist": "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE",
    "readiness_review": "NO_HARDWARE_ACTIVATION_NOT_READY_EVIDENCE_REQUIRED",
}

REQUIRED_STATUS_FIELDS = [
    "project_status",
    "provider_match_status",
    "activation_status",
    "entitlement_evidence_status",
    "bundle_identity_status",
    "hardware_access_status",
    "last_local_report_generated_at_utc",
    "status_source",
]

EXPECTED_STATUS_PROJECTION = {
    "project_status": "RESEARCH_ONLY",
    "provider_match_status": "NO_GO",
    "activation_status": "NO_GO",
    "entitlement_evidence_status": "NEEDS_USER_EVIDENCE",
    "bundle_identity_status": "NEEDS_USER_EVIDENCE",
    "hardware_access_status": "BLOCKED",
    "last_local_report_generated_at_utc": None,
    "status_source": "LOCAL_GENERATED_REPORTS_ONLY",
}

REQUIRED_FALSE_KEYS = [
    "live_system_queries_allowed",
    "runtime_buttons_enabled",
    "activation_runtime_transition_allowed",
    "activation_controller_runtime_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
]

REQUIRED_FALSE_SAFETY = [
    "runtime_buttons_enabled",
    "live_system_queries",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "implements_activation_controller_runtime_path",
    "creates_driverkit_target",
    "adds_dext_provider_class",
    "adds_info_plist_provider_match",
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
    if not path.exists() or not path.is_file():
        return {}
    return json.loads(path.read_text())


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def target_matches(data: dict[str, Any]) -> bool:
    target = data.get("target") or data.get("expected_target") or {}
    if not isinstance(target, dict):
        return False
    return all(target.get(k) == v for k, v in EXPECTED_TARGET.items())


def derive_status_projection(loaded: dict[str, dict[str, Any]]) -> dict[str, Any]:
    status_schema = loaded.get("status_schema", {})
    provider_transition = loaded.get("provider_transition", {})
    activation_transition = loaded.get("activation_transition", {})
    entitlement = loaded.get("entitlement_checklist", {})
    readiness = loaded.get("readiness_review", {})

    provider_no_go = provider_transition.get("decision") == "PROVIDER_MATCH_TRANSITION_GATE_NO_GO"
    activation_no_go = activation_transition.get("decision") == "ACTIVATION_CONTROLLER_TRANSITION_GATE_NO_GO"
    entitlement_needs_evidence = entitlement.get("required_missing_or_blocked_count", 0) > 0
    readiness_no_go = readiness.get("required_no_go_count", 0) > 0

    return {
        "project_status": "RESEARCH_ONLY",
        "provider_match_status": "NO_GO" if provider_no_go else "READY_FOR_REVIEW",
        "activation_status": "NO_GO" if activation_no_go else "READY_FOR_REVIEW",
        "entitlement_evidence_status": "NEEDS_USER_EVIDENCE" if entitlement_needs_evidence else "READY_FOR_REVIEW",
        "bundle_identity_status": "NEEDS_USER_EVIDENCE" if entitlement_needs_evidence else "READY_FOR_REVIEW",
        "hardware_access_status": "BLOCKED" if readiness_no_go else "READY_FOR_REVIEW",
        "last_local_report_generated_at_utc": status_schema.get("generated_at_utc"),
        "status_source": "LOCAL_GENERATED_REPORTS_ONLY",
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

    status_schema = loaded["status_schema"]

    fields = status_schema.get("status_fields", [])
    field_names = {item.get("field") for item in fields if isinstance(item, dict)}
    for field in REQUIRED_STATUS_FIELDS:
        add_check(checks, f"required_status_field:{field}", field in field_names, "present" if field in field_names else "missing")

    for key in REQUIRED_FALSE_KEYS:
        add_check(checks, f"schema_blocks:{key}", status_schema.get(key) is False, f"value={status_schema.get(key)!r}")

    sb = status_schema.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_schema_only", sb.get("schema_only") is True, f"value={sb.get('schema_only')!r}")
    add_check(checks, "safety_local_report_only", sb.get("local_report_only") is True, f"value={sb.get('local_report_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    projection = derive_status_projection(loaded)

    for key, expected in EXPECTED_STATUS_PROJECTION.items():
        if key == "last_local_report_generated_at_utc":
            add_check(checks, f"status_projection:{key}", projection.get(key) is not None, f"value={projection.get(key)!r}")
        else:
            add_check(checks, f"status_projection:{key}", projection.get(key) == expected, f"value={projection.get(key)!r}")

    add_check(
        checks,
        "activation_transition_stays_no_go",
        loaded["activation_transition"].get("activation_runtime_transition_allowed") is False,
        f"value={loaded['activation_transition'].get('activation_runtime_transition_allowed')!r}",
    )
    add_check(
        checks,
        "provider_transition_stays_no_go",
        loaded["provider_transition"].get("provider_work_transition_allowed") is False,
        f"value={loaded['provider_transition'].get('provider_work_transition_allowed')!r}",
    )
    add_check(
        checks,
        "ui_plan_stays_ui_only",
        loaded["ui_plan"].get("ui_only") is True and loaded["ui_plan"].get("runtime_buttons_enabled") is False,
        f"ui_only={loaded['ui_plan'].get('ui_only')!r}, runtime_buttons_enabled={loaded['ui_plan'].get('runtime_buttons_enabled')!r}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "target": EXPECTED_TARGET,
        "decision": "PASS_HOST_APP_STATUS_SCHEMA_VALIDATION" if failed_count == 0 else "FAIL_HOST_APP_STATUS_SCHEMA_VALIDATION",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "status_projection": projection,
        "expected_status_projection": EXPECTED_STATUS_PROJECTION,
        "validation_checks": checks,
        "input_files": INPUT_FILES,
        "host_app_status_schema_valid": failed_count == 0,
        "local_report_only": True,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "activation_runtime_transition_allowed": False,
        "activation_controller_runtime_allowed": False,
        "activation_request_allowed": False,
        "deactivation_request_allowed": False,
        "manager_submit_allowed": False,
        "driverkit_target_creation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "hardware_access_allowed": False,
        "safety_boundary": {
            "read_only": True,
            "local_json_validation_only": True,
            "schema_validation_only": True,
            "local_report_only": True,
            "live_system_queries": False,
            "runtime_buttons_enabled": False,
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
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["validation_checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Host-app Status Schema Validator Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Host-app status schema valid: `{report['host_app_status_schema_valid']}`",
            "",
            f"Local report only: `{report['local_report_only']}`",
            "",
            f"Live system queries allowed: `{report['live_system_queries_allowed']}`",
            "",
            f"Runtime buttons enabled: `{report['runtime_buttons_enabled']}`",
            "",
            f"Activation runtime transition allowed: `{report['activation_runtime_transition_allowed']}`",
            "",
            f"Activation request allowed: `{report['activation_request_allowed']}`",
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
            "## Status Projection",
            "",
            "```json",
            json.dumps(report["status_projection"], indent=2, sort_keys=True),
            "```",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This validator consumes local generated JSON only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, implement activation runtime, create DriverKit targets, attach providers, request device ownership, run live PCI tools, access PCI config space, map BAR memory, perform MMIO access, execute RTX 5070 shaders, submit hardware commands, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate host-app status schema against local generated reports.")
    parser.add_argument("--input-dir", default=".", help="Directory containing local generated JSON reports.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(input_dir)

    json_path = out_dir / "host-app-status-schema-validator-report.json"
    md_path = out_dir / "host-app-status-schema-validator-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
