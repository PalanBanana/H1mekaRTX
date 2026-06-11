#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_workload_result_schema.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

RUNTIME_SCHEMA = {
    "schema_name": "h1mekartx.metal_reference_workload_runtime.v1",
    "required_top_level_fields": [
        "schema",
        "deviceName",
        "registryID",
        "workloadCount",
        "validationPassed",
        "workloads",
        "safetyBoundary",
    ],
    "workload_fields": [
        "name",
        "functionName",
        "vectorLength",
        "validationPassed",
        "maxAbsoluteError",
    ],
    "safety_boundary_fields": [
        "usesExistingSystemMetalDeviceOnly",
        "rtx5070MetalAccelerationAttempt",
        "performsPCIConfigReads",
        "performsPCIConfigWrites",
        "performsMMIOReads",
        "performsMMIOWrites",
        "mapsBARMemory",
        "barPoking",
        "gpuReset",
        "firmwareLoading",
        "gspInitialization",
        "displayEngineInit",
        "framebufferInit",
        "driverkitActivation",
        "hardwareCommandSubmissionToRTX5070",
        "resourceAllocationOnRTX5070",
    ],
}

WORKLOAD_CATALOG = [
    {
        "name": "vector_add",
        "function_name": "h1meka_vector_add",
        "workload_type": "compute",
        "input_buffers": ["a", "b"],
        "output_buffers": ["out"],
        "expected_formula": "out[i] = a[i] + b[i]",
        "deterministic": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "saxpy",
        "function_name": "h1meka_saxpy",
        "workload_type": "compute",
        "input_buffers": ["x", "y", "alpha"],
        "output_buffers": ["out"],
        "expected_formula": "out[i] = alpha * x[i] + y[i]",
        "deterministic": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "square",
        "function_name": "h1meka_square",
        "workload_type": "compute",
        "input_buffers": ["x"],
        "output_buffers": ["out"],
        "expected_formula": "out[i] = x[i] * x[i]",
        "deterministic": True,
        "rtx5070_execution_allowed": False,
    },
]

VALIDATION_RULES = [
    {
        "rule": "schema matches runtime schema",
        "required": True,
        "expected": "h1mekartx.metal_reference_workload_runtime.v1",
    },
    {
        "rule": "workloadCount matches workload array length",
        "required": True,
        "expected": "workloadCount == len(workloads)",
    },
    {
        "rule": "every workload validationPassed is true",
        "required": True,
        "expected": "all workload validationPassed values are true",
    },
    {
        "rule": "maxAbsoluteError is within tolerance",
        "required": True,
        "expected": "maxAbsoluteError <= 0.0001",
    },
    {
        "rule": "existing system Metal device only",
        "required": True,
        "expected": "usesExistingSystemMetalDeviceOnly == true",
    },
    {
        "rule": "RTX 5070 acceleration disabled",
        "required": True,
        "expected": "rtx5070MetalAccelerationAttempt == false",
    },
    {
        "rule": "BAR and MMIO disabled",
        "required": True,
        "expected": "performsMMIOReads == false, performsMMIOWrites == false, mapsBARMemory == false",
    },
]

FORBIDDEN_NOW = [
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission to RTX 5070",
    "RTX 5070 resource allocation",
    "live PCI probing",
    "ioreg collection",
    "system_profiler collection",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "DriverKit activation",
    "System Extension activation request",
    "System Extension deactivation request",
    "extension manager submit request",
    "device ownership request",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "GPU reset logic",
]


def build_schema() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "METAL_WORKLOAD_RESULT_SCHEMA_READY",
        "full_metal_goal": True,
        "research_continues": True,
        "safe_app_level_production_started": True,
        "real_acceleration_production_started": False,
        "real_acceleration_production_allowed": False,
        "runtime_schema": RUNTIME_SCHEMA,
        "workload_catalog": WORKLOAD_CATALOG,
        "validation_rules": VALIDATION_RULES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 33 should add a workload regression manifest for the public Metal reference suite.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "schema_only": True,
            "uses_existing_system_metal_device_only": True,
            "real_acceleration_implementation_allowed": False,
            "real_acceleration_implementation_started": False,
            "rtx5070_metal_acceleration_attempt": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
            "live_pci_probing": False,
            "runs_ioreg": False,
            "runs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "device_ownership_request": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    top_rows = [f"| `{field}` | required |" for field in data["runtime_schema"]["required_top_level_fields"]]
    workload_field_rows = [f"| `{field}` | required |" for field in data["runtime_schema"]["workload_fields"]]
    safety_rows = [f"| `{field}` | required |" for field in data["runtime_schema"]["safety_boundary_fields"]]

    workload_rows = []
    for item in data["workload_catalog"]:
        workload_rows.append(
            f"| `{item['name']}` | `{item['function_name']}` | `{item['workload_type']}` | `{item['deterministic']}` | `{item['rtx5070_execution_allowed']}` | `{item['expected_formula']}` |"
        )

    rule_rows = []
    for item in data["validation_rules"]:
        rule_rows.append(
            f"| {item['rule']} | `{item['required']}` | `{item['expected']}` |"
        )

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Metal Workload Result Schema",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Full Metal goal: `{data['full_metal_goal']}`",
            "",
            f"Research continues: `{data['research_continues']}`",
            "",
            f"Safe app-level production started: `{data['safe_app_level_production_started']}`",
            "",
            f"Real acceleration production started: `{data['real_acceleration_production_started']}`",
            "",
            f"Real acceleration production allowed: `{data['real_acceleration_production_allowed']}`",
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
            "## Runtime Schema",
            "",
            f"Schema name: `{data['runtime_schema']['schema_name']}`",
            "",
            "### Required Top-level Fields",
            "",
            "| Field | Status |",
            "| --- | --- |",
            *top_rows,
            "",
            "### Required Workload Fields",
            "",
            "| Field | Status |",
            "| --- | --- |",
            *workload_field_rows,
            "",
            "### Required Safety Boundary Fields",
            "",
            "| Field | Status |",
            "| --- | --- |",
            *safety_rows,
            "",
            "## Workload Catalog",
            "",
            "| Name | Function | Type | Deterministic | RTX 5070 Execution Allowed | Expected Formula |",
            "| --- | --- | --- | --- | --- | --- |",
            *workload_rows,
            "",
            "## Validation Rules",
            "",
            "| Rule | Required | Expected |",
            "| --- | --- | --- |",
            *rule_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is schema-only and documentation-only.",
            "",
            "It does not start real RTX 5070 Metal acceleration production, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, activate DriverKit, submit System Extension requests, request device ownership, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX Metal workload result schema."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_schema()

    json_path = out_dir / "metal-workload-result-schema.json"
    md_path = out_dir / "metal-workload-result-schema.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
