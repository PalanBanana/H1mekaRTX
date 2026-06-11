#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.local_host_report_renderer.v1"

REQUIRED_TOP_LEVEL = [
    "schema",
    "decision",
    "generatedAtUTC",
    "target",
    "hostState",
    "plannedPanels",
    "safetyBoundary",
]

TARGET_FIELDS = [
    "gpu",
    "vendorID",
    "deviceID",
    "iopcimatch",
    "subsystemVendorID",
    "subsystemID",
]

HOST_STATE_FIELDS = [
    "hostSkeletonPresent",
    "activationControllerImplemented",
    "driverExtensionTargetIncluded",
    "activationRequestSubmitted",
    "deactivationRequestSubmitted",
    "managerSubmitCalled",
    "deviceOwnershipRequested",
    "metalReferenceWorkloadLauncherPlanned",
]

SAFETY_BOUNDARY_FIELDS = [
    "existingSystemMetalDeviceValidationOnly",
    "rtx5070MetalAccelerationImplementation",
    "rtx5070ShaderExecution",
    "hardwareCommandSubmission",
    "rtx5070ResourceAllocation",
    "pciConfigReads",
    "pciConfigWrites",
    "mmioReads",
    "mmioWrites",
    "barMapping",
    "barPoking",
    "driverActivation",
    "systemExtensionActivationRequest",
    "systemExtensionDeactivationRequest",
    "systemExtensionManagerSubmit",
    "deviceOwnershipRequest",
    "firmwareLoading",
    "gspInitialization",
    "displayEngineInitialization",
    "framebufferInitialization",
    "gpuResetLogic",
]

