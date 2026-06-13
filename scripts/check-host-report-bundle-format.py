#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_report_bundle_format_check.v1"

REQUIRED_FILES = [
    "scripts/generate-host-report-bundle-format.py",
    "docs/metal/host-report-bundle-format.md",
]

REQUIRED_LAYOUT_PATHS = [
    "bundle.json",
    "README.md",
    "reports/metal-workload-runtime.json",
    "reports/metal-workload-result-schema.json",
    "reports/metal-workload-regression-manifest.json",
    "reports/host-status.json",
    "reports/host-diagnostics-summary.json",
    "reports/host-diagnostics-summary.md",
    "reports/bar-inventory-summary.json",
    "reports/bar-inventory-summary.md",
    "reports/ui-compositor-proof-schema.json",
    "reports/ui-compositor-proof-schema.md",
    "reports/ui-compositor-sample-summary.json",
    "reports/ui-compositor-sample-summary.md",
    "reports/ui-compositor-readiness-matrix.json",
    "reports/ui-compositor-readiness-matrix.md",
    "reports/ui-gpu-attribution-summary.json",
    "reports/ui-gpu-attribution-summary.md",
    "reports/rendered-host-status-report.md",
    "reports/safety-gates.md",
]

REQUIRED_SAFETY_FALSE = [
    "host_gui_implementation",
    "live_extension_status_query",
    "system_extension_activation_request",
    "system_extension_deactivation_request",
    "extension_manager_submit_request",
    "driverkit_activation",
    "device_ownership_request",
    "rtx5070_metal_acceleration_attempt",
    "rtx5070_shader_execution",
    "hardware_command_submission_to_rtx5070",
    "resource_allocation_on_rtx5070",
    "live_pci_probing",
    "runs_ioreg",
    "runs_system_profiler",
    "performs_pci_config_reads",
    "performs_pci_config_writes",
    "performs_mmio_reads",
    "performs_mmio_writes",
    "maps_bar_memory",
    "bar_poking",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def run_generator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["python3", str(root / "scripts" / "generate-host-report-bundle-format.py"), "--out-dir", str(out_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    for rel in REQUIRED_FILES:
        path = root / rel
        add(f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(
        [
            read_text(root / "scripts" / "generate-host-report-bundle-format.py"),
            read_text(root / "docs" / "metal" / "host-report-bundle-format.md"),
        ]
    )

    required_terms = [
        "HOST_REPORT_BUNDLE_FORMAT_READY",
        "LOCAL_ONLY_REPORT_BUNDLE",
        "h1mekartx.host_report_bundle.v1",
        "local_files_only",
        "noLiveExtensionQuery",
        "noSystemExtensionRequests",
        "noDriverKitActivation",
        "noDeviceOwnershipRequest",
        "noPCIConfigAccess",
        "noMMIOAccess",
        "noBARMapping",
        "noRTX5070Acceleration",
    ]

    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "IOPCI" + "Device",
        "Configuration" + "Write",
        "Memory" + "Read",
        "Memory" + "Write",
        "sub" + "process.run([\"ioreg\"",
        "sub" + "process.run([\"system_profiler\"",
    ]

    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    format_path = out_dir / "host-report-bundle-format.json"
    data = json.loads(format_path.read_text()) if format_path.exists() else {}

    add("format_schema", data.get("schema") == "h1mekartx.host_report_bundle_format.v1", f"schema={data.get('schema')!r}")
    add("format_decision", data.get("decision") == "HOST_REPORT_BUNDLE_FORMAT_READY", f"decision={data.get('decision')!r}")
    add("bundle_type", data.get("bundle_type") == "LOCAL_ONLY_REPORT_BUNDLE", f"bundle_type={data.get('bundle_type')!r}")
    add("real_acceleration_not_started", data.get("real_acceleration_production_started") is False, f"value={data.get('real_acceleration_production_started')!r}")
    add("real_acceleration_not_allowed", data.get("real_acceleration_production_allowed") is False, f"value={data.get('real_acceleration_production_allowed')!r}")

    layout_paths = {item.get("path") for item in data.get("bundle_layout", []) if isinstance(item, dict)}
    for rel in REQUIRED_LAYOUT_PATHS:
        add(f"layout_path:{rel}", rel in layout_paths, "present" if rel in layout_paths else "missing")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add("safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add("safety_format_only", sb.get("format_only") is True, f"value={sb.get('format_only')!r}")
    add("safety_local_files_only", sb.get("local_files_only") is True, f"value={sb.get('local_files_only')!r}")

    for key in REQUIRED_SAFETY_FALSE:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_HOST_REPORT_BUNDLE_FORMAT_READY" if failed_count == 0 else "FAIL_HOST_REPORT_BUNDLE_FORMAT_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "required_layout_paths": REQUIRED_LAYOUT_PATHS,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "format_only": True,
            "local_files_only": True,
            "host_gui_implementation": False,
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
            "hardware_command_submission_to_rtx5070": False,
            "resource_allocation_on_rtx5070": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    paths = [f"- `{path}`" for path in report["required_layout_paths"]]

    return "\n".join(
        [
            "# Host Report Bundle Format Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Required Layout Paths",
            "",
            *paths,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates a local-only host report bundle format.",
            "",
            "It does not query live extension state, add System Extension request code, activate DriverKit, submit activation or deactivation requests, submit extension manager requests, request device ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX host report bundle format.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "host-report-bundle-format-check.json"
    md_path = out_dir / "host-report-bundle-format-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
