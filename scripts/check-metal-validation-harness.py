#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.metal_validation_harness_check.v1"

REQUIRED_FILES = [
    "tools/metal-validation-harness/Package.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/main.swift",
    "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/vector_add.metal",
    "docs/metal/metal-validation-harness.md",
]

REQUIRED_SOURCE_TERMS = [
    "MTLCreateSystemDefaultDevice",
    "makeCommandQueue",
    "makeCommandBuffer",
    "makeComputePipelineState",
    "makeComputeCommandEncoder",
    "dispatchThreads",
    "usesExistingSystemMetalDeviceOnly",
    "rtx5070MetalAccelerationAttempt: false",
    "performsMMIOReads: false",
    "performsMMIOWrites: false",
    "driverkitActivation: false",
]

FORBIDDEN_SOURCE_TERMS = [
    "IOPCIDevice",
    "ConfigurationWrite",
    "MemoryRead",
    "MemoryWrite",
    "IOAccelerator",
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
            "reason": "Metal validation harness build is only attempted on macOS",
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
            read_text(root / "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/vector_add.metal"),
        ]
    )

    for term in REQUIRED_SOURCE_TERMS:
        add(
            f"required_source_term:{term}",
            term in source,
            "found" if term in source else "missing",
        )

    for term in FORBIDDEN_SOURCE_TERMS:
        add(
            f"forbidden_source_term_absent:{term}",
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
        "decision": "PASS_METAL_VALIDATION_HARNESS_READY" if failed_count == 0 else "FAIL_METAL_VALIDATION_HARNESS_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "optional_build": build,
        "safety_boundary": {
            "read_only_static_check": True,
            "optional_build_only": should_build,
            "uses_existing_system_metal_device_only": True,
            "rtx5070_metal_acceleration_attempt": False,
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
            "driverkit_activation": False,
            "private_graphics_framework_patching": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Metal Validation Harness Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
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
            "## Safety Boundary",
            "",
            "This check validates the Metal validation harness source tree.",
            "",
            "The harness is limited to the existing system Metal device and does not attempt RTX 5070 Metal acceleration, PCI config-space access, MMIO access, BAR mapping, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, DriverKit activation, or private graphics framework patching.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the H1mekaRTX Metal validation harness skeleton."
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

    json_path = out_dir / "metal-validation-harness-report.json"
    md_path = out_dir / "metal-validation-harness-report.md"

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
