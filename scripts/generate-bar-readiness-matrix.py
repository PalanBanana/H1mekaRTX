#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXPECTED_SCHEMA = "h1mekartx.bar_inventory_summary.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

DANGEROUS_FLAGS = [
    "pci_config_writes",
    "mmio_writes",
    "bar_poking",
    "gpu_reset",
    "firmware_loading",
    "gsp_initialization",
    "display_engine_init",
    "framebuffer_init",
    "metal_acceleration_attempt",
    "driverkit_activation",
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        raise SystemExit(f"Missing summary JSON: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}")

    if not isinstance(data, dict):
        raise SystemExit(f"Summary JSON must be an object: {path}")

    return data


def as_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def norm(value: Any) -> str:
    return str(value).strip().lower()


def check_target(summary: dict[str, Any]) -> tuple[bool, str]:
    target = summary.get("target", {})
    if not isinstance(target, dict):
        return False, "target object missing"

    mismatches = []

    for key, expected in EXPECTED_TARGET.items():
        actual = norm(target.get(key, ""))
        if actual != expected:
            mismatches.append(f"{key}: expected {expected}, actual {actual or '<missing>'}")

    if mismatches:
        return False, "; ".join(mismatches)

    return True, "RTX 5070 PCI target IDs match expected values"


def check_target_observed(summary: dict[str, Any]) -> tuple[bool, str]:
    target_hits = summary.get("target_hits", {})
    if not isinstance(target_hits, dict):
        return False, "target_hits object missing"

    vendor_hit = as_int(target_hits.get("vendor_10de", 0)) >= 1
    device_hit = as_int(target_hits.get("device_2f04", 0)) >= 1
    match_hit = as_int(target_hits.get("iopcimatch_2f0410de", 0)) >= 1

    if vendor_hit and (device_hit or match_hit):
        return True, "vendor 0x10de and device/IOPCIMatch hint observed"

    return (
        False,
        (
            f"vendor_10de={target_hits.get('vendor_10de', 0)!r}, "
            f"device_2f04={target_hits.get('device_2f04', 0)!r}, "
            f"iopcimatch_2f0410de={target_hits.get('iopcimatch_2f0410de', 0)!r}"
        ),
    )


def check_read_only(summary: dict[str, Any]) -> tuple[bool, str]:
    safety = summary.get("safety_boundary", {})
    if not isinstance(safety, dict):
        return False, "safety_boundary object missing"

    if safety.get("read_only") is not True:
        return False, f"read_only={safety.get('read_only')!r}"

    enabled = [flag for flag in DANGEROUS_FLAGS if safety.get(flag) is not False]

    if enabled:
        return False, "unsafe or missing flags: " + ", ".join(enabled)

    return True, "read-only boundary is intact and all risky action flags are false"


def make_requirement(
    area: str,
    requirement: str,
    status: str,
    evidence: str,
    next_action: str,
) -> dict[str, str]:
    return {
        "area": area,
        "requirement": requirement,
        "status": status,
        "evidence": evidence,
        "next_action": next_action,
    }


def build_matrix(summary: dict[str, Any], summary_path: Path) -> dict[str, Any]:
    schema_ok = summary.get("schema") == EXPECTED_SCHEMA
    target_ok, target_detail = check_target(summary)
    observed_ok, observed_detail = check_target_observed(summary)
    read_only_ok, read_only_detail = check_read_only(summary)

    requirements = [
        make_requirement(
            "Input",
            "Stage 4 summary JSON is present and uses the expected schema.",
            "PASS" if schema_ok else "FAIL",
            f"schema={summary.get('schema')!r}",
            "Regenerate the Stage 4 summary with scripts/summarize-bar-inventory.py if this fails.",
        ),
        make_requirement(
            "PCI target",
            "RTX 5070 PCI target IDs match the expected project target.",
            "PASS" if target_ok else "FAIL",
            target_detail,
            "Fix the target metadata before using this summary for future research.",
        ),
        make_requirement(
            "PCI target observation",
            "OS-visible inventory contains at least the NVIDIA vendor hint and device or IOPCIMatch hint.",
            "PASS" if observed_ok else "FAIL",
            observed_detail,
            "Re-run Stage 3 diagnostics and confirm the GPU is visible to macOS.",
        ),
        make_requirement(
            "Safety boundary",
            "All generated metadata still declares read-only behavior and no risky actions.",
            "PASS" if read_only_ok else "FAIL",
            read_only_detail,
            "Stop and repair the safety metadata before continuing.",
        ),
        make_requirement(
            "BAR identity",
            "Each BAR/aperture index is mapped to a documented role.",
            "BLOCKED",
            "Stage 4 only records OS-visible hints; it does not define BAR roles.",
            "Create a later read-only BAR role research stage before any aperture access.",
        ),
        make_requirement(
            "BAR size semantics",
            "BAR sizes and address ranges are understood without probing or poking.",
            "BLOCKED",
            "No trusted BAR size interpretation is recorded in the current project metadata.",
            "Add a documentation-only BAR layout note from reliable sources or safe OS inventory.",
        ),
        make_requirement(
            "Register map",
            "No register is accessed until its offset, width, side effects, and reset behavior are documented.",
            "BLOCKED",
            "No RTX 5070 register map is present in this repo stage.",
            "Create a register-map placeholder and keep all unknown offsets forbidden.",
        ),
        make_requirement(
            "Recovery path",
            "A safe recovery plan exists for failed experiments.",
            "BLOCKED",
            "No GPU reset/recovery runbook exists yet.",
            "Document reboot, power-cycle, rollback, and panic-log capture procedures first.",
        ),
        make_requirement(
            "DriverKit activation",
            "Any DriverKit activation or entitlement work is separated from BAR inventory work.",
            "BLOCKED",
            "This stage does not request or activate DriverKit device ownership.",
            "Create a separate DriverKit activation design review stage later.",
        ),
        make_requirement(
            "Metal acceleration",
            "Metal acceleration remains out of scope for BAR readiness.",
            "BLOCKED",
            "No display, framebuffer, command processor, firmware, or Metal path is implemented.",
            "Keep Metal acceleration as a later high-level milestone.",
        ),
    ]

    hard_fail = any(item["status"] == "FAIL" for item in requirements)
    blockers = [item for item in requirements if item["status"] == "BLOCKED"]

    readiness = "INVALID" if hard_fail else "NOT_READY"
    if not hard_fail and not blockers:
        readiness = "READY_FOR_REVIEW"

    return {
        "schema": "h1mekartx.bar_access_readiness_matrix.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_summary": str(summary_path),
        "readiness": readiness,
        "pass_count": sum(1 for item in requirements if item["status"] == "PASS"),
        "fail_count": sum(1 for item in requirements if item["status"] == "FAIL"),
        "blocked_count": sum(1 for item in requirements if item["status"] == "BLOCKED"),
        "requirements": requirements,
        "safety_boundary": {
            "read_only": True,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "metal_acceleration_attempt": False,
            "driverkit_activation": False,
        },
    }


def markdown_report(matrix: dict[str, Any]) -> str:
    rows = []
    for item in matrix["requirements"]:
        rows.append(
            "| {area} | {requirement} | {status} | `{evidence}` | {next_action} |".format(
                area=item["area"],
                requirement=item["requirement"],
                status=item["status"],
                evidence=item["evidence"].replace("|", "\\|"),
                next_action=item["next_action"],
            )
        )

    return "\n".join(
        [
            "# BAR Access Readiness Matrix",
            "",
            f"Generated UTC: `{matrix['generated_at_utc']}`",
            "",
            f"Input summary: `{matrix['input_summary']}`",
            "",
            f"Readiness: `{matrix['readiness']}`",
            "",
            f"PASS: `{matrix['pass_count']}`",
            "",
            f"FAIL: `{matrix['fail_count']}`",
            "",
            f"BLOCKED: `{matrix['blocked_count']}`",
            "",
            "## Matrix",
            "",
            "| Area | Requirement | Status | Evidence | Next Action |",
            "| --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Interpretation",
            "",
            "`NOT_READY` is the expected result for this stage.",
            "",
            "The project should remain blocked from BAR/MMIO access until BAR identity, BAR size semantics, register side effects, recovery flow, and DriverKit activation boundaries are separately documented and reviewed.",
            "",
            "## Safety Boundary",
            "",
            "This report is generated from an existing Stage 4 summary JSON only.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR mapping, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a BAR access readiness matrix from a Stage 4 BAR inventory summary."
    )
    parser.add_argument(
        "summary_json",
        help="Path to bar-inventory-summary.json generated by Stage 4.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to the summary JSON directory.",
    )

    args = parser.parse_args()

    summary_path = Path(args.summary_json).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else summary_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = load_json(summary_path)
    matrix = build_matrix(summary, summary_path)

    json_path = out_dir / "bar-access-readiness-matrix.json"
    md_path = out_dir / "bar-access-readiness-matrix.md"

    json_path.write_text(json.dumps(matrix, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(matrix) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Readiness: {matrix['readiness']}")

    if matrix["readiness"] == "INVALID":
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
