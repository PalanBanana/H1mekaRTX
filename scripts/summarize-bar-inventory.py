#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TARGET = {
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}


EXPECTED_FILES = [
    "sw_vers.txt",
    "uname.txt",
    "system_profiler-SPPCIDataType.txt",
    "system_profiler-SPDisplaysDataType.txt",
    "ioreg-IODeviceTree.txt",
    "ioreg-IOService.txt",
    "ioreg-rtx5070-filtered.txt",
    "logs-driverkit-pci-last30m.txt",
    "README.txt",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def parse_sw_vers(text: str) -> dict[str, str]:
    result: dict[str, str] = {}

    for line in text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()

    return {
        "product_name": result.get("ProductName", ""),
        "product_version": result.get("ProductVersion", ""),
        "build_version": result.get("BuildVersion", ""),
    }


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def first_matching_lines(text: str, patterns: list[str], limit: int = 40) -> list[str]:
    out: list[str] = []

    for line in text.splitlines():
        haystack = line.lower()

        if any(pattern.lower() in haystack for pattern in patterns):
            cleaned = line.strip()
            if cleaned:
                out.append(cleaned)

        if len(out) >= limit:
            break

    return out


def file_inventory(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    for name in EXPECTED_FILES:
        path = root / name
        items.append(
            {
                "file": name,
                "present": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )

    return items


def build_summary(input_dir: Path) -> dict[str, Any]:
    sw_vers = read_text(input_dir / "sw_vers.txt")
    uname = read_text(input_dir / "uname.txt")
    pci = read_text(input_dir / "system_profiler-SPPCIDataType.txt")
    displays = read_text(input_dir / "system_profiler-SPDisplaysDataType.txt")
    filtered = read_text(input_dir / "ioreg-rtx5070-filtered.txt")
    logs = read_text(input_dir / "logs-driverkit-pci-last30m.txt")

    combined_target_surface = "\n".join([pci, displays, filtered])

    target_hits = {
        "vendor_10de": count_pattern(combined_target_surface, r"10de"),
        "device_2f04": count_pattern(combined_target_surface, r"2f04"),
        "iopcimatch_2f0410de": count_pattern(combined_target_surface, r"2f0410de"),
        "subsystem_vendor_1458": count_pattern(combined_target_surface, r"1458"),
        "subsystem_id_417e": count_pattern(combined_target_surface, r"417e"),
    }

    keyword_hits = {
        "assigned_addresses": count_pattern(filtered, r"assigned-addresses"),
        "reg": count_pattern(filtered, r"\breg\b"),
        "class_code": count_pattern(filtered, r"class-code"),
        "device_id": count_pattern(filtered, r"device-id"),
        "vendor_id": count_pattern(filtered, r"vendor-id"),
        "subsystem": count_pattern(filtered, r"subsystem"),
        "iopcimatch": count_pattern(filtered, r"IOPCIMatch"),
        "slot_name": count_pattern(filtered, r"AAPL,slot-name"),
    }

    log_hits = {
        "h1mekartx": count_pattern(logs, r"H1mekaRTX"),
        "iopcidevice": count_pattern(logs, r"IOPCIDevice"),
        "driverkit": count_pattern(logs, r"DriverKit"),
        "sysextd": count_pattern(logs, r"sysextd"),
    }

    likely_target_present = (
        target_hits["vendor_10de"] > 0
        and (
            target_hits["device_2f04"] > 0
            or target_hits["iopcimatch_2f0410de"] > 0
        )
    )

    return {
        "schema": "h1mekartx.bar_inventory_summary.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "target": TARGET,
        "host": {
            "sw_vers": parse_sw_vers(sw_vers),
            "uname": uname.strip(),
        },
        "files": file_inventory(input_dir),
        "target_hits": target_hits,
        "keyword_hits": keyword_hits,
        "log_hits": log_hits,
        "likely_target_present": likely_target_present,
        "filtered_ioreg_preview": first_matching_lines(
            filtered,
            [
                "10de",
                "2f04",
                "IOPCIMatch",
                "assigned-addresses",
                "reg",
                "AAPL,slot-name",
                "class-code",
                "device-id",
                "vendor-id",
                "subsystem",
            ],
            limit=40,
        ),
        "safety_boundary": {
            "read_only": True,
            "runs_ioreg": False,
            "runs_system_profiler": False,
            "pci_config_writes": False,
            "mmio_writes": False,
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


def markdown_report(summary: dict[str, Any]) -> str:
    sw = summary["host"]["sw_vers"]

    file_lines = []
    for item in summary["files"]:
        present = "yes" if item["present"] else "no"
        file_lines.append(f"| `{item['file']}` | {present} | {item['bytes']} |")

    preview_lines = summary["filtered_ioreg_preview"]
    if preview_lines:
        preview = "\n".join(f"- `{line}`" for line in preview_lines)
    else:
        preview = "- No filtered IORegistry preview lines found."

    target = summary["target"]
    target_hits = summary["target_hits"]
    keyword_hits = summary["keyword_hits"]
    log_hits = summary["log_hits"]

    lines = [
        "# BAR Inventory Summary",
        "",
        "## Input",
        "",
        f"`{summary['input_dir']}`",
        "",
        "## Host",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Product Name | `{sw.get('product_name', '')}` |",
        f"| Product Version | `{sw.get('product_version', '')}` |",
        f"| Build Version | `{sw.get('build_version', '')}` |",
        f"| Kernel | `{summary['host'].get('uname', '')}` |",
        "",
        "## RTX 5070 PCI Target",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Vendor ID | `{target['vendor_id']}` |",
        f"| Device ID | `{target['device_id']}` |",
        f"| IOPCIMatch | `{target['iopcimatch']}` |",
        f"| Subsystem Vendor ID | `{target['subsystem_vendor_id']}` |",
        f"| Subsystem ID | `{target['subsystem_id']}` |",
        "",
        "## Target Detection",
        "",
        "| Signal | Count |",
        "| --- | ---: |",
        f"| vendor_10de | {target_hits['vendor_10de']} |",
        f"| device_2f04 | {target_hits['device_2f04']} |",
        f"| iopcimatch_2f0410de | {target_hits['iopcimatch_2f0410de']} |",
        f"| subsystem_vendor_1458 | {target_hits['subsystem_vendor_1458']} |",
        f"| subsystem_id_417e | {target_hits['subsystem_id_417e']} |",
        "",
        f"Likely target present: `{summary['likely_target_present']}`",
        "",
        "## BAR / PCI Keyword Hints",
        "",
        "| Keyword | Count |",
        "| --- | ---: |",
        f"| assigned-addresses | {keyword_hits['assigned_addresses']} |",
        f"| reg | {keyword_hits['reg']} |",
        f"| class-code | {keyword_hits['class_code']} |",
        f"| device-id | {keyword_hits['device_id']} |",
        f"| vendor-id | {keyword_hits['vendor_id']} |",
        f"| subsystem | {keyword_hits['subsystem']} |",
        f"| IOPCIMatch | {keyword_hits['iopcimatch']} |",
        f"| AAPL,slot-name | {keyword_hits['slot_name']} |",
        "",
        "## Log Hints",
        "",
        "| Keyword | Count |",
        "| --- | ---: |",
        f"| H1mekaRTX | {log_hits['h1mekartx']} |",
        f"| IOPCIDevice | {log_hits['iopcidevice']} |",
        f"| DriverKit | {log_hits['driverkit']} |",
        f"| sysextd | {log_hits['sysextd']} |",
        "",
        "## Captured Files",
        "",
        "| File | Present | Bytes |",
        "| --- | --- | ---: |",
        *file_lines,
        "",
        "## Filtered IORegistry Preview",
        "",
        preview,
        "",
        "## Safety Boundary",
        "",
        "This report is generated from already-collected diagnostics files only.",
        "",
        "It does not run ioreg, system_profiler, DriverKit activation, PCI config-space writes, MMIO writes, BAR poking, GPU reset logic, firmware loading, GSP initialization, display engine initialization, framebuffer initialization, or Metal acceleration attempts.",
        "",
    ]

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize H1mekaRTX BAR inventory diagnostics output."
    )
    parser.add_argument(
        "input_dir",
        help="Directory created by scripts/collect-bar-inventory.sh",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Output directory. Defaults to input_dir.",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else input_dir

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(input_dir)

    json_path = out_dir / "bar-inventory-summary.json"
    md_path = out_dir / "bar-inventory-summary.md"

    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(summary) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
