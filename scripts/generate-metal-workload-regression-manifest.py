#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_workload_regression_manifest.v2"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

REFERENCE_RUNTIME_SCHEMA = "h1mekartx.metal_reference_workload_runtime.v1"

REGRESSION_CASES = [
    {
        "case_id": "MWR-001",
        "name": "vector_add",
        "function_name": "h1meka_vector_add",
        "stage_added": "Stage 25",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"a": "Float(i) * 0.25", "b": "Float(i % 17) * 1.5"},
        "expected_formula": "out[i] = a[i] + b[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "case_id": "MWR-002",
        "name": "saxpy",
        "function_name": "h1meka_saxpy",
        "stage_added": "Stage 25",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"x": "Float(i) * 0.25", "y": "Float(i % 17) * 1.5", "alpha": "2.5"},
        "expected_formula": "out[i] = alpha * x[i] + y[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "case_id": "MWR-003",
        "name": "square",
        "function_name": "h1meka_square",
        "stage_added": "Stage 25",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"x": "Float(i) * 0.25"},
        "expected_formula": "out[i] = x[i] * x[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "case_id": "MWR-004",
        "name": "vector_multiply",
        "function_name": "h1meka_vector_multiply",
        "stage_added": "Stage 35",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"a": "Float(i) * 0.25", "b": "Float(i % 17) * 1.5"},
        "expected_formula": "out[i] = a[i] * b[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "case_id": "MWR-005",
        "name": "vector_subtract",
        "function_name": "h1meka_vector_subtract",
        "stage_added": "Stage 35",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"a": "Float(i) * 0.25", "b": "Float(i % 17) * 1.5"},
        "expected_formula": "out[i] = a[i] - b[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "case_id": "MWR-006",
        "name": "axpby",
        "function_name": "h1meka_axpby",
        "stage_added": "Stage 35",
        "workload_type": "compute",
        "vector_length": 512,
        "input_pattern": {"x": "Float(i) * 0.25", "y": "Float(i % 17) * 1.5", "alpha": "2.5", "beta": "-0.75"},
        "expected_formula": "out[i] = alpha * x[i] + beta * y[i]",
        "max_absolute_error_tolerance": 0.0001,
        "required_result": "PASS",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
]

REGRESSION_RULES = [
    {
        "rule_id": "MRR-001",
        "name": "runtime schema match",
        "required": True,
        "expected": REFERENCE_RUNTIME_SCHEMA,
    },
    {
        "rule_id": "MRR-002",
        "name": "all expected workloads present",
        "required": True,
        "expected": "vector_add, saxpy, square, vector_multiply, vector_subtract, axpby",
    },
    {
        "rule_id": "MRR-003",
        "name": "workload count match",
        "required": True,
        "expected": "runtime workloadCount equals six regression cases",
    },
    {
        "rule_id": "MRR-004",
        "name": "all workloads pass",
        "required": True,
        "expected": "validationPassed == true for every workload",
    },
    {
        "rule_id": "MRR-005",
        "name": "error tolerance",
        "required": True,
        "expected": "maxAbsoluteError <= per-case tolerance",
    },
    {
        "rule_id": "MRR-006",
        "name": "existing system Metal device only",
        "required": True,
        "expected": "usesExistingSystemMetalDeviceOnly == true",
    },
    {
        "rule_id": "MRR-007",
        "name": "RTX 5070 acceleration disabled",
        "required": True,
        "expected": "rtx5070MetalAccelerationAttempt == false",
    },
    {
        "rule_id": "MRR-008",
        "name": "hardware access disabled",
        "required": True,
        "expected": "PCI config, MMIO, BAR, DriverKit, firmware, display, framebuffer, and GPU reset flags are false",
    },
]

