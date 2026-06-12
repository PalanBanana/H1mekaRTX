#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.free_account_driverkit_feasibility_matrix_check.v1"

REQUIRED_FILES = [
    "scripts/generate-free-account-driverkit-feasibility-matrix.py",
    "scripts/check-free-account-driverkit-feasibility-matrix.py",
    "docs/metal/free-account-driverkit-feasibility-matrix.md",
]

REQUIRED_TERMS = [
    "FREE_ACCOUNT_DRIVERKIT_FEASIBILITY_RESEARCH_ONLY_NO_RUNTIME",
    "free_account_official_driverkit_runtime_allowed",
    "paid_program_or_apple_granted_capability_required",
    "apple_granted_driverkit_capability_required",
    "security_reduction_is_not_capability_grant",
    "ad_hoc_signing_is_not_capability_grant",
    "rtx5070_metal_acceleration_runtime_allowed",
    "feasibility_matrix_only",
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


def run_generator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["python3", str(root / "scripts" / "generate-free-account-driverkit-feasibility-matrix.py"), "--out-dir", str(out_dir)],
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

    generator = run_generator(root, out_dir)
    add_check(checks, "generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    matrix_path = out_dir / "free-account-driverkit-feasibility-matrix.json"
    data = json.loads(matrix_path.read_text()) if matrix_path.exists() else {}

    add_check(checks, "matrix_schema", data.get("schema") == "h1mekartx.free_account_driverkit_feasibility_matrix.v1", f"schema={data.get('schema')!r}")
    add_check(checks, "matrix_decision", data.get("decision") == "FREE_ACCOUNT_DRIVERKIT_FEASIBILITY_RESEARCH_ONLY_NO_RUNTIME", f"decision={data.get('decision')!r}")
    add_check(checks, "free_account_path_available", data.get("free_account_path_available") is True, f"value={data.get('free_account_path_available')!r}")

    for key in [
        "free_account_official_driverkit_runtime_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "low_level_hardware_access_allowed",
        "rtx5070_metal_device_exposure_allowed",
        "rtx5070_metal_acceleration_runtime_allowed",
    ]:
        add_check(checks, f"blocked:{key}", data.get(key) is False, f"value={data.get(key)!r}")

    for key in [
        "paid_program_or_apple_granted_capability_required",
        "apple_granted_driverkit_capability_required",
        "security_reduction_is_not_capability_grant",
        "ad_hoc_signing_is_not_capability_grant",
    ]:
        add_check(checks, f"required_true:{key}", data.get(key) is True, f"value={data.get(key)!r}")

    target = data.get("target", {})
    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }
    for key, expected in expected_target.items():
        add_check(checks, f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    matrix = data.get("matrix", [])
    blockers = data.get("blockers", [])
    add_check(checks, "matrix_rows_present", isinstance(matrix, list) and len(matrix) >= 7, f"count={len(matrix) if isinstance(matrix, list) else 'not-list'}")
    add_check(checks, "blockers_present", isinstance(blockers, list) and len(blockers) >= 7, f"count={len(blockers) if isinstance(blockers, list) else 'not-list'}")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "read_only",
        "documentation_only",
        "feasibility_matrix_only",
        "no_runtime",
        "no_security_bypass_instructions",
        "no_driver_installation",
        "no_driver_activation",
        "no_provider_attach",
        "no_device_ownership",
        "no_low_level_hardware_access",
        "no_metal_device_exposure",
        "no_rtx5070_metal_runtime",
    ]:
        add_check(checks, f"safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_FREE_ACCOUNT_DRIVERKIT_FEASIBILITY_MATRIX_READY" if failed_count == 0 else "FAIL_FREE_ACCOUNT_DRIVERKIT_FEASIBILITY_MATRIX",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "feasibility_matrix_only": True,
            "no_runtime": True,
            "no_security_bypass_instructions": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_low_level_hardware_access": True,
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
            "# Free-account DriverKit Feasibility Matrix Check",
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
            "This check validates the free-account feasibility matrix only. It adds no runtime, no bypass instructions, no driver activation, no provider transition, no device ownership transition, no low-level hardware access, and no RTX 5070 Metal runtime.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check free-account DriverKit feasibility matrix.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "free-account-driverkit-feasibility-matrix-check.json"
    md_path = out_dir / "free-account-driverkit-feasibility-matrix-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
