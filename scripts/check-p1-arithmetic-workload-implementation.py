#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.p1_arithmetic_workload_implementation_check.v1"

REQUIRED_FILES = [
    "tools/metal-validation-harness/Package.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/main.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/reference_workloads.metal",
    "docs/metal/p1-arithmetic-workload-implementation.md",
]

REQUIRED_WORKLOADS = [
    "vector_add",
    "saxpy",
    "square",
    "vector_multiply",
    "vector_subtract",
    "axpby",
]

REQUIRED_FUNCTIONS = [
    "h1meka_vector_add",
    "h1meka_saxpy",
    "h1meka_square",
    "h1meka_vector_multiply",
    "h1meka_vector_subtract",
    "h1meka_axpby",
]

REQUIRED_TERMS = [
    "MTLCreateSystemDefaultDevice",
    "makeCommandQueue",
    "makeCommandBuffer",
    "makeComputePipelineState",
    "dispatchThreads",
    "usesExistingSystemMetalDeviceOnly",
    "rtx5070MetalAccelerationAttempt: false",
    "performsMMIOReads: false",
    "performsMMIOWrites: false",
    "mapsBARMemory: false",
    "driverkitActivation: false",
    "hardwareCommandSubmissionToRTX5070: false",
    "resourceAllocationOnRTX5070: false",
]

FORBIDDEN_TERMS = [
    "IOPCI" + "Device",
    "OSSystem" + "ExtensionRequest",
    "OSSystem" + "ExtensionManager",
    "Configuration" + "Write",
    "Memory" + "Read",
    "Memory" + "Write",
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


def maybe_run(root: Path, should_run: bool) -> dict[str, Any]:
    if not should_run:
        return {
            "attempted": False,
            "passed": None,
            "reason": "runtime not requested",
            "stdout": "",
            "stderr": "",
            "parsed_report": {},
        }

    if platform.system() != "Darwin":
        return {
            "attempted": False,
            "passed": None,
            "reason": "Metal runtime is only attempted on macOS",
            "stdout": "",
            "stderr": "",
            "parsed_report": {},
        }

    if not command_exists("swift"):
        return {
            "attempted": False,
            "passed": None,
            "reason": "swift command not found",
            "stdout": "",
            "stderr": "",
            "parsed_report": {},
        }

    harness_dir = root / "tools" / "metal-validation-harness"
    proc = subprocess.run(
        ["swift", "run"],
        cwd=harness_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )

    parsed: dict[str, Any] = {}
    if proc.returncode == 0:
        try:
            parsed = json.loads(proc.stdout)
        except json.JSONDecodeError:
            parsed = {}

    expected = set(REQUIRED_WORKLOADS)
    got = set()
    if isinstance(parsed.get("workloads"), list):
        got = {item.get("name") for item in parsed["workloads"] if isinstance(item, dict)}

    safety = parsed.get("safetyBoundary", {})
    if not isinstance(safety, dict):
        safety = {}

    runtime_passed = (
        proc.returncode == 0
        and parsed.get("schema") == "h1mekartx.metal_reference_workload_runtime.v1"
        and parsed.get("validationPassed") is True
        and expected.issubset(got)
        and safety.get("usesExistingSystemMetalDeviceOnly") is True
        and safety.get("rtx5070MetalAccelerationAttempt") is False
        and safety.get("performsMMIOReads") is False
        and safety.get("performsMMIOWrites") is False
        and safety.get("mapsBARMemory") is False
        and safety.get("driverkitActivation") is False
        and safety.get("hardwareCommandSubmissionToRTX5070") is False
        and safety.get("resourceAllocationOnRTX5070") is False
    )

    return {
        "attempted": True,
        "passed": runtime_passed,
        "reason": "swift run completed and runtime report passed" if runtime_passed else "swift run failed or runtime report did not pass",
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "parsed_report": parsed,
    }


def build_report(root: Path, should_build: bool, should_run: bool) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

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

    for workload in REQUIRED_WORKLOADS:
        add(
            f"required_workload:{workload}",
            workload in source,
            "found" if workload in source else "missing",
        )

    for function in REQUIRED_FUNCTIONS:
        add(
            f"required_function:{function}",
            function in source,
            "found" if function in source else "missing",
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
        add("optional_swift_build", build["passed"] is True, build["reason"])

    runtime = maybe_run(root, should_run)
    if runtime["attempted"]:
        add("optional_swift_runtime", runtime["passed"] is True, runtime["reason"])

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_P1_ARITHMETIC_WORKLOADS_READY" if failed_count == 0 else "FAIL_P1_ARITHMETIC_WORKLOADS_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "optional_build": build,
        "optional_runtime": runtime,
        "implemented_workloads": REQUIRED_WORKLOADS,
        "p1_workloads_added": [
            "vector_multiply",
            "vector_subtract",
            "axpby",
        ],
        "safety_boundary": {
            "read_only_static_check": True,
            "optional_build_only": should_build,
            "optional_runtime_uses_existing_system_metal_device_only": should_run,
            "safe_app_level_metal_workload_implementation": True,
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
            "device_ownership_request": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_reset": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    workload_lines = [f"- `{name}`" for name in report["implemented_workloads"]]
    added_lines = [f"- `{name}`" for name in report["p1_workloads_added"]]

    return "\n".join(
        [
            "# P1 Arithmetic Workload Implementation Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Implemented Workloads",
            "",
            *workload_lines,
            "",
            "## P1 Workloads Added",
            "",
            *added_lines,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Optional Build",
            "",
            f"- Attempted: `{report['optional_build']['attempted']}`",
            f"- Passed: `{report['optional_build']['passed']}`",
            f"- Reason: `{report['optional_build']['reason']}`",
            "",
            "## Optional Runtime",
            "",
            f"- Attempted: `{report['optional_runtime']['attempted']}`",
            f"- Passed: `{report['optional_runtime']['passed']}`",
            f"- Reason: `{report['optional_runtime']['reason']}`",
            "",
            "## Safety Boundary",
            "",
            "This check validates safe app-level Metal compute workloads on the existing system Metal device only.",
            "",
            "It does not attempt RTX 5070 Metal acceleration, execute shaders on RTX 5070, submit hardware commands to RTX 5070, allocate RTX 5070 resources, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, activate DriverKit, submit System Extension requests, request device ownership, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check H1mekaRTX P1 arithmetic Metal workload implementation."
    )
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    parser.add_argument("--build", action="store_true", help="Optionally run swift build on macOS.")
    parser.add_argument("--run", action="store_true", help="Optionally run the Metal workload suite on macOS.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, args.build, args.run)

    json_path = out_dir / "p1-arithmetic-workload-implementation-report.json"
    md_path = out_dir / "p1-arithmetic-workload-implementation-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
