#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.provider_match_evidence_ledger_check.v1"

REQUIRED_FILES = [
    "scripts/generate-provider-match-evidence-ledger.py",
    "docs/metal/provider-match-evidence-ledger.md",
]

REQUIRED_TERMS = [
    "PROVIDER_MATCH_EVIDENCE_LEDGER_READY_BLOCKED_ON_USER_EVIDENCE",
    "provider_match_transition_allowed",
    "driverkit_target_creation_allowed",
    "activation_request_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "provider-match-dry-run-spec",
    "entitlement-evidence-checklist",
    "no-hardware-activation-readiness-review",
    "vendor ID exact match",
    "device ID exact match",
    "IOPCIMatch exact match",
    "subsystem vendor ID exact match",
    "subsystem ID exact match",
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
            str(root / "scripts" / "generate-provider-match-evidence-ledger.py"),
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
            read_text(root / "scripts" / "generate-provider-match-evidence-ledger.py"),
            read_text(root / "docs" / "metal" / "provider-match-evidence-ledger.md"),
        ]
    )

    for term in REQUIRED_TERMS:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add(f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    ledger_path = out_dir / "provider-match-evidence-ledger.json"
    data = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}

    add("ledger_schema", data.get("schema") == "h1mekartx.provider_match_evidence_ledger.v1", f"schema={data.get('schema')!r}")
    add("ledger_decision", data.get("decision") == "PROVIDER_MATCH_EVIDENCE_LEDGER_READY_BLOCKED_ON_USER_EVIDENCE", f"decision={data.get('decision')!r}")
    add("ledger_ready", data.get("provider_match_evidence_ledger_ready") is True, f"value={data.get('provider_match_evidence_ledger_ready')!r}")
    add("provider_transition_blocked", data.get("provider_match_transition_allowed") is False, f"value={data.get('provider_match_transition_allowed')!r}")

    for key in [
        "driverkit_target_creation_allowed",
        "activation_request_allowed",
        "provider_attach_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add(f"blocked:{key}", data.get(key) is False, f"value={data.get(key)!r}")

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

    source_artifacts = data.get("source_artifacts", [])
    source_names = {item.get("artifact") for item in source_artifacts if isinstance(item, dict)}
    for required_source in [
        "provider-match-dry-run-spec",
        "entitlement-evidence-checklist",
        "no-hardware-activation-readiness-review",
    ]:
        add(
            f"source_artifact:{required_source}",
            required_source in source_names,
            "present" if required_source in source_names else "missing",
        )

    ledger_items = data.get("evidence_ledger", [])
    add("ledger_item_count_minimum", isinstance(ledger_items, list) and len(ledger_items) >= 12, f"count={len(ledger_items) if isinstance(ledger_items, list) else 'not-list'}")
    add("blocking_ledger_items_present", data.get("blocking_ledger_item_count", 0) > 0, f"value={data.get('blocking_ledger_item_count')!r}")

    categories = {item.get("category") for item in ledger_items if isinstance(item, dict)}
    for category in [
        "target_identity",
        "entitlement",
        "bundle_identity",
        "wrong_device_prevention",
        "activation_boundary",
        "device_ownership_boundary",
        "hardware_access_boundary",
    ]:
        add(f"ledger_category:{category}", category in categories, "present" if category in categories else "missing")

    gates = data.get("transition_gates", [])
    add("transition_gates_present", isinstance(gates, list) and len(gates) >= 8, f"count={len(gates) if isinstance(gates, list) else 'not-list'}")
    add("blocking_transition_gates_present", data.get("blocking_transition_gate_count", 0) > 0, f"value={data.get('blocking_transition_gate_count')!r}")
    add("pass_transition_gates_present", data.get("pass_transition_gate_count", 0) > 0, f"value={data.get('pass_transition_gate_count')!r}")
    add("has_no_go_gate", any(isinstance(item, dict) and item.get("status") == "NO_GO" for item in gates), "NO_GO found")
    add("has_pass_gate", any(isinstance(item, dict) and item.get("status") == "PASS" for item in gates), "PASS found")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add("safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add("safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add("safety_ledger_only", sb.get("ledger_only") is True, f"value={sb.get('ledger_only')!r}")
    add("safety_local_report_reference_only", sb.get("local_report_reference_only") is True, f"value={sb.get('local_report_reference_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_PROVIDER_MATCH_EVIDENCE_LEDGER_READY" if failed_count == 0 else "FAIL_PROVIDER_MATCH_EVIDENCE_LEDGER",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "ledger_only": True,
            "local_report_reference_only": True,
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
            "# Provider-match Evidence Ledger Check",
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
            "This check validates the provider-match evidence ledger using local generator output only.",
            "",
            "It does not create DriverKit targets, add dext provider classes, add Info.plist provider-match dictionaries, create activation requests, create deactivation requests, call extension manager submit, activate DriverKit, request device ownership, attach to PCI providers, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX provider-match evidence ledger.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "provider-match-evidence-ledger-check.json"
    md_path = out_dir / "provider-match-evidence-ledger-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