FORBIDDEN_TRUE_FLAGS = [
    "rtx5070MetalAccelerationImplementation",
    "rtx5070ShaderExecution",
    "hardwareCommandSubmission",
    "rtx5070ResourceAllocation",
    "pciConfigReads",
    "pciConfigWrites",
    "mmioReads",
    "mmioWrites",
    "barMapping",
    "barPoking",
    "driverActivation",
    "systemExtensionActivationRequest",
    "systemExtensionDeactivationRequest",
    "systemExtensionManagerSubmit",
    "deviceOwnershipRequest",
    "firmwareLoading",
    "gspInitialization",
    "displayEngineInitialization",
    "framebufferInitialization",
    "gpuResetLogic",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(errors="replace"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object at top level: {path}")

    return data


def bool_cell(value: Any) -> str:
    if value is True:
        return "PASS_TRUE"
    if value is False:
        return "PASS_FALSE"
    if value is None:
        return "MISSING"
    return str(value)


def build_validation(data: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "detail": detail,
            }
        )

    for field in REQUIRED_TOP_LEVEL:
        add(
            f"top_level:{field}",
            field in data,
            "present" if field in data else "missing",
        )

    target = data.get("target", {})
    if not isinstance(target, dict):
        target = {}

    for field in TARGET_FIELDS:
        add(
            f"target:{field}",
            field in target,
            "present" if field in target else "missing",
        )

    host_state = data.get("hostState", {})
    if not isinstance(host_state, dict):
        host_state = {}

    for field in HOST_STATE_FIELDS:
        add(
            f"hostState:{field}",
            field in host_state,
            f"value={host_state.get(field)!r}" if field in host_state else "missing",
        )

    safety = data.get("safetyBoundary", {})
    if not isinstance(safety, dict):
        safety = {}

    for field in SAFETY_BOUNDARY_FIELDS:
        add(
            f"safetyBoundary:{field}",
            field in safety,
            f"value={safety.get(field)!r}" if field in safety else "missing",
        )

    for field in FORBIDDEN_TRUE_FLAGS:
        add(
            f"forbidden_flag_false:{field}",
            safety.get(field) is False,
            f"value={safety.get(field)!r}",
        )

    add(
        "safe_existing_system_metal_device_validation_only",
        safety.get("existingSystemMetalDeviceValidationOnly") is True,
        f"value={safety.get('existingSystemMetalDeviceValidationOnly')!r}",
    )

    add(
        "planned_panels_is_list",
        isinstance(data.get("plannedPanels"), list),
        f"type={type(data.get('plannedPanels')).__name__}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
    }


def render_markdown(input_path: Path, data: dict[str, Any], validation: dict[str, Any]) -> str:
    target = data.get("target", {}) if isinstance(data.get("target"), dict) else {}
    host_state = data.get("hostState", {}) if isinstance(data.get("hostState"), dict) else {}
    safety = data.get("safetyBoundary", {}) if isinstance(data.get("safetyBoundary"), dict) else {}
    panels = data.get("plannedPanels", [])
    if not isinstance(panels, list):
        panels = []

    target_rows = [
        f"| `{field}` | `{target.get(field, '—')}` |"
        for field in TARGET_FIELDS
    ]

    host_rows = [
        f"| `{field}` | `{bool_cell(host_state.get(field))}` |"
        for field in HOST_STATE_FIELDS
    ]

    safety_rows = [
        f"| `{field}` | `{bool_cell(safety.get(field))}` |"
        for field in SAFETY_BOUNDARY_FIELDS
    ]

    panel_lines = [f"- `{panel}`" for panel in panels] or ["- `—`"]

    decision = "PASS_LOCAL_HOST_REPORT_RENDERED" if validation["failed_count"] == 0 else "FAIL_LOCAL_HOST_REPORT_RENDER_INVALID"

    return "\n".join(
        [
            "# Local Host Status Report",
            "",
            f"Rendered UTC: `{datetime.now(timezone.utc).isoformat()}`",
            "",
            f"Input: `{input_path}`",
            "",
            f"Renderer decision: `{decision}`",
            "",
            f"Source schema: `{data.get('schema', '—')}`",
            "",
            f"Source decision: `{data.get('decision', '—')}`",
            "",
            f"Source generated UTC: `{data.get('generatedAtUTC', '—')}`",
            "",
            f"Passed checks: `{validation['passed_count']}`",
            "",
            f"Failed checks: `{validation['failed_count']}`",
            "",
            "## Target",
            "",
            "| Field | Value |",
            "| --- | --- |",
            *target_rows,
            "",
            "## Host State",
            "",
            "| Field | Value |",
            "| --- | --- |",
            *host_rows,
            "",
            "## Planned Panels",
            "",
            *panel_lines,
            "",
            "## Safety Boundary",
            "",
            "| Field | Value |",
            "| --- | --- |",
            *safety_rows,
            "",
            "## Local-only Boundary",
            "",
            "This renderer reads an existing local JSON file and writes Markdown/JSON summaries.",
            "",
            "It does not query extension state, submit extension requests, activate DriverKit, request device ownership, collect live PCI inventory, access PCI configuration space, access MMIO, map BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, load firmware, initialize display paths, or reset the GPU.",
            "",
        ]
    )


def build_renderer_report(input_path: Path, output_md: Path, data: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    decision = "PASS_LOCAL_HOST_REPORT_RENDERED" if validation["failed_count"] == 0 else "FAIL_LOCAL_HOST_REPORT_RENDER_INVALID"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "input_path": str(input_path),
        "output_markdown_path": str(output_md),
        "source_schema": data.get("schema"),
        "source_decision": data.get("decision"),
        "passed_count": validation["passed_count"],
        "failed_count": validation["failed_count"],
        "checks": validation["checks"],
        "safety_boundary": {
            "local_file_read_only": True,
            "writes_markdown_summary": True,
            "writes_json_summary": True,
            "queries_live_extension_state": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "device_ownership_request": False,
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
            "hardware_command_submission": False,
            "resource_allocation_on_rtx5070": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a local H1mekaRTX host status JSON report to Markdown."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Local host status JSON report to render.",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not input_path.exists() or not input_path.is_file():
        raise SystemExit(f"Input report does not exist: {input_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    data = load_json(input_path)
    validation = build_validation(data)

    md_path = out_dir / "rendered-host-status-report.md"
    report_path = out_dir / "local-host-report-renderer-report.json"

    md_path.write_text(render_markdown(input_path, data, validation) + "\n")

    report = build_renderer_report(input_path, md_path, data, validation)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    print(f"Wrote: {md_path}")
    print(f"Wrote: {report_path}")
    print(f"Decision: {report['decision']}")

    return 0 if validation["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
