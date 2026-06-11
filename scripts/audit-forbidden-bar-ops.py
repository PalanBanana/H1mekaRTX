#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPORT_SCHEMA = "h1mekartx.forbidden_bar_operation_audit.v1"


DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".build",
    "build",
    "DerivedData",
    "__pycache__",
    ".swiftpm",
    "docs",
}


DEFAULT_INCLUDED_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cxx",
    ".h",
    ".hh",
    ".hpp",
    ".hxx",
    ".m",
    ".mm",
    ".swift",
    ".plist",
    ".entitlements",
    ".json",
    ".sh",
    ".py",
}


FORBIDDEN_PATTERNS: list[dict[str, str]] = [
    {
        "id": "pcidriverkit_configuration_write",
        "severity": "BLOCK",
        "pattern": r"\bConfigurationWrite(?:8|16|32)\b",
        "reason": "PCI config-space writes are forbidden in the current BAR/MMIO safety boundary.",
    },
    {
        "id": "pcidriverkit_memory_read",
        "severity": "BLOCK",
        "pattern": r"\bMemoryRead(?:8|16|32|64)\b",
        "reason": "PCI aperture/MMIO reads are forbidden until BAR identity and register semantics are reviewed.",
    },
    {
        "id": "pcidriverkit_memory_write",
        "severity": "BLOCK",
        "pattern": r"\bMemoryWrite(?:8|16|32|64)\b",
        "reason": "PCI aperture/MMIO writes are forbidden.",
    },
    {
        "id": "legacy_iokit_config_write",
        "severity": "BLOCK",
        "pattern": r"\bconfigWrite(?:8|16|32)\b",
        "reason": "Legacy IOKit PCI config-space writes are forbidden.",
    },
    {
        "id": "legacy_iokit_io_write",
        "severity": "BLOCK",
        "pattern": r"\bioWrite(?:8|16|32)\b",
        "reason": "Legacy IOKit I/O writes are forbidden.",
    },
    {
        "id": "legacy_iokit_io_read",
        "severity": "BLOCK",
        "pattern": r"\bioRead(?:8|16|32)\b",
        "reason": "Legacy IOKit I/O reads are forbidden until explicitly reviewed.",
    },
    {
        "id": "bar_memory_mapping",
        "severity": "BLOCK",
        "pattern": r"\b(?:CreateMemoryMap|MapDeviceMemoryWithIndex|getDeviceMemoryWithIndex|getDeviceMemoryWithRegister)\b",
        "reason": "BAR/device memory mapping is forbidden in the current stage.",
    },
    {
        "id": "bus_master_enable",
        "severity": "BLOCK",
        "pattern": r"\b(?:BusMaster|busMaster|kIOPCICommandBusMaster)\b",
        "reason": "Bus mastering enablement or related code is forbidden in this stage.",
    },
    {
        "id": "memory_space_enable",
        "severity": "BLOCK",
        "pattern": r"\b(?:MemorySpace|memorySpace|kIOPCICommandMemorySpace)\b",
        "reason": "PCI memory space enablement is forbidden in this stage.",
    },
    {
        "id": "driverkit_transport_pci_entitlement",
        "severity": "REVIEW",
        "pattern": r"com\.apple\.developer\.driverkit\.transport\.pci",
        "reason": "PCI DriverKit entitlement usage must be reviewed separately from BAR inventory work.",
    },
]


SELF_ALLOWLIST = {
    "scripts/audit-forbidden-bar-ops.py",
}


@dataclass
class Finding:
    file: str
    line: int
    column: int
    pattern_id: str
    severity: str
    reason: str
    snippet: str


def is_binary(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:4096]
    except OSError:
        return True

    return b"\0" in chunk


def should_scan_file(path: Path, root: Path, included_extensions: set[str]) -> bool:
    rel = path.relative_to(root).as_posix()

    if rel in SELF_ALLOWLIST:
        return False

    if path.suffix not in included_extensions:
        return False

    if is_binary(path):
        return False

    return True


