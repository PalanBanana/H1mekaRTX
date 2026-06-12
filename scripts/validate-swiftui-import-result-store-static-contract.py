#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_import_result_store_static_contract.v1"

EXPECTED_TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

SWIFT_PACKAGE_ROOT = "tools/host-app-no-runtime-swiftui"

SOURCE_FILES = [
    "tools/host-app-no-runtime-swiftui/Package.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalImportResultStore.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ImportResultStoreView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ContentView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalStatusImportValidator.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalStatusImportPolicy.swift",
]

REQUIRED_TERMS = [
    "final class LocalImportResultStore: ObservableObject",
    "@Published private(set) var latestStatus",
    "@Published private(set) var latestFileName",
    "@Published private(set) var latestMessages",
    "@Published private(set) var acceptedCount",
    "@Published private(set) var rejectedCount",
    "func record(fileName: String, result: LocalStatusImportResult)",
    "func recordSelectionOnly(fileName: String)",
    "func reset()",
    "static let sample = LocalImportResultStore",
    "struct ImportResultStoreView: View",
    "@ObservedObject var store: LocalImportResultStore",
    "ImportResultStoreView(store: .sample)",
    "ACCEPTED_LOCAL_IMPORT",
    "REJECTED_LOCAL_IMPORT",
    "SELECTED_LOCAL_FILE",
    "NO_IMPORT_RESULT",
]

FORBIDDEN_SOURCE_TOKENS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submitRequest"]),
    "".join(["OSSystem", "ExtensionManager.shared"]),
    "".join(["OSSystem", "ExtensionRequest"]),
    "".join(["IOPCI", "Device"]),
    "".join(["IOService", "GetMatchingServices"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
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


def run_optional_swift_build(root: Path) -> dict[str, Any]:
    enabled = os.environ.get("H1MEKARTX_RUN_SWIFT_BUILD", "0") == "1"
    swift_path = shutil.which("swift")

    if not enabled:
        return {
            "enabled": False,
            "status": "SKIPPED_DISABLED",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

    if not swift_path:
        return {
            "enabled": True,
            "status": "SKIPPED_SWIFT_NOT_FOUND",
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }

    proc = subprocess.run(
        [
            swift_path,
            "build",
            "--package-path",
            str(root / SWIFT_PACKAGE_ROOT),
        ],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return {
        "enabled": True,
        "status": "PASS" if proc.returncode == 0 else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout[-6000:],
        "stderr": proc.stderr[-6000:],
    }


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in SOURCE_FILES:
        path = root / rel
        add_check(checks, f"source_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in SOURCE_FILES)

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    add_check(checks, "package_root_exists", (root / SWIFT_PACKAGE_ROOT).is_dir(), SWIFT_PACKAGE_ROOT)
    add_check(checks, "package_swift_exists", (root / SWIFT_PACKAGE_ROOT / "Package.swift").is_file(), "Package.swift")
    add_check(checks, "store_source_exists", (root / "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalImportResultStore.swift").is_file(), "LocalImportResultStore.swift")
    add_check(checks, "store_view_source_exists", (root / "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ImportResultStoreView.swift").is_file(), "ImportResultStoreView.swift")

    build_probe = run_optional_swift_build(root)
    add_check(
        checks,
        "optional_swift_build_probe_status_allowed",
        build_probe["status"] in ["SKIPPED_DISABLED", "SKIPPED_SWIFT_NOT_FOUND", "PASS"],
        f"status={build_probe['status']!r}, returncode={build_probe['returncode']!r}",
    )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "target": EXPECTED_TARGET,
        "decision": "PASS_SWIFTUI_IMPORT_RESULT_STORE_STATIC_CONTRACT" if failed_count == 0 else "FAIL_SWIFTUI_IMPORT_RESULT_STORE_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "source_files": SOURCE_FILES,
        "optional_swift_build_probe": build_probe,
        "import_result_store_static_contract_valid": failed_count == 0,
        "actual_app_code_continues": True,
        "local_ui_state_only": True,
        "observable_store": True,
        "no_runtime": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "safety_boundary": {
            "read_only": True,
            "static_source_scan_only": True,
            "optional_build_probe_only": True,
            "swiftui_source_only": True,
            "local_import_result_store_contract_only": True,
            "local_ui_state_only": True,
            "observable_store_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    files = [f"- `{item}`" for item in report["source_files"]]
    probe = report["optional_swift_build_probe"]

    return "\n".join(
        [
            "# SwiftUI Import Result Store Static Contract Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Import result store static contract valid: `{report['import_result_store_static_contract_valid']}`",
            "",
            f"Actual app code continues: `{report['actual_app_code_continues']}`",
            "",
            f"Local UI state only: `{report['local_ui_state_only']}`",
            "",
            f"Observable store: `{report['observable_store']}`",
            "",
            f"No runtime: `{report['no_runtime']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"Driver runtime allowed: `{report['driver_runtime_allowed']}`",
            "",
            f"Driver installation allowed: `{report['driver_installation_allowed']}`",
            "",
            f"Driver activation allowed: `{report['driver_activation_allowed']}`",
            "",
            f"Provider attach allowed: `{report['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{report['device_ownership_allowed']}`",
            "",
            f"Low-level hardware path allowed: `{report['low_level_hardware_path_allowed']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Source Files",
            "",
            *files,
            "",
            "## Optional Swift Build Probe",
            "",
            f"- Enabled: `{probe['enabled']}`",
            f"- Status: `{probe['status']}`",
            f"- Return code: `{probe['returncode']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This validator performs static source scanning and an optional Swift build probe only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate SwiftUI import result store static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "swiftui-import-result-store-static-contract-report.json"
    md_path = out_dir / "swiftui-import-result-store-static-contract-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
