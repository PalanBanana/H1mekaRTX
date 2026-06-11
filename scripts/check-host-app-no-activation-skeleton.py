#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_no_activation_skeleton_check.v1"

REQUIRED_FILES = [
    "tools/host-app-no-activation/Package.swift",
    "tools/host-app-no-activation/Sources/H1mekaRTXHostNoActivation/main.swift",
    "docs/metal/host-app-no-activation-skeleton.md",
]

REQUIRED_TERMS = [
    "H1mekaRTXHostNoActivationReport",
    "HOST_APP_SKELETON_READY_NO_ACTIVATION",
    "hostSkeletonPresent: true",
    "activationControllerImplemented: false",
    "driverExtensionTargetIncluded: false",
    "activationRequestSubmitted: false",
    "deactivationRequestSubmitted: false",
    "managerSubmitCalled: false",
    "deviceOwnershipRequested: false",
    "metalReferenceWorkloadLauncherPlanned: true",
    "rtx5070MetalAccelerationImplementation: false",
    "hardwareCommandSubmission: false",
    "rtx5070ResourceAllocation: false",
    "mmioReads: false",
    "mmioWrites: false",
    "barMapping: false",
    "driverActivation: false",
]

FORBIDDEN_TERMS = [
    "OSSystem" + "ExtensionRequest",
    "OSSystem" + "ExtensionManager",
    "submitRequest",
    "IOPCI" + "Device",
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
            "reason": "Swift build is only attempted on macOS",
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

    skeleton_dir = root / "tools" / "host-app-no-activation"
    proc = subprocess.run(
        ["swift", "build"],
        cwd=skeleton_dir,
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
            read_text(root / "tools/host-app-no-activation/Package.swift"),
            read_text(root / "tools/host-app-no-activation/Sources/H1mekaRTXHostNoActivation/main.swift"),
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
        add("optional_swift_build", build["passed"] is True, build["reason"])

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_HOST_APP_SKELETON_NO_ACTIVATION" if failed_count == 0 else "FAIL_HOST_APP_SKELETON_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "optional_build": build,
        "safety_boundary": {
            "read_only_static_check": True,
            "optional_build_only": should_build,
            "adds_host_app_skeleton": True,
            "adds_driverkit_dext_target": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "ossystemextensionmanager_submit_request": False,
            "iopcidevice_ownership_request": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "resource_allocation_on_rtx5070": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
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


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Host App No-activation Skeleton Check",
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
            "This check validates the no-activation host app skeleton source tree.",
            "",
            "The skeleton does not add a DriverKit dext target, System Extension request code, DriverKit activation, System Extension activation/deactivation requests, manager submit calls, IOPCIDevice ownership, PCI config-space access, MMIO access, BAR mapping, RTX 5070 shader execution, RTX 5070 resource allocation, firmware loading, display initialization, framebuffer initialization, GPU reset logic, or RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the H1mekaRTX no-activation host app skeleton."
    )
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    parser.add_argument("--build", action="store_true", help="Optionally run swift build on macOS.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, args.build)

    json_path = out_dir / "host-app-no-activation-skeleton-report.json"
    md_path = out_dir / "host-app-no-activation-skeleton-report.md"

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
