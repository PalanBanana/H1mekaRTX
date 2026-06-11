#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.local_diagnostics_index_check.v1"

REQUIRED_FILES = [
    "scripts/generate-local-diagnostics-index.py",
    "docs/metal/local-diagnostics-index.md",
]

EXPECTED_ITEMS = [
    "metal-workload-result-schema.json",
    "metal-workload-regression-manifest.json",
    "workload-schema-regression-sync-report.json",
    "p1-arithmetic-workload-implementation-report.json",
    "local-host-report-renderer-report.json",
    "rendered-host-status-report.md",
    "host-report-bundle-format.json",
    "host-report-bundle-format-check.json",
    "local-host-report-bundle-generator-check.json",
    "host-report-bundle/bundle.json",
    "host-report-bundle/README.md",
    "forbidden-bar-operation-audit.md",
    "release-readiness-check.md",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def write_fixture_reports(fixture_root: Path) -> None:
    fixture_root.mkdir(parents=True, exist_ok=True)
    (fixture_root / "host-report-bundle").mkdir(parents=True, exist_ok=True)

    json_files = [
        "metal-workload-result-schema.json",
        "metal-workload-regression-manifest.json",
        "workload-schema-regression-sync-report.json",
        "p1-arithmetic-workload-implementation-report.json",
        "local-host-report-renderer-report.json",
        "host-report-bundle-format.json",
        "host-report-bundle-format-check.json",
        "local-host-report-bundle-generator-check.json",
        "host-report-bundle/bundle.json",
    ]

    for rel in json_files:
        path = fixture_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema": "fixture",
                    "decision": "FIXTURE_PRESENT",
                    "path": rel,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n"
        )

    md_files = [
        "rendered-host-status-report.md",
        "host-report-bundle/README.md",
        "forbidden-bar-operation-audit.md",
        "release-readiness-check.md",
    ]

    for rel in md_files:
        path = fixture_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# Fixture\n\nPath: `{rel}`\n")