REPORTING_FIELDS = [
    "schema",
    "deviceName",
    "registryID",
    "workloadCount",
    "validationPassed",
    "workloads[].name",
    "workloads[].functionName",
    "workloads[].vectorLength",
    "workloads[].validationPassed",
    "workloads[].maxAbsoluteError",
    "safetyBoundary.usesExistingSystemMetalDeviceOnly",
    "safetyBoundary.rtx5070MetalAccelerationAttempt",
    "safetyBoundary.performsPCIConfigReads",
    "safetyBoundary.performsPCIConfigWrites",
    "safetyBoundary.performsMMIOReads",
    "safetyBoundary.performsMMIOWrites",
    "safetyBoundary.mapsBARMemory",
    "safetyBoundary.driverkitActivation",
    "safetyBoundary.hardwareCommandSubmissionToRTX5070",
    "safetyBoundary.resourceAllocationOnRTX5070",
]

FORBIDDEN_NOW = [
    "RTX 5070 Metal acceleration implementation",
    "RTX 5070 shader execution",
    "hardware command submission to RTX 5070",
    "RTX 5070 resource allocation",
    "VRAM residency experiments",
    "device address programming",
    "page table creation",
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


def build_manifest() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "METAL_WORKLOAD_REGRESSION_MANIFEST_SYNCED_WITH_P1",
        "full_metal_goal": True,
        "research_continues": True,
        "safe_app_level_production_started": True,
        "p1_workloads_included": True,
        "real_acceleration_production_started": False,
        "real_acceleration_production_allowed": False,
        "reference_runtime_schema": REFERENCE_RUNTIME_SCHEMA,
        "regression_case_count": len(REGRESSION_CASES),
        "regression_cases": REGRESSION_CASES,
        "regression_rules": REGRESSION_RULES,
        "reporting_fields": REPORTING_FIELDS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 37 should add host report bundle format for local app/Metal reports.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "manifest_only": True,
            "uses_existing_system_metal_device_only": True,
            "p1_workloads_documented": True,
            "real_acceleration_implementation_allowed": False,
            "real_acceleration_implementation_started": False,
            "rtx5070_metal_acceleration_attempt": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
            "vram_residency_experiments": False,
            "device_address_programming": False,
            "page_table_creation": False,
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
    case_rows = []
    for item in data["regression_cases"]:
        inputs = "<br>".join(f"`{k}` = `{v}`" for k, v in item["input_pattern"].items())
        case_rows.append(
            f"| `{item['case_id']}` | `{item['name']}` | `{item['function_name']}` | `{item['stage_added']}` | `{item['vector_length']}` | {inputs} | `{item['expected_formula']}` | `{item['max_absolute_error_tolerance']}` | `{item['rtx5070_execution_allowed']}` |"
        )

    rule_rows = []
    for item in data["regression_rules"]:
        rule_rows.append(f"| `{item['rule_id']}` | {item['name']} | `{item['required']}` | `{item['expected']}` |")

    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Metal Workload Regression Manifest",
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
            f"P1 workloads included: `{data['p1_workloads_included']}`",
            "",
            f"Real acceleration production started: `{data['real_acceleration_production_started']}`",
            "",
            f"Real acceleration production allowed: `{data['real_acceleration_production_allowed']}`",
            "",
            f"Reference runtime schema: `{data['reference_runtime_schema']}`",
            "",
            f"Regression case count: `{data['regression_case_count']}`",
            "",
            "## Regression Cases",
            "",
            "| Case | Name | Function | Stage Added | Vector Length | Inputs | Expected Formula | Tolerance | RTX 5070 Execution Allowed |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *case_rows,
            "",
            "## Regression Rules",
            "",
            "| Rule | Name | Required | Expected |",
            "| --- | --- | --- | --- |",
            *rule_rows,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is manifest-only and documentation-only.",
            "",
            "It documents the six public Metal regression cases that run on the existing system Metal device only. It does not start RTX 5070 Metal acceleration, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, access PCI config space, access MMIO, map BAR memory, activate DriverKit, submit System Extension requests, request device ownership, load firmware, initialize display paths, or reset the GPU.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synced H1mekaRTX Metal workload regression manifest.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_manifest()

    json_path = out_dir / "metal-workload-regression-manifest.json"
    md_path = out_dir / "metal-workload-regression-manifest.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
