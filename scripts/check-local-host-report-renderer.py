#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.local_host_report_renderer_check.v1"

REQUIRED_FILES = [
    "scripts/render-host-status-report.py",
    "docs/metal/local-host-report-renderer.md",
]

REQUIRED_TERMS = [
    "PASS_LOCAL_HOST_REPORT_RENDERED",
    "render_markdown",
    "build_renderer_report",
    "local_file_read_only",
    "queries_live_extension_state",
    "driverkit_activation",
    "performs_mmio_reads",
    "performs_mmio_writes",
    "maps_bar_memory",
    "rtx5070_metal_acceleration_implementation",
]

FORBIDDEN_TERMS = [
    "OSSystem" + "ExtensionRequest",
    "OSSystem" + "ExtensionManager",
    "IOPCI" + "Device",
    "Configuration" + "Write",
    "Memory" + "Read",
    "Memory" + "Write",
    "sub" + "process.run([\"ioreg\"",
    "sub" + "process.run([\"system_profiler\"",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture(path: Path) -> None:
    fixture = {
        "schema": "h1mekartx.host_status_report.v1",
        "decision": "HOST_APP_SKELETON_READY_NO_ACTIVATION",
        "generatedAtUTC": "2026-06-11T00:00:00Z",
        "target": {
            "gpu": "NVIDIA RTX 5070",
            "vendorID": "0x10de",
            "deviceID": "0x2f04",
            "iopcimatch": "0x2f0410de",
            "subsystemVendorID": "0x1458",
            "subsystemID": "0x417e",
        },
        "hostState": {
            "hostSkeletonPresent": True,
            "activationControllerImplemented": False,
            "driverExtensionTargetIncluded": False,
            "activationRequestSubmitted": False,
            "deactivationRequestSubmitted": False,
            "managerSubmitCalled": False,
            "deviceOwnershipRequested": False,
            "metalReferenceWorkloadLauncherPlanned": True,
        },
        "plannedPanels": [
            "status",
            "safety-boundary",
            "metal-reference-workloads",
            "diagnostics-export",
        ],
        "safetyBoundary": {
            "existingSystemMetalDeviceValidationOnly": True,
            "rtx5070MetalAccelerationImplementation": False,
            "rtx5070ShaderExecution": False,
            "hardwareCommandSubmission": False,
            "rtx5070ResourceAllocation": False,
            "pciConfigReads": False,
            "pciConfigWrites": False,
            "mmioReads": False,
            "mmioWrites": False,
            "barMapping": False,
            "barPoking": False,
            "driverActivation": False,
            "systemExtensionActivationRequest": False,
            "systemExtensionDeactivationRequest": False,
            "systemExtensionManagerSubmit": False,
            "deviceOwnershipRequest": False,
            "firmwareLoading": False,
            "gspInitialization": False,
            "displayEngineInitialization": False,
            "framebufferInitialization": False,
            "gpuResetLogic": False,
        },
    }

    path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n")


def run_fixture(root: Path, out_dir: Path) -> dict[str, Any]:
    fixture_dir = out_dir / "fixture"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    fixture_path = fixture_dir / "host-status-fixture.json"
    render_out = fixture_dir / "rendered"
    render_out.mkdir(parents=True, exist_ok=True)

    write_fixture(fixture_path)

    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "render-host-status-report.py"),
            "--input",
            str(fixture_path),
            "--out-dir",
            str(render_out),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    report_path = render_out / "local-host-report-renderer-report.json"
    report = {}
    if report_path.exists():
        report = json.loads(report_path.read_text())

    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "fixture_path": str(fixture_path),
        "render_out": str(render_out),
        "report": report,
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
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

    source = read_text(root / "scripts" / "render-host-status-report.py")

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

    fixture_result = run_fixture(root, out_dir)
    fixture_report = fixture_result.get("report", {})

    add(
        "fixture_renderer_returncode",
        fixture_result["returncode"] == 0,
        f"returncode={fixture_result['returncode']}",
    )
    add(
        "fixture_renderer_decision",
        fixture_report.get("decision") == "PASS_LOCAL_HOST_REPORT_RENDERED",
        f"decision={fixture_report.get('decision')!r}",
    )
    add(
        "fixture_renderer_failed_count",
        fixture_report.get("failed_count") == 0,
        f"failed_count={fixture_report.get('failed_count')!r}",
    )

    safety = fixture_report.get("safety_boundary", {})
    if not isinstance(safety, dict):
        safety = {}

    for key in [
        "queries_live_extension_state",
        "driverkit_activation",
        "system_extension_activation_request",
        "system_extension_deactivation_request",
        "extension_manager_submit_request",
        "device_ownership_request",
        "performs_mmio_reads",
        "performs_mmio_writes",
        "maps_bar_memory",
        "rtx5070_metal_acceleration_implementation",
        "rtx5070_shader_execution",
        "hardware_command_submission",
        "resource_allocation_on_rtx5070",
    ]:
        add(
            f"fixture_safety_false:{key}",
            safety.get(key) is False,
            f"value={safety.get(key)!r}",
        )

    add(
        "fixture_local_file_read_only",
        safety.get("local_file_read_only") is True,
        f"value={safety.get('local_file_read_only')!r}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_LOCAL_HOST_REPORT_RENDERER_READY" if failed_count == 0 else "FAIL_LOCAL_HOST_REPORT_RENDERER_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "fixture_result": fixture_result,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_fixture_only": True,
            "runs_renderer_on_local_json": True,
            "queries_live_extension_state": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
            "device_ownership_request": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission": False,
            "resource_allocation_on_rtx5070": False,
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
            "# Local Host Report Renderer Check",
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
            "## Safety Boundary",
            "",
            "This check validates a local-only host report renderer using a local fixture JSON file.",
            "",
            "It does not query live extension state, add System Extension request code, activate DriverKit, submit activation or deactivation requests, submit extension manager requests, request device ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the H1mekaRTX local host report renderer."
    )
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "local-host-report-renderer-report.json"
    md_path = out_dir / "local-host-report-renderer-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
