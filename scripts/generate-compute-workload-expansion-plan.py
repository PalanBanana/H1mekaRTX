#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.compute_workload_expansion_plan.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

CURRENT_WORKLOADS = [
    {
        "name": "vector_add",
        "function_name": "h1meka_vector_add",
        "status": "IMPLEMENTED",
        "workload_type": "compute",
        "vector_length": 512,
        "expected_formula": "out[i] = a[i] + b[i]",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "saxpy",
        "function_name": "h1meka_saxpy",
        "status": "IMPLEMENTED",
        "workload_type": "compute",
        "vector_length": 512,
        "expected_formula": "out[i] = alpha * x[i] + y[i]",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "square",
        "function_name": "h1meka_square",
        "status": "IMPLEMENTED",
        "workload_type": "compute",
        "vector_length": 512,
        "expected_formula": "out[i] = x[i] * x[i]",
        "deterministic": True,
        "system_metal_device_only": True,
        "rtx5070_execution_allowed": False,
    },
]

PLANNED_WORKLOADS = [
    {
        "name": "vector_multiply",
        "proposed_function_name": "h1meka_vector_multiply",
        "priority": "P1",
        "category": "elementwise_arithmetic",
        "expected_formula": "out[i] = a[i] * b[i]",
        "input_buffers": ["a", "b"],
        "output_buffers": ["out"],
        "scalar_parameters": [],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.0001,
        "reason": "Covers elementwise multiplication and verifies two-input buffer handling.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "vector_subtract",
        "proposed_function_name": "h1meka_vector_subtract",
        "priority": "P1",
        "category": "elementwise_arithmetic",
        "expected_formula": "out[i] = a[i] - b[i]",
        "input_buffers": ["a", "b"],
        "output_buffers": ["out"],
        "scalar_parameters": [],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.0001,
        "reason": "Adds signed arithmetic behavior and complements vector_add.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "axpby",
        "proposed_function_name": "h1meka_axpby",
        "priority": "P1",
        "category": "linear_algebra_microkernel",
        "expected_formula": "out[i] = alpha * x[i] + beta * y[i]",
        "input_buffers": ["x", "y"],
        "output_buffers": ["out"],
        "scalar_parameters": ["alpha", "beta"],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.0001,
        "reason": "Generalizes saxpy and validates multiple scalar constants.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "clamp",
        "proposed_function_name": "h1meka_clamp",
        "priority": "P2",
        "category": "branchless_range",
        "expected_formula": "out[i] = min(max(x[i], low), high)",
        "input_buffers": ["x"],
        "output_buffers": ["out"],
        "scalar_parameters": ["low", "high"],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.0001,
        "reason": "Validates min/max behavior and bounded output ranges.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "threshold_mask",
        "proposed_function_name": "h1meka_threshold_mask",
        "priority": "P2",
        "category": "predicate_output",
        "expected_formula": "out[i] = x[i] >= threshold ? 1.0 : 0.0",
        "input_buffers": ["x"],
        "output_buffers": ["out"],
        "scalar_parameters": ["threshold"],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.0001,
        "reason": "Adds deterministic predicate output without touching graphics or hardware-specific paths.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
    {
        "name": "fma_reference",
        "proposed_function_name": "h1meka_fma_reference",
        "priority": "P3",
        "category": "floating_point_behavior",
        "expected_formula": "out[i] = a[i] * b[i] + c[i]",
        "input_buffers": ["a", "b", "c"],
        "output_buffers": ["out"],
        "scalar_parameters": [],
        "vector_lengths": [64, 512, 4096],
        "max_absolute_error_tolerance": 0.001,
        "reason": "Adds a tolerance-aware floating-point reference case for multiply-add behavior.",
        "implementation_allowed_now": False,
        "rtx5070_execution_allowed": False,
    },
]

EXPANSION_PHASES = [
    {
        "phase": "CWE-1",
        "name": "P1 arithmetic expansion",
        "workloads": ["vector_multiply", "vector_subtract", "axpby"],
        "status": "PLANNED_ONLY",
        "implementation_stage": "Stage 35 candidate",
    },
    {
        "phase": "CWE-2",
        "name": "P2 range and predicate expansion",
        "workloads": ["clamp", "threshold_mask"],
        "status": "PLANNED_ONLY",
        "implementation_stage": "Future public Metal workload stage",
    },
    {
        "phase": "CWE-3",
        "name": "P3 floating-point behavior expansion",
        "workloads": ["fma_reference"],
        "status": "PLANNED_ONLY",
        "implementation_stage": "Future tolerance review stage",
    },
]

ACCEPTANCE_RULES = [
    {
        "rule": "all new workloads must run on the existing system Metal device only",
        "required": True,
    },
    {
        "rule": "each workload must have deterministic CPU-side expected outputs",
        "required": True,
    },
    {
        "rule": "each workload must report maxAbsoluteError",
        "required": True,
    },
    {
        "rule": "each workload must be added to the regression manifest before release",
        "required": True,
    },
    {
        "rule": "each workload must keep RTX 5070 execution disabled",
        "required": True,
    },
    {
        "rule": "no workload may introduce PCI, BAR, MMIO, DriverKit, firmware, display, framebuffer, or GPU reset code",
        "required": True,
    },
]

FORBIDDEN_NOW = [
    "implementing planned workloads in this stage",
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


def build_plan() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "COMPUTE_WORKLOAD_EXPANSION_PLAN_READY",
        "full_metal_goal": True,
        "research_continues": True,
        "safe_app_level_production_started": True,
        "planned_workload_implementation_started": False,
        "real_acceleration_production_started": False,
        "real_acceleration_production_allowed": False,
        "current_workload_count": len(CURRENT_WORKLOADS),
        "planned_workload_count": len(PLANNED_WORKLOADS),
        "current_workloads": CURRENT_WORKLOADS,
        "planned_workloads": PLANNED_WORKLOADS,
        "expansion_phases": EXPANSION_PHASES,
        "acceptance_rules": ACCEPTANCE_RULES,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 35 should implement the P1 arithmetic workload expansion on the existing system Metal device only, if safety gates remain clean.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "plan_only": True,
            "uses_existing_system_metal_device_only": True,
            "planned_workload_implementation_started": False,
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
    current_rows = []
    for item in data["current_workloads"]:
        current_rows.append(
            f"| `{item['name']}` | `{item['function_name']}` | `{item['status']}` | `{item['expected_formula']}` | `{item['rtx5070_execution_allowed']}` |"
        )

    planned_rows = []
    for item in data["planned_workloads"]:
        inputs = ", ".join(f"`{x}`" for x in item["input_buffers"])
        outputs = ", ".join(f"`{x}`" for x in item["output_buffers"])
        scalars = ", ".join(f"`{x}`" for x in item["scalar_parameters"]) if item["scalar_parameters"] else "—"
        lengths = ", ".join(str(x) for x in item["vector_lengths"])
        planned_rows.append(
            f"| `{item['name']}` | `{item['proposed_function_name']}` | `{item['priority']}` | `{item['category']}` | {inputs} | {outputs} | {scalars} | `{lengths}` | `{item['expected_formula']}` | `{item['implementation_allowed_now']}` | `{item['rtx5070_execution_allowed']}` |"
        )

    phase_rows = []
    for item in data["expansion_phases"]:
        workloads = ", ".join(f"`{x}`" for x in item["workloads"])
        phase_rows.append(
            f"| `{item['phase']}` | {item['name']} | {workloads} | `{item['status']}` | {item['implementation_stage']} |"
        )

    rule_lines = [f"- {item['rule']} (`required={item['required']}`)" for item in data["acceptance_rules"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# Compute Workload Expansion Plan",
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
            f"Planned workload implementation started: `{data['planned_workload_implementation_started']}`",
            "",
            f"Real acceleration production started: `{data['real_acceleration_production_started']}`",
            "",
            f"Real acceleration production allowed: `{data['real_acceleration_production_allowed']}`",
            "",
            f"Current workload count: `{data['current_workload_count']}`",
            "",
            f"Planned workload count: `{data['planned_workload_count']}`",
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
            "## Current Workloads",
            "",
            "| Name | Function | Status | Expected Formula | RTX 5070 Execution Allowed |",
            "| --- | --- | --- | --- | --- |",
            *current_rows,
            "",
            "## Planned Workloads",
            "",
            "| Name | Proposed Function | Priority | Category | Inputs | Outputs | Scalars | Vector Lengths | Expected Formula | Implementation Allowed Now | RTX 5070 Execution Allowed |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *planned_rows,
            "",
            "## Expansion Phases",
            "",
            "| Phase | Name | Workloads | Status | Implementation Stage |",
            "| --- | --- | --- | --- | --- |",
            *phase_rows,
            "",
            "## Acceptance Rules",
            "",
            *rule_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is plan-only and documentation-only.",
            "",
            "It does not implement the planned workloads, start real RTX 5070 Metal acceleration production, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, run VRAM residency experiments, program device addresses, create page tables, run live PCI probing, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, activate DriverKit, submit System Extension requests, request device ownership, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate H1mekaRTX compute workload expansion plan."
    )
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_plan()

    json_path = out_dir / "compute-workload-expansion-plan.json"
    md_path = out_dir / "compute-workload-expansion-plan.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
