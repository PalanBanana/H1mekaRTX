#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.workload_schema_regression_sync_check.v1"

EXPECTED_WORKLOADS = {
    "vector_add",
    "saxpy",
    "square",
    "vector_multiply",
    "vector_subtract",
    "axpby",
}

EXPECTED_FUNCTIONS = {
    "h1meka_vector_add",
    "h1meka_saxpy",
    "h1meka_square",
    "h1meka_vector_multiply",
    "h1meka_vector_subtract",
    "h1meka_axpby",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def run_generator(root: Path, script: str, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ["python3", str(root / "scripts" / script), "--out-dir", str(out_dir)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "script": script,
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def build_report(root: Path, out_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    source = "\n".join(
        [
            read_text(root / "tools/metal-validation-harness/Sources/H1mekaMetalValidation/main.swift"),
            read_text(root / "tools/metal-validation-harness/Sources/H1mekaMetalValidation/Shaders/reference_workloads.metal"),
            read_text(root / "scripts/generate-metal-workload-result-schema.py"),
            read_text(root / "scripts/generate-metal-workload-regression-manifest.py"),
            read_text(root / "docs/metal/metal-workload-result-schema.md"),
            read_text(root / "docs/metal/metal-workload-regression-manifest.md"),
        ]
    )

    for name in sorted(EXPECTED_WORKLOADS):
        add(f"expected_workload_present:{name}", name in source, "found" if name in source else "missing")

    for name in sorted(EXPECTED_FUNCTIONS):
        add(f"expected_function_present:{name}", name in source, "found" if name in source else "missing")

    forbidden_terms = [
        "IOPCI" + "Device",
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "Configuration" + "Write",
        "Memory" + "Read",
        "Memory" + "Write",
        "sub" + "process.run([\"ioreg\"",
        "sub" + "process.run([\"system_profiler\"",
    ]

    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    schema_run = run_generator(root, "generate-metal-workload-result-schema.py", out_dir)
    manifest_run = run_generator(root, "generate-metal-workload-regression-manifest.py", out_dir)

    add("schema_generator_returncode", schema_run["returncode"] == 0, f"returncode={schema_run['returncode']}")
    add("manifest_generator_returncode", manifest_run["returncode"] == 0, f"returncode={manifest_run['returncode']}")

    schema_path = out_dir / "metal-workload-result-schema.json"
    manifest_path = out_dir / "metal-workload-regression-manifest.json"

    schema_data = json.loads(schema_path.read_text()) if schema_path.exists() else {}
    manifest_data = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    schema_workloads = {item.get("name") for item in schema_data.get("workload_catalog", []) if isinstance(item, dict)}
    manifest_workloads = {item.get("name") for item in manifest_data.get("regression_cases", []) if isinstance(item, dict)}

    add("schema_decision_synced", schema_data.get("decision") == "METAL_WORKLOAD_RESULT_SCHEMA_SYNCED_WITH_P1", f"decision={schema_data.get('decision')!r}")
    add("manifest_decision_synced", manifest_data.get("decision") == "METAL_WORKLOAD_REGRESSION_MANIFEST_SYNCED_WITH_P1", f"decision={manifest_data.get('decision')!r}")
    add("schema_has_six_workloads", EXPECTED_WORKLOADS.issubset(schema_workloads), f"workloads={sorted(schema_workloads)}")
    add("manifest_has_six_workloads", EXPECTED_WORKLOADS.issubset(manifest_workloads), f"workloads={sorted(manifest_workloads)}")
    add("schema_workload_count", schema_data.get("workload_count") == 6, f"workload_count={schema_data.get('workload_count')!r}")
    add("manifest_case_count", manifest_data.get("regression_case_count") == 6, f"regression_case_count={manifest_data.get('regression_case_count')!r}")

    schema_sb = schema_data.get("safety_boundary", {})
    manifest_sb = manifest_data.get("safety_boundary", {})
    if not isinstance(schema_sb, dict):
        schema_sb = {}
    if not isinstance(manifest_sb, dict):
        manifest_sb = {}

    for prefix, sb in [("schema", schema_sb), ("manifest", manifest_sb)]:
        add(f"{prefix}_existing_system_metal_only", sb.get("uses_existing_system_metal_device_only") is True, f"value={sb.get('uses_existing_system_metal_device_only')!r}")
        add(f"{prefix}_p1_documented", sb.get("p1_workloads_documented") is True, f"value={sb.get('p1_workloads_documented')!r}")
        for key in [
            "rtx5070_metal_acceleration_attempt",
            "rtx5070_shader_execution",
            "hardware_command_submission_to_rtx5070",
            "resource_allocation_on_rtx5070",
            "performs_mmio_reads",
            "performs_mmio_writes",
            "maps_bar_memory",
            "driverkit_activation",
            "system_extension_activation_request",
            "device_ownership_request",
        ]:
            add(f"{prefix}_safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_WORKLOAD_SCHEMA_REGRESSION_SYNCED_WITH_P1" if failed_count == 0 else "FAIL_WORKLOAD_SCHEMA_REGRESSION_SYNC",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "expected_workloads": sorted(EXPECTED_WORKLOADS),
        "expected_functions": sorted(EXPECTED_FUNCTIONS),
        "generator_runs": [schema_run, manifest_run],
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "uses_existing_system_metal_device_only": True,
            "p1_workloads_documented": True,
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
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    workloads = [f"- `{name}`" for name in report["expected_workloads"]]

    return "\n".join(
        [
            "# Workload Schema and Regression Sync Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Expected Workloads",
            "",
            *workloads,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates that the schema and regression manifest are synced with the Stage 35 P1 workloads.",
            "",
            "It does not attempt RTX 5070 Metal acceleration, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, activate DriverKit, submit System Extension requests, request device ownership, load firmware, initialize GSP, initialize display engine, initialize framebuffer, or run GPU reset logic.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX workload schema/regression sync.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "workload-schema-regression-sync-report.json"
    md_path = out_dir / "workload-schema-regression-sync-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
