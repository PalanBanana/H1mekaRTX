#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.local_diagnostics_index.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendorID": "0x10de",
    "deviceID": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystemVendorID": "0x1458",
    "subsystemID": "0x417e",
}

INDEX_ITEMS = [
    {
        "path": "metal-workload-result-schema.json",
        "category": "metal_schema",
        "kind": "json_report",
        "required": False,
        "description": "Generated public Metal workload result schema.",
    },
    {
        "path": "metal-workload-regression-manifest.json",
        "category": "metal_regression",
        "kind": "json_report",
        "required": False,
        "description": "Generated public Metal workload regression manifest.",
    },
    {
        "path": "workload-schema-regression-sync-report.json",
        "category": "metal_regression",
        "kind": "json_report",
        "required": False,
        "description": "Generated schema/regression sync check report.",
    },
    {
        "path": "p1-arithmetic-workload-implementation-report.json",
        "category": "metal_runtime_check",
        "kind": "json_report",
        "required": False,
        "description": "Generated P1 arithmetic workload implementation check report.",
    },
    {
        "path": "local-host-report-renderer-report.json",
        "category": "host_tooling",
        "kind": "json_report",
        "required": False,
        "description": "Generated local host report renderer check report.",
    },
    {
        "path": "host-diagnostics-summary.json",
        "category": "host_diagnostics",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 1 host and graphics stack diagnostics JSON summary.",
    },
    {
        "path": "host-diagnostics-summary.md",
        "category": "host_diagnostics",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 1 host and graphics stack diagnostics Markdown summary.",
    },
    {
        "path": "host-ui-diagnostics-check.json",
        "category": "host_diagnostics",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 1 host and graphics stack diagnostics fixture check.",
    },
    {
        "path": "bar-inventory-summary.json",
        "category": "host_diagnostics",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 1 BAR inventory diagnostics JSON summary.",
    },
    {
        "path": "bar-inventory-summary.md",
        "category": "host_diagnostics",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 1 BAR inventory diagnostics Markdown summary.",
    },
    {
        "path": "phase1-diagnostics-bundle-runner-check.json",
        "category": "host_diagnostics",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 1 diagnostics bundle runner static check.",
    },
    {
        "path": "ui-compositor-proof-schema.json",
        "category": "ui_compositor_proof",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor proof schema.",
    },
    {
        "path": "ui-compositor-proof-schema.md",
        "category": "ui_compositor_proof",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor proof schema Markdown.",
    },
    {
        "path": "ui-compositor-proof-schema-check.json",
        "category": "ui_compositor_proof",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor proof schema check.",
    },
    {
        "path": "ui-compositor-sample-summary.json",
        "category": "ui_compositor_sample",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor sample diagnostics JSON summary.",
    },
    {
        "path": "ui-compositor-sample-summary.md",
        "category": "ui_compositor_sample",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor sample diagnostics Markdown summary.",
    },
    {
        "path": "ui-compositor-sample-diagnostics-check.json",
        "category": "ui_compositor_sample",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor sample diagnostics check.",
    },
    {
        "path": "ui-compositor-readiness-matrix.json",
        "category": "ui_compositor_readiness",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor readiness matrix JSON.",
    },
    {
        "path": "ui-compositor-readiness-matrix.md",
        "category": "ui_compositor_readiness",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor readiness matrix Markdown.",
    },
    {
        "path": "ui-compositor-readiness-matrix-check.json",
        "category": "ui_compositor_readiness",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI compositor readiness matrix check.",
    },
    {
        "path": "ui-gpu-attribution-summary.json",
        "category": "ui_gpu_attribution",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI GPU attribution candidate diagnostics JSON summary.",
    },
    {
        "path": "ui-gpu-attribution-summary.md",
        "category": "ui_gpu_attribution",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 2 UI GPU attribution candidate diagnostics Markdown summary.",
    },
    {
        "path": "ui-gpu-attribution-diagnostics-check.json",
        "category": "ui_gpu_attribution",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI GPU attribution diagnostics check.",
    },
    {
        "path": "ui-workload-correlation-report.json",
        "category": "ui_workload_correlation",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI workload correlation candidate JSON report.",
    },
    {
        "path": "ui-workload-correlation-report.md",
        "category": "ui_workload_correlation",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated Phase 2 UI workload correlation candidate Markdown report.",
    },
    {
        "path": "ui-workload-correlation-report-check.json",
        "category": "ui_workload_correlation",
        "kind": "json_report",
        "required": False,
        "description": "Generated Phase 2 UI workload correlation report check.",
    },
    {
        "path": "rendered-host-status-report.md",
        "category": "host_tooling",
        "kind": "markdown_report",
        "required": False,
        "description": "Rendered local host status report.",
    },
    {
        "path": "host-report-bundle-format.json",
        "category": "host_bundle",
        "kind": "json_report",
        "required": False,
        "description": "Generated local host report bundle format.",
    },
    {
        "path": "host-report-bundle-format-check.json",
        "category": "host_bundle",
        "kind": "json_report",
        "required": False,
        "description": "Generated local host report bundle format check.",
    },
    {
        "path": "local-host-report-bundle-generator-check.json",
        "category": "host_bundle",
        "kind": "json_report",
        "required": False,
        "description": "Generated local host report bundle generator check.",
    },
    {
        "path": "host-report-bundle/bundle.json",
        "category": "host_bundle",
        "kind": "bundle_manifest",
        "required": False,
        "description": "Generated local-only host report bundle manifest.",
    },
    {
        "path": "host-report-bundle/README.md",
        "category": "host_bundle",
        "kind": "bundle_summary",
        "required": False,
        "description": "Generated local-only host report bundle README.",
    },
    {
        "path": "forbidden-bar-operation-audit.md",
        "category": "safety",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated forbidden BAR operation audit report, if present.",
    },
    {
        "path": "release-readiness-check.md",
        "category": "release",
        "kind": "markdown_report",
        "required": False,
        "description": "Generated release readiness report, if present.",
    },
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_item(root: Path, item: dict[str, Any]) -> dict[str, Any]:
    path = root / item["path"]
    present = path.exists() and path.is_file()

    return {
        "path": item["path"],
        "absolutePath": str(path),
        "category": item["category"],
        "kind": item["kind"],
        "required": item["required"],
        "present": present,
        "sha256": sha256_file(path) if present else None,
        "bytes": path.stat().st_size if present else 0,
        "description": item["description"],
    }


def build_index(root: Path) -> dict[str, Any]:
    items = [inspect_item(root, item) for item in INDEX_ITEMS]
    present_count = sum(1 for item in items if item["present"])
    missing_count = len(items) - present_count

    categories: dict[str, dict[str, Any]] = {}
    for item in items:
        category = item["category"]
        categories.setdefault(
            category,
            {
                "category": category,
                "total": 0,
                "present": 0,
                "missing": 0,
            },
        )
        categories[category]["total"] += 1
        if item["present"]:
            categories[category]["present"] += 1
        else:
            categories[category]["missing"] += 1

    return {
        "schema": SCHEMA,
        "generatedAtUTC": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "LOCAL_DIAGNOSTICS_INDEX_CREATED",
        "indexType": "LOCAL_ONLY_DIAGNOSTICS_INDEX",
        "rootDirectory": str(root),
        "itemCount": len(items),
        "presentItemCount": present_count,
        "missingItemCount": missing_count,
        "categories": sorted(categories.values(), key=lambda x: x["category"]),
        "items": items,
        "safetyBoundary": {
            "localFilesOnly": True,
            "indexesExistingLocalFilesOnly": True,
            "noLiveExtensionQuery": True,
            "noSystemExtensionRequests": True,
            "noDriverKitActivation": True,
            "noDeviceOwnershipRequest": True,
            "noPCIConfigAccess": True,
            "noMMIOAccess": True,
            "noBARMapping": True,
            "noRTX5070Acceleration": True,
            "noRTX5070ShaderExecution": True,
            "noHardwareCommandSubmission": True,
            "noRTX5070ResourceAllocation": True,
            "noFirmwareLoading": True,
            "noDisplayInitialization": True,
            "noFramebufferInitialization": True,
            "noGPUReset": True,
        },
    }


def markdown_report(index: dict[str, Any]) -> str:
    category_rows = [
        f"| `{item['category']}` | `{item['total']}` | `{item['present']}` | `{item['missing']}` |"
        for item in index["categories"]
    ]

    item_rows = []
    for item in index["items"]:
        status = "present" if item["present"] else "missing"
        item_rows.append(
            f"| `{item['path']}` | `{item['category']}` | `{item['kind']}` | `{status}` | `{item['bytes']}` |"
        )

    return "\n".join(
        [
            "# Local Diagnostics Index",
            "",
            f"Generated UTC: `{index['generatedAtUTC']}`",
            "",
            f"Decision: `{index['decision']}`",
            "",
            f"Index type: `{index['indexType']}`",
            "",
            f"Root directory: `{index['rootDirectory']}`",
            "",
            f"Item count: `{index['itemCount']}`",
            "",
            f"Present item count: `{index['presentItemCount']}`",
            "",
            f"Missing item count: `{index['missingItemCount']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{index['target']['gpu']}`",
            f"- Vendor ID: `{index['target']['vendorID']}`",
            f"- Device ID: `{index['target']['deviceID']}`",
            f"- IOPCIMatch: `{index['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{index['target']['subsystemVendorID']}`",
            f"- Subsystem ID: `{index['target']['subsystemID']}`",
            "",
            "## Categories",
            "",
            "| Category | Total | Present | Missing |",
            "| --- | ---: | ---: | ---: |",
            *category_rows,
            "",
            "## Items",
            "",
            "| Path | Category | Kind | Status | Bytes |",
            "| --- | --- | --- | --- | ---: |",
            *item_rows,
            "",
            "## Safety Boundary",
            "",
            "This index is local-file-only.",
            "",
            "It indexes already-existing local files and records file metadata.",
            "",
            "It does not query live extension state, submit extension requests, activate DriverKit, request device ownership, collect live PCI inventory, access PCI configuration space, access MMIO, map BAR memory, execute RTX 5070 shaders, submit hardware commands, allocate RTX 5070 resources, load firmware, initialize display paths, initialize framebuffer, or reset the GPU.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a local-only H1mekaRTX diagnostics index."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Directory containing local reports. Defaults to current directory.",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root directory does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    index = build_index(root)

    json_path = out_dir / "local-diagnostics-index.json"
    md_path = out_dir / "local-diagnostics-index.md"

    json_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(index) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {index['decision']}")
    print(f"Present items: {index['presentItemCount']}/{index['itemCount']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