def walk_files(root: Path, included_extensions: set[str], excluded_dirs: set[str]) -> list[Path]:
    files: list[Path] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        parts = set(path.relative_to(root).parts)
        if parts.intersection(excluded_dirs):
            continue

        if should_scan_file(path, root, included_extensions):
            files.append(path)

    return files


def scan_file(path: Path, root: Path) -> list[Finding]:
    text = path.read_text(errors="replace")
    rel = path.relative_to(root).as_posix()
    findings: list[Finding] = []

    compiled = [
        {
            **item,
            "compiled": re.compile(item["pattern"]),
        }
        for item in FORBIDDEN_PATTERNS
    ]

    for line_no, line in enumerate(text.splitlines(), start=1):
        for item in compiled:
            match = item["compiled"].search(line)
            if not match:
                continue

            findings.append(
                Finding(
                    file=rel,
                    line=line_no,
                    column=match.start() + 1,
                    pattern_id=item["id"],
                    severity=item["severity"],
                    reason=item["reason"],
                    snippet=line.strip()[:240],
                )
            )

    return findings


def build_report(root: Path, findings: list[Finding], scanned_files: list[Path]) -> dict[str, Any]:
    block_count = sum(1 for finding in findings if finding.severity == "BLOCK")
    review_count = sum(1 for finding in findings if finding.severity == "REVIEW")

    if block_count:
        decision = "FAIL_BLOCKED_OPERATION_FOUND"
    elif review_count:
        decision = "REVIEW_REQUIRED"
    else:
        decision = "PASS_NO_FORBIDDEN_BAR_OPS"

    return {
        "schema": REPORT_SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": decision,
        "scanned_file_count": len(scanned_files),
        "finding_count": len(findings),
        "block_count": block_count,
        "review_count": review_count,
        "findings": [
            {
                "file": finding.file,
                "line": finding.line,
                "column": finding.column,
                "pattern_id": finding.pattern_id,
                "severity": finding.severity,
                "reason": finding.reason,
                "snippet": finding.snippet,
            }
            for finding in findings
        ],
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
    findings = report["findings"]

    if findings:
        rows = [
            "| File | Line | Column | Severity | Pattern | Reason | Snippet |",
            "| --- | ---: | ---: | --- | --- | --- | --- |",
        ]

        for finding in findings:
            snippet = finding["snippet"].replace("|", "\\|")
            reason = finding["reason"].replace("|", "\\|")
            rows.append(
                f"| `{finding['file']}` | {finding['line']} | {finding['column']} | {finding['severity']} | `{finding['pattern_id']}` | {reason} | `{snippet}` |"
            )
    else:
        rows = ["No forbidden BAR operation patterns were found."]

    return "\n".join(
        [
            "# Forbidden BAR Operation Audit",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Repo root: `{report['repo_root']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Scanned files: `{report['scanned_file_count']}`",
            "",
            f"Findings: `{report['finding_count']}`",
            "",
            f"BLOCK findings: `{report['block_count']}`",
            "",
            f"REVIEW findings: `{report['review_count']}`",
            "",
            "## Findings",
            "",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This audit scans repository text files for forbidden operation symbols only.",
            "",
            "It does not run ioreg, system_profiler, PCI config-space reads, PCI config-space writes, MMIO reads, MMIO writes, BAR mapping, BAR poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, Metal acceleration attempts, or DriverKit activation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit the repository for forbidden BAR/MMIO/PCI operation symbols."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to scan. Defaults to current directory.",
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

    scanned_files = walk_files(root, DEFAULT_INCLUDED_EXTENSIONS, DEFAULT_EXCLUDED_DIRS)
    findings: list[Finding] = []

    for path in scanned_files:
        findings.extend(scan_file(path, root))

    report = build_report(root, findings, scanned_files)

    json_path = out_dir / "forbidden-bar-operation-audit.json"
    md_path = out_dir / "forbidden-bar-operation-audit.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    if report["block_count"] > 0:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
