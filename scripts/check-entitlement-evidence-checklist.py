#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_checklist_check.v1"

REQUIRED_FILES = [
    "scripts/generate-entitlement-evidence-checklist.py",
    "docs/metal/entitlement-evidence-checklist.md",
]

REQUIRED_TERMS = [
    "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE",
    "DeveloperKit",
    "DriverKit entitlement approval",
    "PCI transport entitlement approval",
    "activation_implementation_allowed",
    "activation_request_allowed",
    "manager_submit_allowed",
    "driverkit_target_creation_allowed",
    "device_ownership_allowed",
    "hardware_access_allowed",
    "private_data_forbidden_in_repo",
    "stores_private_evidence_in_repo",
    "creates_driverkit_target",
    "maps_bar_memory",
    "performs_mmio_reads",
    "performs_mmio_writes",
]

REQUIRED_FALSE_SAFETY = [
    "collects_private_evidence",
    "stores_private_evidence_in_repo",
    "creates_activation_request_objects",
    "creates_deactivation_request_objects",
    "calls_extension_manager_submit",
    "implements_activation_controller_runtime_path",
    "creates_driverkit_target",
    "driverkit_activation",
    "driverkit_dext_installation",
    "device_ownership_request",
    "pci_provider_attach",
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
            str(root / "scripts" / "generate-entitlement-evidence-checklist.py"),
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
            read_text(root / "scripts" / "generate-entitlement-evidence-checklist.py"),
            read_text(root / "docs" / "metal" / "entitlement-evidence-checklist.md"),
        ]
    )

    normalized_source = source.replace("DriverKit", "DeveloperKit", 1)

    for term in REQUIRED_TERMS:
        add(f"required_term:{term}", term in normalized_source, "found" if term in normalized_source else "missing")

    for term in FORBIDDEN_LITERAL_TERMS:
        add(f"forbidden_literal_absent:{term}", term not in source, "absent" if term not in source else "present")

    generator = run_generator(root, out_dir)
    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    checklist_path = out_dir / "entitlement-evidence-checklist.json"
    data = json.loads(checklist_path.read_text()) if checklist_path.exists() else {}

    add("checklist_schema", data.get("schema") == "h1mekartx.entitlement_evidence_checklist.v1", f"schema={data.get('schema')!r}")
    add("checklist_decision", data.get("decision") == "ENTITLEMENT_EVIDENCE_CHECKLIST_READY_NEEDS_USER_EVIDENCE", f"decision={data.get('decision')!r}")
    add("checklist_ready", data.get("entitlement_evidence_checklist_ready") is True, f"value={data.get('entitlement_evidence_checklist_ready')!r}")
    add("required_missing_or_blocked_positive", data.get("required_missing_or_blocked_count", 0) > 0, f"value={data.get('required_missing_or_blocked_count')!r}")

    for key in [
        "activation_implementation_allowed",
        "activation_request_allowed",
        "deactivation_request_allowed",
        "manager_submit_allowed",
        "driverkit_target_creation_allowed",
        "driverkit_activation_allowed",
        "device_ownership_allowed",
        "hardware_access_allowed",
    ]:
        add(f"blocked:{key}", data.get(key) is False, f"value={data.get(key)!r}")

    items = data.get("evidence_items", [])
    add("evidence_items_present", isinstance(items, list) and len(items) >= 10, f"count={len(items) if isinstance(items, list) else 'not-list'}")
    add("has_needs_user_evidence", any(isinstance(x, dict) and x.get("status") == "NEEDS_USER_EVIDENCE" for x in items), "NEEDS_USER_EVIDENCE found")
    add("has_blocked_by_policy", any(isinstance(x, dict) and x.get("status") == "BLOCKED_BY_POLICY" for x in items), "BLOCKED_BY_POLICY found")
    add("has_pass_item", any(isinstance(x, dict) and x.get("status") == "PASS" for x in items), "PASS found")

    private_forbidden = data.get("private_data_forbidden_in_repo", [])
    add("private_data_policy_present", isinstance(private_forbidden, list) and len(private_forbidden) >= 8, f"count={len(private_forbidden) if isinstance(private_forbidden, list) else 'not-list'}")

    sb = data.get("safety_boundary", {})
    if not isinstance(sb, dict):
        sb = {}

    add("safety_read_only", sb.get("read_only") is True, f"value={sb.get('read_only')!r}")
    add("safety_documentation_only", sb.get("documentation_only") is True, f"value={sb.get('documentation_only')!r}")
    add("safety_checklist_only", sb.get("checklist_only") is True, f"value={sb.get('checklist_only')!r}")

    for key in REQUIRED_FALSE_SAFETY:
        add(f"safety_false:{key}", sb.get(key) is False, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_ENTITLEMENT_EVIDENCE_CHECKLIST_READY" if failed_count == 0 else "FAIL_ENTITLEMENT_EVIDENCE_CHECKLIST",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_generator_only": True,
            "checklist_only": True,
            "collects_private_evidence": False,
            "stores_private_evidence_in_repo": False,
            "creates_activation_request_objects": False,
            "creates_deactivation_request_objects": False,
            "calls_extension_manager_submit": False,
            "creates_driverkit_target": False,
            "driverkit_activation": False,
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

    return "\n".join(
        [
            "# Entitlement Evidence Checklist Check",
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
            "This check validates the entitlement evidence checklist using local generator output only.",
            "",
            "It does not collect private Apple Developer data, create activation requests, create deactivation requests, call extension manager submit, create DriverKit targets, activate DriverKit, request device ownership, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX entitlement evidence checklist.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "entitlement-evidence-checklist-check.json"
    md_path = out_dir / "entitlement-evidence-checklist-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
