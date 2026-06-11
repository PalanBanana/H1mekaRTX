#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_status_schema_viewer_plan.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

HOST_STATUS_SCHEMA = {
    "schema": "h1mekartx.host_status_report.v1",
    "required_top_level_fields": [
        "schema",
        "decision",
        "generatedAtUTC",
        "target",
        "hostState",
        "plannedPanels",
        "safetyBoundary",
    ],
    "target_fields": [
        "gpu",
        "vendorID",
        "deviceID",
        "iopcimatch",
        "subsystemVendorID",
        "subsystemID",
    ],
    "host_state_fields": [
        "hostSkeletonPresent",
        "activationControllerImplemented",
        "driverExtensionTargetIncluded",
        "activationRequestSubmitted",
        "deactivationRequestSubmitted",
        "managerSubmitCalled",
        "deviceOwnershipRequested",
        "metalReferenceWorkloadLauncherPlanned",
    ],
    "safety_boundary_fields": [
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
    ],
}

STATUS_STATES = [
    {
        "state": "NO_ACTIVATION_SKELETON_READY",
        "allowed_currently": True,
        "meaning": "Host-side skeleton exists and reports local status only.",
    },
    {
        "state": "LOCAL_REPORT_VIEWER_PLANNED",
        "allowed_currently": True,
        "meaning": "A future local viewer may read generated JSON reports and render them without hardware access.",
    },
    {
        "state": "STATUS_VIEWER_IMPLEMENTED",
        "allowed_currently": False,
        "meaning": "Future stage may add a local-only viewer implementation.",
    },
    {
        "state": "EXTENSION_REQUEST_READY",
        "allowed_currently": False,
        "meaning": "Future state only after entitlement, signing, rollback, and dry-run gates pass.",
    },
    {
        "state": "EXTENSION_PENDING_APPROVAL",
        "allowed_currently": False,
        "meaning": "Future activation request submitted and waiting for user approval.",
    },
    {
        "state": "EXTENSION_ACTIVE",
        "allowed_currently": False,
        "meaning": "Future system extension active state. Not allowed in this track yet.",
    },
    {
        "state": "FAILED_OR_ROLLED_BACK",
        "allowed_currently": False,
        "meaning": "Future failure or rollback state.",
    },
]

VIEWER_PANELS = [
    {
        "panel": "overview",
        "status": "PLANNED_ONLY",
        "inputs": [
            "host status report JSON",
            "stage decision",
            "generated timestamp",
        ],
        "forbidden_inputs": [
            "live system extension query",
            "live PCI probing",
            "live BAR or MMIO data",
        ],
    },
    {
        "panel": "target-identity",
        "status": "PLANNED_ONLY",
        "inputs": [
            "static RTX 5070 target identity",
            "repo-generated report fields",
        ],
        "forbidden_inputs": [
            "live I/O registry collection",
            "live system profiler collection",
        ],
    },
    {
        "panel": "safety-boundary",
        "status": "PLANNED_ONLY",
        "inputs": [
            "safetyBoundary JSON object",
            "known forbidden operation flags",
        ],
        "forbidden_inputs": [
            "hardware access result",
            "driver activation result",
        ],
    },
    {
        "panel": "metal-reference-workloads",
        "status": "PLANNED_ONLY",
        "inputs": [
            "Stage 25 workload suite reports",
            "existing system Metal device validation results",
        ],
        "forbidden_inputs": [
            "RTX 5070 shader execution result",
            "RTX 5070 command submission result",
        ],
    },
    {
        "panel": "diagnostics-export",
        "status": "PLANNED_ONLY",
        "inputs": [
            "local generated markdown reports",
            "local generated JSON reports",
        ],
        "forbidden_inputs": [
            "automatic log collection",
            "automatic hardware probing",
            "private profile or certificate material",
        ],
    },
]

REPORT_SOURCES = [
    {
        "source": "host app no-activation runtime report",
        "path_hint": "tools/host-app-no-activation swift run output",
        "status": "AVAILABLE_FROM_STAGE27",
        "live_hardware_access": False,
    },
    {
        "source": "Metal reference workload suite report",
        "path_hint": "metal-reference-workload-suite-report.json",
        "status": "LOCAL_GENERATED_ARTIFACT",
        "live_hardware_access": False,
    },
    {
        "source": "BAR evidence ledger",
        "path_hint": "bar-evidence-ledger.json",
        "status": "LOCAL_GENERATED_ARTIFACT",
        "live_hardware_access": False,
    },
    {
        "source": "implementation blocker register",
        "path_hint": "implementation-blocker-register.json",
        "status": "LOCAL_GENERATED_ARTIFACT",
        "live_hardware_access": False,
    },
]

VIEWER_GATES = [
    {
        "gate": "HSG-1",
        "name": "Schema fields stable",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_viewer_implementation": True,
        "reason": "Stage 28 defines required report fields.",
    },
    {
        "gate": "HSG-2",
        "name": "Local-only input policy",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_viewer_implementation": True,
        "reason": "Viewer inputs are limited to local generated JSON and markdown reports.",
    },
    {
        "gate": "HSG-3",
        "name": "No activation dependency",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_viewer_implementation": True,
        "reason": "Viewer does not require any extension request or driver activation.",
    },
    {
        "gate": "HSG-4",
        "name": "No hardware access dependency",
        "status": "PASS_FOR_CURRENT_STAGE",
        "required_before_viewer_implementation": True,
        "reason": "Viewer does not require PCI, BAR, MMIO, command submission, or RTX 5070 resource allocation.",
    },
    {
        "gate": "HSG-5",
        "name": "UI implementation",
        "status": "FUTURE_STAGE_ONLY",
        "required_before_viewer_implementation": False,
        "reason": "This stage plans the viewer schema and panels only.",
    },
]

