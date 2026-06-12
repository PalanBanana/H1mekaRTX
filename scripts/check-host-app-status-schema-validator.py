#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_app_status_schema_validator_check.v1"

REQUIRED_FILES = [
    "scripts/validate-host-app-status-schema.py",
    "scripts/check-host-app-status-schema-validator.py",
    "docs/metal/host-app-status-schema-validator.md",
]

REQUIRED_TERMS = [
    "PASS_HOST_APP_STATUS_SCHEMA_VALIDATION",
    "host-app-status-schema.json",
    "host-app-activation-ui-plan.json",
    "activation-controller-transition-gate-report.json",
    "provider-match-transition-gate-report.json",
    "status_projection",
    "LOCAL_GENERATED_REPORTS_ONLY",
    "schema_validation_only",
    "local_report_only",
    "live_system_queries_allowed",
    "runtime_buttons_enabled",
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
            read_text(root / "scripts" / "validate-host-app-status-schema.py"),
            read_text(root / "scripts" / "check-host-app-status-schema-validator.py"),
            read_text(root / "docs" / "metal" / "host-app-status-schema-validator.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add_check(checks, f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add_check(checks, f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_dir = out_dir / "fixture" / "host-app-status-schema-validator"
    fixture_dir.mkdir(parents=True, exist_ok=True)

    commands = [
        ["python3", str(root / "scripts" / "generate-host-app-status-schema.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-host-app-activation-ui-plan.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-activation-controller-design-stub.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "validate-activation-controller-static-contract.py"), "--root", str(root), "--input-dir", str(fixture_dir), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-provider-match-dry-run-spec.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-entitlement-evidence-checklist.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-no-hardware-activation-readiness-review.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-provider-match-evidence-ledger.py"), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "validate-provider-match-evidence-ledger.py"), "--input-dir", str(fixture_dir), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-provider-match-transition-gate-report.py"), "--input-dir", str(fixture_dir), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "generate-activation-controller-transition-gate-report.py"), "--input-dir", str(fixture_dir), "--out-dir", str(fixture_dir)],
        ["python3", str(root / "scripts" / "validate-host-app-status-schema.py"), "--input-dir", str(fixture_dir), "--out-dir", str(fixture_dir)],
    ]

    runs = []
    for index, cmd in enumerate(commands, start=1):
        run = run_command(cmd, root)
        runs.append(run)
        add_check(checks, f"command_{index}_returncode", run["returncode"] == 0, f"returncode={run['returncode']}")

    validator_path = fixture_dir / "host-app-status-schema-validator-report.json"
    validator = json.loads(validator_path.read_text()) if validator_path.exists() else {}

    add_check(checks, "validator_schema", validator.get("schema") == "h1mekartx.host_app_status_schema_validator.v1", f"schema={validator.get('schema')!r}")
    add_check(checks, "validator_decision", validator.get("decision") == "PASS_HOST_APP_STATUS_SCHEMA_VALIDATION", f"decision={validator.get('decision')!r}")
    add_check(checks, "validator_failed_count_zero", validator.get("failed_count") == 0, f"failed_count={validator.get('failed_count')!r}")
    add_check(checks, "validator_local_report_only", validator.get("local_report_only") is True, f"value={validator.get('local_report_only')!r}")

    projection = validator.get("status_projection", {})
    expected_projection = {
        "project_status": "RESEARCH_ONLY",
        "provider_match_status": "NO_GO",
        "activation_status": "NO_GO",
        "entitlement_evidence_status": "NEEDS_USER_EVIDENCE",
        "bundle_identity_status": "NEEDS_USER_EVIDENCE",
        "hardware_access_status": "BLOCKED",
        "status_source": "LOCAL_GENERATED_REPORTS_ONLY",
    }

    for key, expected in expected_projection.items():
        add_check(checks, f"projection:{key}", projection.get(key) == expected, f"value={projection.get(key)!r}")

    for key in [
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
    ]:
        add_check(checks, f"validator_blocks:{key}", validator.get(key) is False, f"value={validator.get(key)!r}")

    target = validator.get("target", {})
    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }

    for key, expected in expected_target.items():
        add_check(checks, f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    sb = validator.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add_check(checks, "safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add_check(checks, "safety_local_json_validation_only", sb.get("local_json_validation_only") is True, f"value={sb.get('local_json_validation_only')!r}")
    add_check(checks, "safety_schema_validation_only", sb.get("schema_validation_only") is True, f"value={sb.get('schema_validation_only')!r}")
    add_check(checks, "safety_local_report_only", sb.get("local_report_only") is True, f"value={sb.get('local_report_only')!r}")

    for key in [
        "live_system_queries",
        "runtime_buttons_enabled",
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
        "fixture_dir": str(fixture_dir),
        "decision": "PASS_HOST_APP_STATUS_SCHEMA_VALIDATOR_READY" if failed_count == 0 else "FAIL_HOST_APP_STATUS_SCHEMA_VALIDATOR",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "runs": runs,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "local_json_validation_only": True,
            "schema_validation_only": True,
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
            "# Host-app Status Schema Validator Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Fixture directory: `{report['fixture_dir']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates the host-app status schema validator using local fixture JSON only.",
            "",
            "It does not create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, request device ownership, attach to PCI providers, run live PCI tools, access PCI config space, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check host-app status schema validator.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=None, help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "host-app-status-schema-validator-check.json"
    md_path = out_dir / "host-app-status-schema-validator-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
