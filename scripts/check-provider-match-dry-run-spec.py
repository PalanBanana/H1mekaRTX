#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_dry_run_spec_check.v1"

REQUIRED_FILES = [
    "scripts/generate-provider-match-dry-run-spec.py",
    "docs/metal/provider-match-dry-run-spec.md",
]

REQUIRED_TERMS = [
    "PROVIDER_MATCH_DRY_RUN_SPEC_READY",
    "MATCH_TARGET_SPEC_ONLY",
    "REJECT_WRONG_VENDOR",
    "REJECT_WRONG_DEVICE",
    "REJECT_WRONG_SUBSYSTEM",
    "REJECT_INCOMPLETE_IDENTITY",
    "vendor_id",
    "device_id",
    "iopcimatch",
    "subsystem_vendor_id",
    "subsystem_id",
    "creates_driverkit_target",
    "adds_info_plist_provider_match",
    "device_ownership_request",
    "pci_provider_attach",
    "maps_bar_memory",
    "performs_mmio_reads",
    "performs_mmio_writes",
]

REQUIRED_FALSE_SAFETY = [
    "creates_driverkit_target",
    "adds_dext_provider_class",
    "adds_info_plist_provider_match",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "implements_activation_controller_runtime_path",
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

FORBIDDEN_LITERAL_TERMS = [
    "activationRequest(forExtensionWithIdentifier",
    "deactivationRequest(forExtensionWithIdentifier",
    ".submitRequest",
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


def run_generator(root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-provider-match-dry-run-spec.py"),
            "--out-dir",
            str(out_dir),
        ],
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
            read_text(root / "scripts" / "generate-provider-match-dry-run-spec.py"),
            read_text(root / "docs" / "metal" / "provider-match-dry-run-spec.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add(f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    spec_path = out_dir / "provider-match-dry-run-spec.json"
    data = json.loads(spec_path.read_text()) if spec_path.exists() else {}

    add("spec_schema", data.get("schema") == "h1mekartx.provider_match_dry_run_spec.v1", f"schema={data.get('schema')!r}")
    add("spec_decision", data.get("decision") == "PROVIDER_MATCH_DRY_RUN_SPEC_READY", f"decision={data.get('decision')!r}")
    add("provider_match_spec_ready", data.get("provider_match_spec_ready") is True, f"value={data.get('provider_match_spec_ready')!r}")
    add("dry_run_only", data.get("dry_run_only") is True, f"value={data.get('dry_run_only')!r}")
    add("failed_case_count_zero", data.get("failed_case_count") == 0, f"failed_case_count={data.get('failed_case_count')!r}")
    add("case_count_minimum", data.get("case_count", 0) >= 5, f"case_count={data.get('case_count')!r}")

    target = data.get("target", {})
    if not isinstance(target, dict):
        target = {}

    expected_target = {
        "vendor_id": "0x10de",
        "device_id": "0x2f04",
        "iopcimatch": "0x2f0410de",
        "subsystem_vendor_id": "0x1458",
        "subsystem_id": "0x417e",
    }

    for key, expected in expected_target.items():
        add(f"target:{key}", target.get(key) == expected, f"value={target.get(key)!r}")

    match_fields = data.get("match_fields", [])
    field_names = {item.get("field") for item in match_fields if isinstance(item, dict)}
    for key in expected_target:
        add(f"match_field:{key}", key in field_names, "present" if key in field_names else "missing")

    cases = data.get("dry_run_cases", [])
    actual_decisions = {item.get("actual_decision") for item in cases if isinstance(item, dict)}
    for decision in [
        "MATCH_TARGET_SPEC_ONLY",
        "REJECT_WRONG_VENDOR",
        "REJECT_WRONG_DEVICE",
        "REJECT_WRONG_SUBSYSTEM",
        "REJECT_INCOMPLETE_IDENTITY",
    ]:
        add(f"dry_run_decision:{decision}", decision in actual_decisions, "present" if decision in actual_decisions else "missing")

    add("all_cases_passed", all(isinstance(item, dict) and item.get("passed") is True for item in cases), "all passed")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add("safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add("safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add("safety_spec_only", sb.get("spec_only") is True, f"value={sb.get('spec_only')!r}")
    add("safety_local_dry_run_only", sb.get("local_dry_run_only") is True, f"value={sb.get('local_dry_run_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_PROVIDER_MATCH_DRY_RUN_SPEC_READY" if failed_count == 0 else "FAIL_PROVIDER_MATCH_DRY_RUN_SPEC",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "spec_only": True,
            "local_dry_run_only": True,
            "creates_driverkit_target": False,
            "adds_dext_provider_class": False,
            "adds_info_plist_provider_match": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "driverkit_activation": False,
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
            "# Provider-match Dry-run Spec Check",
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
            "This check validates the provider-match dry-run spec using local generator output only.",
            "",
            "It does not create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, create activation requests, create deactivation requests, call extension manager submit, activate DriverKit, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX provider-match dry-run spec.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "provider-match-dry-run-spec-check.json"
    md_path = out_dir / "provider-match-dry-run-spec-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
