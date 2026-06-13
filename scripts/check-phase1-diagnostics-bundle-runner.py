#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.phase1_diagnostics_bundle_runner_check.v1"

REQUIRED_FILES = [
    "scripts/create-phase1-diagnostics-bundle.sh",
    "docs/metal/phase1-diagnostics-bundle-runner.md",
]

REQUIRED_TERMS = [
    "collect-host-diagnostics.sh",
    "summarize-host-diagnostics.py",
    "collect-bar-inventory.sh",
    "summarize-bar-inventory.py",
    "create-local-host-report-bundle.py",
    "generate-local-diagnostics-index.py",
    "host-diagnostics-summary.json",
    "host-diagnostics-summary.md",
    "bar-inventory-summary.json",
    "bar-inventory-summary.md",
    "local-diagnostics-index.json",
    "host-report-bundle/bundle.json",
    "Host diagnostics",
    "Graphics stack diagnostics",
    "Runtime probe: not attempted",
    "UI compositor proof: unproven",
    "Metal proof: unproven",
    "No DriverKit activation",
    "No System Extension activation",
    "No PCI config-space writes",
    "No MMIO reads",
    "No MMIO writes",
    "No BAR mapping",
    "No GPU command submission",
    "No RTX 5070 Metal acceleration claim",
]

FORBIDDEN_TERMS = [
    "OSSystem" + "ExtensionRequest",
    "OSSystem" + "ExtensionManager",
    "Configuration" + "Write",
    "Memory" + "Write",
    "Create" + "Memory" + "Map",
    "systemextensionsctl developer on",
    "csrutil disable",
    "spctl --master-disable",
    "nvram boot-args",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    for rel in REQUIRED_FILES:
        path = root / rel
        add(f"path_exists:{rel}", path.exists(), "present" if path.exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in REQUIRED_FILES)

    for term in REQUIRED_TERMS:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    for term in FORBIDDEN_TERMS:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_PHASE1_DIAGNOSTICS_BUNDLE_RUNNER_READY" if failed_count == 0 else "FAIL_PHASE1_DIAGNOSTICS_BUNDLE_RUNNER_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_report_generation": True,
            "runs_host_diagnostics_collector_when_user_invoked": True,
            "runs_bar_inventory_collector_when_user_invoked": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "bar_poking": False,
            "gpu_command_submission": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
    }


def markdown_report(report: dict[str, Any]) -> str:
    rows = [
        f"| `{item['name']}` | {'PASS' if item['passed'] else 'FAIL'} | {str(item['detail']).replace('|', '\\|')} |"
        for item in report["checks"]
    ]

    return "\n".join(
        [
            "# Phase 1 Diagnostics Bundle Runner Check",
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
            "This check validates the Phase 1 diagnostics bundle runner as a static contract. It does not run live diagnostics, activate DriverKit, activate System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, submit GPU commands, prove UI compositor acceleration, or prove Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX Phase 1 diagnostics bundle runner.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)
    json_path = out_dir / "phase1-diagnostics-bundle-runner-check.json"
    md_path = out_dir / "phase1-diagnostics-bundle-runner-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
