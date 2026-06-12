#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_no_runtime_static_contract_check.v1"

REQUIRED_FILES = [
    "scripts/validate-swiftui-no-runtime-static-contract.py",
    "scripts/check-swiftui-no-runtime-static-contract.py",
    "docs/metal/swiftui-no-runtime-static-contract.md",
]

REQUIRED_TERMS = [
    "PASS_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT",
    "swiftui_static_contract_valid",
    "optional_swift_build_probe",
    "actual_app_code_started",
    "no_runtime",
    "local_status_placeholders_only",
    "runtime_buttons_enabled",
    "live_system_queries_allowed",
    "activation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["sub", "process.run([\"live registry tool\""]),
    "".join(["sub", "process.run([\"live profiler tool\""]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_command(args: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "args": args,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-5000:],
        "stderr": proc.stderr[-5000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    validator_run = run_command(
        [
            "python3",
            str(root / "scripts" / "validate-swiftui-no-runtime-static-contract.py"),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
        root,
    )
    add_check(checks, "validator_returncode", validator_run["returncode"] == 0, f"returncode={validator_run['returncode']}")

    report_path = out_dir / "swiftui-no-runtime-static-contract-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "contract_schema", report.get("schema") == "h1mekartx.swiftui_no_runtime_static_contract.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "contract_decision", report.get("decision") == "PASS_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT", f"decision={report.get('decision')!r}")
    add_check(checks, "contract_failed_count_zero", report.get("failed_count") == 0, f"failed_count={report.get('failed_count')!r}")
    add_check(checks, "contract_valid", report.get("swiftui_static_contract_valid") is True, f"value={report.get('swiftui_static_contract_valid')!r}")
    add_check(checks, "actual_app_code_started", report.get("actual_app_code_started") is True, f"value={report.get('actual_app_code_started')!r}")
    add_check(checks, "no_runtime", report.get("no_runtime") is True, f"value={report.get('no_runtime')!r}")

    for key in [
        "runtime_buttons_enabled",
        "live_system_queries_allowed",
        "activation_runtime_transition_allowed",
        "activation_controller_runtime_allowed",
        "activation_request_allowed",
        "deactivation_request_allowed",
        "manager_submit_allowed",
        "driverkit_target_creation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add_check(checks, f"contract_blocks:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    target = report.get("target", {})
    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }
    for key, expected in expected_target.items():
        add_check(checks, f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    build_probe = report.get("optional_swift_build_probe", {})
    add_check(
        checks,
        "optional_build_probe_status_allowed",
        isinstance(build_probe, dict) and build_probe.get("status") in ["SKIPPED_DISABLED", "SKIPPED_SWIFT_NOT_FOUND", "PASS"],
        f"status={build_probe.get('status') if isinstance(build_probe, dict) else None!r}",
    )

    sb = report.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key, expected in [
        ("read_only", True),
        ("static_source_scan_only", True),
        ("optional_build_probe_only", True),
        ("swiftui_source_only", True),
        ("no_runtime", True),
        ("local_status_placeholders_only", True),
    ]:
        add_check(checks, f"safety_true:{key}", sb.get(key) is expected, f"value={sb.get(key)!r}")

    for key in [
        "runtime_buttons_enabled",
        "live_system_queries",
        "creates_activation_request_objects",
        "creates_deactivation_request_objects",
        "calls_extension_manager_submit",
        "implements_activation_controller_runtime_path",
        "creates_driverkit_target",
        "driverkit_activation",
        "driverkit_dext_installation",
        "device_ownership_request",
        "pci_provider_attach",
        "performs_pci_config_reads",
        "performs_pci_config_writes",
        "performs_mmio_reads",
        "performs_mmio_writes",
        "maps_bar_memory",
        "rtx5070_metal_acceleration_implementation",
        "rtx5070_shader_execution",
        "hardware_command_submission_to_rtx5070",
        "resource_allocation_on_rtx5070",
    ]:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_SWIFTUI_NO_RUNTIME_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "validator_run": validator_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "static_source_scan_only": True,
            "optional_build_probe_only": True,
            "swiftui_source_only": True,
            "no_runtime": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "creates_driverkit_target": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
            "performs_live registry tool": False,
            "performs_live profiler tool": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "rtx5070_metal_acceleration_implementation": False,
            "rtx5070_shader_execution": False,
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        rows.append(f"| `{item['name']}` | {status} | {item['detail'].replace('|', '\\|')} |")

    return "\n".join(
        [
            "# SwiftUI No-runtime Static Contract Check",
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
            "This check validates the SwiftUI no-runtime static contract.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, touch low-level hardware access paths, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SwiftUI no-runtime static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "swiftui-no-runtime-static-contract-check.json"
    md_path = out_dir / "swiftui-no-runtime-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
