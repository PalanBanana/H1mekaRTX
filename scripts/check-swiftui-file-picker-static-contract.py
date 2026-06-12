#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_file_picker_static_contract_check.v1"

REQUIRED_FILES = [
    "scripts/validate-swiftui-file-picker-static-contract.py",
    "scripts/check-swiftui-file-picker-static-contract.py",
    "docs/metal/swiftui-file-picker-static-contract.md",
]

REQUIRED_TERMS = [
    "PASS_SWIFTUI_FILE_PICKER_STATIC_CONTRACT",
    "file_picker_static_contract_valid",
    "optional_swift_build_probe",
    "local_file_only",
    "json_only",
    "no_runtime",
    "driver_installation_allowed",
    "driver_activation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "rtx5070_metal_runtime_allowed",
]

FORBIDDEN_LITERAL_TERMS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
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

    for token in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{token}", token not in source, "absent" if token not in source else "present")

    validator_run = run_command(
        [
            "python3",
            str(root / "scripts" / "validate-swiftui-file-picker-static-contract.py"),
            "--root",
            str(root),
            "--out-dir",
            str(out_dir),
        ],
        root,
    )
    add_check(checks, "validator_returncode", validator_run["returncode"] == 0, f"returncode={validator_run['returncode']}")

    report_path = out_dir / "swiftui-file-picker-static-contract-report.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}

    add_check(checks, "contract_schema", report.get("schema") == "h1mekartx.swiftui_file_picker_static_contract.v1", f"schema={report.get('schema')!r}")
    add_check(checks, "contract_decision", report.get("decision") == "PASS_SWIFTUI_FILE_PICKER_STATIC_CONTRACT", f"decision={report.get('decision')!r}")
    add_check(checks, "contract_failed_count_zero", report.get("failed_count") == 0, f"failed_count={report.get('failed_count')!r}")
    add_check(checks, "contract_valid", report.get("file_picker_static_contract_valid") is True, f"value={report.get('file_picker_static_contract_valid')!r}")
    add_check(checks, "local_file_only", report.get("local_file_only") is True, f"value={report.get('local_file_only')!r}")
    add_check(checks, "json_only", report.get("json_only") is True, f"value={report.get('json_only')!r}")

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
        add_check(checks, f"contract_blocks:{key}", report.get(key) is False, f"value={report.get(key)!r}")

    probe = report.get("optional_swift_build_probe", {})
    add_check(
        checks,
        "optional_build_probe_status_allowed",
        isinstance(probe, dict) and probe.get("status") in ["SKIPPED_DISABLED", "SKIPPED_SWIFT_NOT_FOUND", "PASS"],
        f"status={probe.get('status') if isinstance(probe, dict) else None!r}",
    )

    sb = report.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "static_source_scan_only",
        "optional_build_probe_only",
        "swiftui_source_only",
        "file_picker_contract_only",
        "local_file_only",
        "json_only",
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
        "decision": "PASS_SWIFTUI_FILE_PICKER_STATIC_CONTRACT_READY" if failed_count == 0 else "FAIL_SWIFTUI_FILE_PICKER_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "validator_run": validator_run,
        "safety_boundary": {
            "read_only_static_check": True,
            "static_source_scan_only": True,
            "optional_build_probe_only": True,
            "swiftui_source_only": True,
            "file_picker_contract_only": True,
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
            "# SwiftUI File-picker Static Contract Check",
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
            "This check validates SwiftUI file-picker source and an optional Swift build probe only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SwiftUI file-picker static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "swiftui-file-picker-static-contract-check.json"
    md_path = out_dir / "swiftui-file-picker-static-contract-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