def run_generator(root: Path, fixture_root: Path, out_dir: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "python3",
            str(root / "scripts" / "generate-local-diagnostics-index.py"),
            "--root",
            str(fixture_root),
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
            read_text(root / "scripts" / "generate-local-diagnostics-index.py"),
            read_text(root / "docs" / "metal" / "local-diagnostics-index.md"),
        ]
    )

    required_terms = [
        "LOCAL_DIAGNOSTICS_INDEX_CREATED",
        "LOCAL_ONLY_DIAGNOSTICS_INDEX",
        "localFilesOnly",
        "indexesExistingLocalFilesOnly",
        "noLiveExtensionQuery",
        "noSystemExtensionRequests",
        "noDriverKitActivation",
        "noDeviceOwnershipRequest",
        "noPCIConfigAccess",
        "noMMIOAccess",
        "noBARMapping",
        "noRTX5070Acceleration",
        "noHardwareCommandSubmission",
    ]

    for term in required_terms:
        add(f"required_term:{term}", term in source, "found" if term in source else "missing")

    forbidden_terms = [
        "OSSystem" + "ExtensionRequest",
        "OSSystem" + "ExtensionManager",
        "IOPCI" + "Device",
        "Configuration" + "Write",
        "Memory" + "Read",
        "Memory" + "Write",
        "sub" + "process.run([\"ioreg\"",
        "sub" + "process.run([\"system_profiler\"",
    ]

    for term in forbidden_terms:
        add(f"forbidden_term_absent:{term}", term not in source, "absent" if term not in source else "present")

    fixture_root = out_dir / "fixture" / "diagnostics-root"
    index_out = out_dir / "fixture" / "index-out"

    write_fixture_reports(fixture_root)
    generator = run_generator(root, fixture_root, index_out)

    add("generator_returncode", generator["returncode"] == 0, f"returncode={generator['returncode']}")

    index_path = index_out / "local-diagnostics-index.json"
    index_md = index_out / "local-diagnostics-index.md"

    add("index_json_exists", index_path.exists(), "present" if index_path.exists() else "missing")
    add("index_md_exists", index_md.exists(), "present" if index_md.exists() else "missing")

    index = json.loads(index_path.read_text()) if index_path.exists() else {}

    add("index_schema", index.get("schema") == "h1mekartx.local_diagnostics_index.v1", f"schema={index.get('schema')!r}")
    add("index_decision", index.get("decision") == "LOCAL_DIAGNOSTICS_INDEX_CREATED", f"decision={index.get('decision')!r}")
    add("index_type", index.get("indexType") == "LOCAL_ONLY_DIAGNOSTICS_INDEX", f"indexType={index.get('indexType')!r}")
    add("present_item_count", index.get("presentItemCount") == len(EXPECTED_ITEMS), f"presentItemCount={index.get('presentItemCount')!r}")
    add("missing_item_count", index.get("missingItemCount") == 0, f"missingItemCount={index.get('missingItemCount')!r}")

    item_paths = {item.get("path") for item in index.get("items", []) if isinstance(item, dict)}

    for rel in EXPECTED_ITEMS:
        add(f"indexed_item:{rel}", rel in item_paths, "present" if rel in item_paths else "missing")

    for item in index.get("items", []):
        if not isinstance(item, dict):
            continue
        add(
            f"item_present:{item.get('path')}",
            item.get("present") is True,
            f"present={item.get('present')!r}",
        )
        add(
            f"item_has_sha256:{item.get('path')}",
            isinstance(item.get("sha256"), str) and len(item.get("sha256", "")) == 64,
            f"sha256={item.get('sha256')!r}",
        )
        add(
            f"item_has_bytes:{item.get('path')}",
            isinstance(item.get("bytes"), int) and item.get("bytes", 0) > 0,
            f"bytes={item.get('bytes')!r}",
        )

    sb = index.get("safetyBoundary", {})
    if not isinstance(sb, dict):
        sb = {}

    for key in [
        "localFilesOnly",
        "indexesExistingLocalFilesOnly",
        "noLiveExtensionQuery",
        "noSystemExtensionRequests",
        "noDriverKitActivation",
        "noDeviceOwnershipRequest",
        "noPCIConfigAccess",
        "noMMIOAccess",
        "noBARMapping",
        "noRTX5070Acceleration",
        "noRTX5070ShaderExecution",
        "noHardwareCommandSubmission",
        "noRTX5070ResourceAllocation",
        "noFirmwareLoading",
        "noDisplayInitialization",
        "noFramebufferInitialization",
        "noGPUReset",
    ]:
        add(f"index_safety_true:{key}", sb.get(key) is True, f"value={sb.get(key)!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_LOCAL_DIAGNOSTICS_INDEX_READY" if failed_count == 0 else "FAIL_LOCAL_DIAGNOSTICS_INDEX_NOT_READY",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "generator": generator,
        "fixture_root": str(fixture_root),
        "fixture_index_out": str(index_out),
        "expected_items": EXPECTED_ITEMS,
        "safety_boundary": {
            "read_only_static_check": True,
            "local_fixture_only": True,
            "indexes_existing_local_files_only": True,
            "local_files_only": True,
            "queries_live_extension_state": False,
            "adds_system_extension_request_code": False,
            "driverkit_activation": False,
            "system_extension_activation_request": False,
            "system_extension_deactivation_request": False,
            "extension_manager_submit_request": False,
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

    items = [f"- `{item}`" for item in report["expected_items"]]

    return "\n".join(
        [
            "# Local Diagnostics Index Check",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            "## Expected Indexed Items",
            "",
            *items,
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This check validates a local-only diagnostics index using local fixture files.",
            "",
            "It does not query live extension state, add System Extension request code, activate DriverKit, submit activation or deactivation requests, submit extension manager requests, request device ownership, run live PCI tools, perform PCI config-space access, perform MMIO access, map BAR memory, poke BAR memory, execute RTX 5070 shaders, submit hardware commands to RTX 5070, allocate RTX 5070 resources, or start RTX 5070 Metal acceleration implementation.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Check H1mekaRTX local diagnostics index.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to repo root.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else root

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root, out_dir)

    json_path = out_dir / "local-diagnostics-index-check.json"
    md_path = out_dir / "local-diagnostics-index-check.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
