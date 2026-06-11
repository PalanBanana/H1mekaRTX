#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_reference_workload_suite_check.v1"

REQUIRED_FILES = [
    "tools/metal-validation-harness/Package.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/main.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/reference_workloads.metal",
    "docs/metal/metal-reference-workload-suite.md",
]

REQUIRED_TERMS = [
    "h1meka_vector_add",
    "h1meka_saxpy",
    "h1meka_square",
    "MTLCreateSystemDefaultDevice",
    "makeCommandQueue",
    "makeCommandBuffer",
    "makeComputePipelineState",
    "dispatchThreads",
    "usesExistingSystemMetalDeviceOnly",
    "rtx5070MetalAccelerationAttempt: false",
    "performsMMIOReads: false",
    "performsMMIOWrites: false",
    "driverkitActivation: false",
    "hardwareCommandSubmissionToRTX5070: false",
    "resourceAllocationOnRTX5070: false",
]

FORBIDDEN_TERMS = [
    "IOPCIDevice",
    "ConfigurationWrite",
    "MemoryRead",
    "MemoryWrite",
    "OSSystemExtensionManager",
    "OSSystemExtensionRequest",
    "ioreg",
    "system_profiler",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def command_exists(command: str) -> bool:
    proc = subprocess.run(
        ["which", command],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode == 0


def maybe_build(root: Path, should_build: bool) -> dict[str, Any]:
    if not should_build:
        return {
            "attempted": False,
            "passed": None,
            "reason": "build not requested",
            "stdout": "",
            "stderr": "",
        }

    if platform.system() != "Darwin":
        return {
            "attempted": False,
            "passed": None,
            "reason": "Swift Metal build is only attempted on macOS",
            "stdout": "",
            "stderr": "",
        }

    if not command_exists("swift"):
        return {
            "attempted": False,
            "passed": None,
            "reason": "swift command not found",
            "stdout": "",
            "stderr": "",
        }

    harness_dir = root / "tools" / "metal-validation-harness"
    proc = subprocess.run(
        ["swift", "build"],
        cwd=harness_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return {
        "attempted": True,
        "passed": proc.returncode == 0,
        "reason": "swift build completed" if proc.returncode == 0 else "swift build failed",
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_report(root: Path, should_build: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "detail": detail,
            }
        )

    for rel in REQUIRED_FILES:
        path = root / rel
        add(
            f"path_exists:{rel}",
            path.exists(),
            "present" if path.exists() else "missing",
        )

    source = "\n".join(
        [
            read_text(root / "tools/metal-validation-harness/Package.swift"),
            read_text(root / "tools/metal-validation-harness/Sources/H1mekaMetalValidation/main.swift"),
            read_text(root / "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/reference_workloads.metal"),
        ]
    )

    for term in REQUIRED_TERMS:
        add(
            f"required_term:{term}",
            term in source,
            "found" if term in source else "missing",
        )

    for term in FORBIDDEN_TERMS:
        add(
            f"forbidden_term_absent:{term}",
            term not in source,
            "absent" if term not in source else "present",
        )

    build = maybe_build(root, should_build)
    if build["attempted"]:
        add(
            "optional_swift_build",
            build["passed"] is True,
            build["reason"],
        )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_METAL_REFERENCE_WORKLOAD_SUITE_READY" if failed_count == 0 else "FAIL_METAL_REFERENCE_WORKLOAD_SUITE_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "optional_build": build,
        "workloads": [
            {
                "name": "vector_add",
                "function": "h1meka_vector_add",
                "type": "compute",
            },
            {
                "name": "saxpy",
                "function": "h1meka_saxpy",
                "type": "compute",
            },
            {
                "name": "square",
                "function": "h1meka_square",
                "type": "compute",
            },
        ],
        "safety_boundary": {
            "read_only_static_check": True,
            "optional_build_only": should_build,
            "uses_existing_system_metal_device_only": True,
            "rtx5070_metal_acceleration_attempt": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "iopcidevice_ownership_request": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    check_rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        check_rows.append(f"| `{item['name']}` | {status} | {detail} |")

    workload_rows = []
    for item in report["workloads"]:
        workload_rows.append(f"| `{item['name']}` | `{item['function']}` | `{item['type']}` |")

    return "\n".join(
        [
            "# Metal Reference Workload Suite Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Workloads",
            "",
            "| Name | Function | Type |",
            "| --- | --- | --- |",
            *workload_rows,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *check_rows,
            "",
            "## Optional Build",
            "",
            f"- Attempted: `{report['optional_build']['attempted']}`",
            f"- Passed: `{report['optional_build']['passed']}`",
            f"- Reason: `{report['optional_build']['reason']}`",
            "",
            "## Safety Boundary",
            "",
            "This check validates the public Metal reference workload suite source tree.",
            "",
            "The suite is limited to the existing system Metal device and does not attempt RTX 5070 Metal acceleration, RTX 5070 shader execution, PCI config-space access, MMIO access, BAR mapping, DriverKit activation, System Extension activation, IOPCIDevice ownership, hardware command submission to RTX 5070, or RTX 5070 resource allocation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the H1mekaRTX Metal reference workload suite."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to repo root.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Optionally run swift build on macOS when Swift is available.",
    )

    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, args.build)

    json_path = out_dir / "metal-reference-workload-suite-report.json"
    md_path = out_dir / "metal-reference-workload-suite-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    if report["failed_count"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
