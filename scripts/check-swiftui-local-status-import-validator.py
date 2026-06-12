#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_local_status_import_validator_check.v1"

REQUIRED_FILES = [
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalStatusImportPolicy.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalStatusImportValidator.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/Resources/sample-imported-host-status.json",
    "scripts/generate-swiftui-local-status-import-validator-report.py",
    "scripts/check-swiftui-local-status-import-validator.py",
    "docs/metal/swiftui-local-status-import-validator.md",
]

REQUIRED_TERMS = [
    "SWIFTUI_LOCAL_STATUS_IMPORT_VALIDATOR_READY",
    "LocalStatusImportPolicy",
    "LocalStatusImportValidator",
    "LocalStatusImportResult",
    "LOCAL_IMPORTED_REPORT_ONLY",
    "local_status_import_validator_ready",
    "local_json_only",
    "rtx5070_metal_runtime_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["IOPCI", "Device"]),
    "".join(["map", "DeviceMemory"]),
    "".join(["Create", "MemoryMap"]),
    "".join(["sub", "process.run([\"ioreg\""]),
    "".join(["sub", "process.run([\"system_profiler\""]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def run_report(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-swiftui-local-status-import-validator-report.py"),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
        cwd=root,
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

    for rel in REQUIRED_FILES:
        path = root / rel
        add_check(checks, f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    sample_path = root / "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/Resources/sample-imported-host-status.json"
    sample = json.loads(sample_path.read_text()) if sample_path.exists() else {}

    add_check(checks, "sample_schema", sample.get("schema") == "h1mekartx.host_app_status_model.v1", f"schema={sample.get('schema')!r}")
    add_check(checks, "sample_status_source", sample.get("statusSource") == "LOCAL_IMPORTED_REPORT_ONLY", f"value={sample.get('statusSource')!r}")
    add_check(checks, "sample_project_status", sample.get("projectStatus") == "RESEARCH_ONLY", f"value={sample.get('projectStatus')!r}")
    add_check(checks, "sample_provider_status", sample.get("providerMatchStatus") == "NO_GO", f"value={sample.get('providerMatchStatus')!r}")
    add_check(checks, "sample_activation_status", sample.get("activationStatus") == "NO_GO", f"value={sample.get('activationStatus')!r}")
    add_check(checks, "sample_hardware_status", sample.get("hardwareAccessStatus") == "BLOCKED", f"value={sample.get('hardwareAccessStatus')!r}")

    report_run = run_report(root, out_dir)
    add_check(checks, "report_generator_returncode", report_run["returncode"] == 0, f"returncode={report_run['returncode']}")

    report_path = out_dir / "swiftui-local-status-import-validator-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "report_schema", report.get("schema") == "h1mekartx.swiftui_local_status_import_validator.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "report_decision", report.get("decision") == "SWIFTUI_LOCAL_STATUS_IMPORT_VALIDATOR_READY", f"decision={report.get('decision')!r}")
    add_check(checks, "validator_ready", report.get("local_status_import_validator_ready") is True, f"value={report.get('local_status_import_validator_ready')!r}")
    add_check(checks, "local_json_only", report.get("local_json_only") is True, f"value={report.get('local_json_only')!r}")

    for key in [
        "live_system_queries_allowed",
        "runtime_buttons_enabled",
        "driver_runtime_allowed",
        "driver_installation_allowed",
        "driver_activation_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "low_level_hardware_path_allowed",
        "rtx5070_metal_runtime_allowed",
    ]:
        add_check(checks, f"blocked:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    sb = report.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "swiftui_source_only",
        "local_status_import_validation_only",
        "local_json_only",
        "no_runtime",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_path",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_SWIFTUI_LOCAL_STATUS_IMPORT_VALIDATOR_READY" if failed_count == 0 else "FAIL_SWIFTUI_LOCAL_STATUS_IMPORT_VALIDATOR",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "report_run": report_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "swiftui_source_only": True,
            "local_status_import_validation_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True,
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
            "# SwiftUI Local Status Import Validator Check",
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
            "This check validates local status import logic only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SwiftUI local status import validator.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "swiftui-local-status-import-validator-check.json"
    md_path = out_dir / "swiftui-local-status-import-validator-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
