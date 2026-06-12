#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_status_schema_check.v1"

REQUIRED_FILES = [
    "scripts/generate-host-app-status-schema.py",
    "scripts/check-host-app-status-schema.py",
    "docs/metal/host-app-status-schema.md",
]

REQUIRED_TERMS = [
    "HOST_APP_STATUS_SCHEMA_READY_LOCAL_REPORT_ONLY",
    "host_app_status_schema_ready",
    "local_report_only",
    "live_system_queries_allowed",
    "runtime_buttons_enabled",
    "activation_runtime_transition_allowed",
    "activation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "schema_only",
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

REQUIRED_FALSE_KEYS = [
    "live_system_queries_allowed",
    "runtime_buttons_enabled",
    "activation_runtime_transition_allowed",
    "activation_controller_runtime_allowed",
    "activation_request_allowed",
    "deactivation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
]

REQUIRED_FALSE_SAFETY = [
    "runtime_buttons_enabled",
    "live_system_queries",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "implements_activation_controller_runtime_path",
    "creates_driverkit_target",
    "adds_dext_provider_class",
    "adds_info_plist_provider_match",
    "driverkit_activation",
    "driverkit_dext_installation",
    "device_ownership_request",
    "pci_provider_attach",
    "live_provider_state_query",
    "live_extension_status_query",
    "live_pci_probing",
    "runs_ioreg",
    "runs_system_profiler",
    "performs_pci_config_reads",
    "performs_pci_config_writes",
    "performs_mmio_reads",
    "performs_mmio_writes",
    "maps_bar_memory",
    "bar_poking",
    "rtx5070_metal_acceleration_implementation",
    "rtx5070_shader_execution",
    "hardware_command_submission_to_rtx5070",
    "resource_allocation_on_rtx5070",
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
        ["python3", str(root / "scripts" / "generate-host-app-status-schema.py"), "--out-dir", str(out_dir)],
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

    source = "\n".join(
        [
            read_text(root / "scripts" / "generate-host-app-status-schema.py"),
            read_text(root / "scripts" / "check-host-app-status-schema.py"),
            read_text(root / "docs" / "metal" / "host-app-status-schema.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add_check(checks, "generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    schema_path = out_dir / "host-app-status-schema.json"
    data = json.loads(schema_path.read_text()) if schema_path.exists() else {}

    add_check(checks, "schema_id", data.get("schema") == "h1mekartx.host_app_status_schema.v1", f"schema={data.get('schema')!r}")
    add_check(checks, "schema_decision", data.get("decision") == "HOST_APP_STATUS_SCHEMA_READY_LOCAL_REPORT_ONLY", f"decision={data.get('decision')!r}")
    add_check(checks, "schema_ready", data.get("host_app_status_schema_ready") is True, f"value={data.get('host_app_status_schema_ready')!r}")
    add_check(checks, "local_report_only", data.get("local_report_only") is True, f"value={data.get('local_report_only')!r}")

    for key in REQUIRED_FALSE_KEYS:
        add_check(checks, f"blocked:{key}", data.get(key) is False, f"value={data.get(key)!r}")

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

    fields = data.get("status_fields", [])
    add_check(
        checks,
        "status_fields_present",
        isinstance(fields, list) and len(fields) >= 8,
        f"count={len(fields) if isinstance(fields, list) else 'not-list'}",
    )

    field_names = {item.get("field") for item in fields if isinstance(item, dict)}
    for field in [
        "project_status",
        "provider_match_status",
        "activation_status",
        "entitlement_evidence_status",
        "bundle_identity_status",
        "hardware_access_status",
        "status_source",
    ]:
        add_check(checks, f"field_present:{field}", field in field_names, "present" if field in field_names else "missing")

    example = data.get("status_example", {})
    add_check(
        checks,
        "status_example_local_only",
        isinstance(example, dict) and example.get("status_source") == "LOCAL_GENERATED_REPORTS_ONLY",
        f"value={example.get('status_source') if isinstance(example, dict) else None!r}",
    )

    input_reports = data.get("input_reports", [])
    add_check(
        checks,
        "input_reports_present",
        isinstance(input_reports, list) and len(input_reports) >= 9,
        f"count={len(input_reports) if isinstance(input_reports, list) else 'not-list'}",
    )

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add_check(checks, "safety_schema_only", sb.get("schema_only") is True, f"value={sb.get('schema_only')!r}")
    add_check(checks, "safety_local_report_only", sb.get("local_report_only") is True, f"value={sb.get('local_report_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add_check(checks, f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_HOST_APP_STATUS_SCHEMA_READY" if failed_count == 0 else "FAIL_HOST_APP_STATUS_SCHEMA",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "schema_only": True,
            "local_report_only": True,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "creates_driverkit_target": False,
            "device_ownership_request": False,
            "pci_provider_attach": False,
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

    return "\n".join(
        [
            "# Host-app Status Schema Check",
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
            "This check validates the host-app status schema using local generated JSON only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX host-app status schema.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "host-app-status-schema-check.json"
    md_path = out_dir / "host-app-status-schema-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
