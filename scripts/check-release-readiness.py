#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_SCHEMA = "h1mekartx.release_readiness_check.v1"

REQUIRED_PATHS = [
    "README.md",
    ".github/workflows/bar-safety-gates.yml",
    ".github/release.yml",
    "scripts/run-bar-safety-gates.sh",
    "scripts/audit-forbidden-bar-ops.py",
    "scripts/generate-bar-access-policy.py",
    "scripts/generate-bar-readiness-matrix.py",
    "scripts/check-bar-safety-boundary.py",
    "scripts/summarize-bar-inventory.py",
    "docs/metal/ci-bar-safety-gates.md",
    "docs/metal/forbidden-bar-operation-audit.md",
    "docs/metal/bar-access-policy-default-deny.md",
    "docs/metal/bar-access-readiness-matrix.md",
    "docs/metal/bar-mmio-risk-ledger.md",
    "docs/metal/bar-inventory-report-normalizer.md",
    "docs/metal/bar-inventory-diagnostics.md",
    "docs/metal/release-checklist.md",
]


README_BADGE = "actions/workflows/bar-safety-gates.yml/badge.svg?branch=main"

WORKFLOW_REQUIRED_SNIPPETS = [
    "name: BAR Safety Gates",
    "pull_request:",
    "push:",
    "branches:",
    "main",
    "uses: actions/checkout@v4",
    "uses: actions/setup-python@v5",
    "python-version: \"3.12\"",
    "run: ./scripts/run-bar-safety-gates.sh",
]


SAFETY_BOUNDARY_TERMS = [
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "GPU reset logic",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "Metal acceleration attempts",
    "DriverKit activation",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append(
        {
            "name": name,
            "passed": passed,
            "detail": detail,
        }
    )


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in REQUIRED_PATHS:
        path = root / rel
        add_check(
            checks,
            f"path_exists:{rel}",
            path.exists(),
            "present" if path.exists() else "missing",
        )

    readme = read_text(root / "README.md")
    add_check(
        checks,
        "readme_has_bar_safety_badge",
        README_BADGE in readme,
        "BAR Safety Gates badge found" if README_BADGE in readme else "BAR Safety Gates badge missing",
    )

    workflow = read_text(root / ".github/workflows/bar-safety-gates.yml")
    for snippet in WORKFLOW_REQUIRED_SNIPPETS:
        add_check(
            checks,
            f"workflow_contains:{snippet}",
            snippet in workflow,
            "found" if snippet in workflow else "missing",
        )

    release_yml = read_text(root / ".github/release.yml")
    add_check(
        checks,
        "release_yml_has_changelog",
        "changelog:" in release_yml and "categories:" in release_yml,
        "release note configuration found" if "changelog:" in release_yml and "categories:" in release_yml else "release note configuration missing",
    )

    checklist = read_text(root / "docs/metal/release-checklist.md")
    for term in SAFETY_BOUNDARY_TERMS:
        add_check(
            checks,
            f"release_checklist_mentions:{term}",
            term in checklist,
            "found" if term in checklist else "missing",
        )

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": REPORT_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_RELEASE_READY" if failed_count == 0 else "FAIL_RELEASE_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "safety_boundary": {
            "read_only": True,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "metal_acceleration_attempt": False,
            "driverkit_activation": False,
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
            "# Release Readiness Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Repo root: `{report['repo_root']}`",
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
            "This release readiness check validates repository text files only.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR memory mapping, BAR memory poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check H1mekaRTX release readiness metadata, badge, workflow, and checklist files."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root. Defaults to current directory.",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to repo root.",
    )

    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "release-readiness-check.json"
    md_path = out_dir / "release-readiness-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    if report["failed_count"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
