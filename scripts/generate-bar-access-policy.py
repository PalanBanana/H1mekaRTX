#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_MATRIX_SCHEMA = "h1mekartx.bar_access_readiness_matrix.v1"

POLICY_SCHEMA = "h1mekartx.bar_access_policy.v1"

TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

BAR_SLOTS = [
    "BAR0",
    "BAR1",
    "BAR2",
    "BAR3",
    "BAR4",
    "BAR5",
    "ROM",
]


FORBIDDEN_OPERATIONS = [
    "pci_config_write8",
    "pci_config_write16",
    "pci_config_write32",
    "mmio_read8",
    "mmio_read16",
    "mmio_read32",
    "mmio_read64",
    "mmio_write8",
    "mmio_write16",
    "mmio_write32",
    "mmio_write64",
    "bar_map",
    "bar_unmap",
    "bar_poke",
    "gpu_reset",
    "firmware_load",
    "gsp_init",
    "display_engine_init",
    "framebuffer_init",
    "metal_acceleration",
    "driverkit_activation",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"Missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON file: {path}: {exc}")

    if not isinstance(data, dict):
        raise SystemExit(f"JSON root must be an object: {path}")

    return data


def matrix_is_valid(matrix: dict[str, Any]) -> tuple[bool, list[str]]:
    problems: list[str] = []

    if matrix.get("schema") != EXPECTED_MATRIX_SCHEMA:
        problems.append(
            f"unexpected matrix schema: {matrix.get('schema')!r}; expected {EXPECTED_MATRIX_SCHEMA!r}"
        )

    readiness = matrix.get("readiness")
    if readiness not in {"NOT_READY", "INVALID", "READY_FOR_REVIEW"}:
        problems.append(f"unexpected readiness value: {readiness!r}")

    safety = matrix.get("safety_boundary", {})
    if not isinstance(safety, dict):
        problems.append("missing safety_boundary object")
    else:
        required_false = [
            "performs_pci_config_writes",
            "performs_mmio_reads",
            "performs_mmio_writes",
            "maps_bar_memory",
            "gpu_reset",
            "firmware_loading",
            "gsp_initialization",
            "display_engine_init",
            "framebuffer_init",
            "metal_acceleration_attempt",
            "driverkit_activation",
        ]

        if safety.get("read_only") is not True:
            problems.append(f"safety_boundary.read_only is not true: {safety.get('read_only')!r}")

        for key in required_false:
            if safety.get(key) is not False:
                problems.append(f"safety_boundary.{key} is not false: {safety.get(key)!r}")

    return len(problems) == 0, problems


def make_bar_policy_entry(bar: str, readiness: str) -> dict[str, Any]:
    return {
        "bar": bar,
        "access": "DENY",
        "read": False,
        "write": False,
        "map": False,
        "poke": False,
        "reason": (
            "BAR access is denied by default. "
            f"Current readiness is {readiness}. "
            "BAR identity, size semantics, register side effects, recovery flow, and DriverKit activation are not approved in this stage."
        ),
    }


def build_policy(matrix: dict[str, Any], matrix_path: Path) -> dict[str, Any]:
    ok, problems = matrix_is_valid(matrix)
    readiness = str(matrix.get("readiness", "INVALID"))

    if not ok:
        readiness = "INVALID"

    allow_future_review = readiness == "READY_FOR_REVIEW" and ok

    policy = {
        "schema": POLICY_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_matrix": str(matrix_path),
        "target": TARGET,
        "source_readiness": readiness,
        "policy_mode": "DEFAULT_DENY",
        "effective_decision": "DENY_ALL_BAR_ACCESS",
        "future_review_possible": allow_future_review,
        "matrix_validation_passed": ok,
        "matrix_validation_problems": problems,
        "bar_policy": [make_bar_policy_entry(bar, readiness) for bar in BAR_SLOTS],
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "allowed_operations": [
            "read_existing_stage3_text_files",
            "read_existing_stage4_summary_json",
            "read_existing_stage5_safety_report",
            "read_existing_stage6_readiness_matrix",
            "generate_local_json_report",
            "generate_local_markdown_report",
        ],
        "safety_boundary": {
            "read_only": True,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "metal_acceleration_attempt": False,
            "driverkit_activation": False,
        },
    }

    return policy


def markdown_report(policy: dict[str, Any]) -> str:
    bar_rows = []
    for item in policy["bar_policy"]:
        bar_rows.append(
            f"| {item['bar']} | {item['access']} | {item['read']} | {item['write']} | {item['map']} | {item['poke']} | {item['reason']} |"
        )

    forbidden_rows = [f"- `{op}`" for op in policy["forbidden_operations"]]
    allowed_rows = [f"- `{op}`" for op in policy["allowed_operations"]]

    problems = policy.get("matrix_validation_problems", [])
    if problems:
        problem_lines = [f"- `{problem}`" for problem in problems]
    else:
        problem_lines = ["- No matrix validation problems found."]

    return "\n".join(
        [
            "# BAR Access Policy",
            "",
            f"Generated UTC: `{policy['generated_at_utc']}`",
            "",
            f"Input matrix: `{policy['input_matrix']}`",
            "",
            f"Source readiness: `{policy['source_readiness']}`",
            "",
            f"Policy mode: `{policy['policy_mode']}`",
            "",
            f"Effective decision: `{policy['effective_decision']}`",
            "",
            f"Matrix validation passed: `{policy['matrix_validation_passed']}`",
            "",
            "## Matrix Validation Problems",
            "",
            *problem_lines,
            "",
            "## RTX 5070 PCI Target",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Vendor ID | `{policy['target']['vendor_id']}` |",
            f"| Device ID | `{policy['target']['device_id']}` |",
            f"| IOPCIMatch | `{policy['target']['iopcimatch']}` |",
            f"| Subsystem Vendor ID | `{policy['target']['subsystem_vendor_id']}` |",
            f"| Subsystem ID | `{policy['target']['subsystem_id']}` |",
            "",
            "## BAR Policy",
            "",
            "| BAR | Access | Read | Write | Map | Poke | Reason |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            *bar_rows,
            "",
            "## Forbidden Operations",
            "",
            *forbidden_rows,
            "",
            "## Allowed Operations",
            "",
            *allowed_rows,
            "",
            "## Safety Boundary",
            "",
            "This policy generator only reads an existing Stage 6 readiness matrix and writes local report files.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR mapping, BAR poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.",
            "",
            "## Interpretation",
            "",
            "`DENY_ALL_BAR_ACCESS` is the expected policy decision for this stage.",
            "",
            "A later stage may create a review-only exception proposal, but this Stage 7 policy remains default-deny.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a default-deny BAR access policy from a Stage 6 readiness matrix."
    )
    parser.add_argument(
        "readiness_matrix_json",
        help="Path to bar-access-readiness-matrix.json generated by Stage 6.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to the matrix JSON directory.",
    )

    args = parser.parse_args()

    matrix_path = Path(args.readiness_matrix_json).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else matrix_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    matrix = load_json(matrix_path)
    policy = build_policy(matrix, matrix_path)

    json_path = out_dir / "bar-access-policy.json"
    md_path = out_dir / "bar-access-policy.md"

    json_path.write_text(json.dumps(policy, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(policy) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Effective decision: {policy['effective_decision']}")

    if not policy["matrix_validation_passed"]:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