FORBIDDEN_NOW = [
    "host app GUI implementation",
    "DriverKit dext target creation",
    "System Extension activation request",
    "System Extension deactivation request",
    "extension manager submit request",
    "DriverKit activation",
    "device ownership request",
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
    "hardware command submission",
    "RTX 5070 resource allocation",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "HOST_STATUS_SCHEMA_VIEWER_PLAN_READY",
        "full_metal_goal": True,
        "research_continues": True,
        "host_status_schema_ready": True,
        "local_report_viewer_plan_ready": True,
        "viewer_implementation_allowed": False,
        "host_gui_implementation_allowed": False,
        "system_extension_request_allowed": False,
        "driverkit_activation_allowed": False,
        "implementation_allowed": False,
        "implementation_started": False,
        "host_status_schema": HOST_STATUS_SCHEMA,
        "status_states": STATUS_STATES,
        "viewer_panels": VIEWER_PANELS,
        "report_sources": REPORT_SOURCES,
        "viewer_gates": VIEWER_GATES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 29 should add a local-only host report renderer skeleton, still without System Extension requests, DriverKit activation, IOPCIDevice ownership, BAR/MMIO access, or RTX 5070 acceleration.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "adds_host_gui": False,
            "adds_driverkit_dext_target": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "device_ownership_request": False,
            "live_extension_status_query": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "resource_allocation_on_rtx5070": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    schema_rows = []
    for key, values in data["host_status_schema"].items():
        if isinstance(values, list):
            schema_rows.append(f"| `{key}` | {', '.join(f'`{v}`' for v in values)} |")
        else:
            schema_rows.append(f"| `{key}` | `{values}` |")

    state_rows = []
    for item in data["status_states"]:
        state_rows.append(
            f"| `{item['state']}` | `{item['allowed_currently']}` | {item['meaning']} |"
        )

    panel_rows = []
    for item in data["viewer_panels"]:
        inputs = "<br>".join(item["inputs"])
        forbidden = "<br>".join(item["forbidden_inputs"])
        panel_rows.append(
            f"| `{item['panel']}` | `{item['status']}` | {inputs} | {forbidden} |"
        )

    source_rows = []
    for item in data["report_sources"]:
        source_rows.append(
            f"| {item['source']} | `{item['path_hint']}` | `{item['status']}` | `{item['live_hardware_access']}` |"
        )

    gate_rows = []
    for item in data["viewer_gates"]:
        gate_rows.append(
            f"| `{item['gate']}` | {item['name']} | `{item['status']}` | `{item['required_before_viewer_implementation']}` | {item['reason']} |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Host Status Schema and Local Report Viewer Plan",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Host status schema ready: `{data['host_status_schema_ready']}`",
            "",
            f"Local report viewer plan ready: `{data['local_report_viewer_plan_ready']}`",
            "",
            f"Viewer implementation allowed: `{data['viewer_implementation_allowed']}`",
            "",
            f"Host GUI implementation allowed: `{data['host_gui_implementation_allowed']}`",
            "",
            f"System Extension request allowed: `{data['system_extension_request_allowed']}`",
            "",
            f"DriverKit activation allowed: `{data['driverkit_activation_allowed']}`",
            "",
            f"Implementation allowed: `{data['implementation_allowed']}`",
            "",
            f"Implementation started: `{data['implementation_started']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{data['target']['gpu']}`",
            f"- Vendor ID: `{data['target']['vendor_id']}`",
            f"- Device ID: `{data['target']['device_id']}`",
            f"- IOPCIMatch: `{data['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{data['target']['subsystem_vendor_id']}`",
            f"- Subsystem ID: `{data['target']['subsystem_id']}`",
            "",
            "## Host Status Schema",
            "",
            "| Schema Area | Fields |",
            "| --- | --- |",
            *schema_rows,
            "",
            "## Status States",
            "",
            "| State | Allowed Currently | Meaning |",
            "| --- | --- | --- |",
            *state_rows,
            "",
            "## Planned Viewer Panels",
            "",
            "| Panel | Status | Inputs | Forbidden Inputs |",
            "| --- | --- | --- | --- |",
            *panel_rows,
            "",
            "## Report Sources",
            "",
            "| Source | Path Hint | Status | Live Hardware Access |",
            "| --- | --- | --- | --- |",
            *source_rows,
            "",
            "## Viewer Gates",
            "",
            "| Gate | Name | Status | Required Before Viewer Implementation | Reason |",
            "| --- | --- | --- | --- | --- |",
            *gate_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is documentation-only.",
            "",
            "It does not add a host GUI, add a DriverKit dext target, add System Extension request code, activate DriverKit, submit activation or deactivation requests, submit extension manager requests, request device ownership, query live extension status, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, load firmware, initialize GSP, initialize display engine, initialize framebuffer, run GPU reset logic, or start RTX 5070 Metal acceleration implementation.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX host status schema and local report viewer plan."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_plan()

    json_path = out_dir / "host-status-schema-viewer-plan.json"
    md_path = out_dir / "host-status-schema-viewer-plan.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
