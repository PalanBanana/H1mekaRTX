#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.host_ui_diagnostics_summary.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

EXPECTED_FILES = [
    "sw_vers.txt",
    "uname.txt",
    "arch.txt",
    "csrutil-status.txt",
    "system_profiler-SPHardwareDataType.txt",
    "system_profiler-SPPCIDataType.txt",
    "system_profiler-SPDisplaysDataType.txt",
    "system_profiler-SPDisplaysDataType.json",
    "ioreg-IODeviceTree.txt",
    "ioreg-IOService.txt",
    "ioreg-IOPCIDevice.txt",
    "ioreg-IODisplayConnect.txt",
    "ioreg-IOFramebuffer.txt",
    "ioreg-IOAccelerator.txt",
    "ioreg-rtx5070-filtered.txt",
    "ioreg-graphics-filtered.txt",
    "process-windowserver-dock.txt",
    "frameworks-graphics.txt",
    "ui-preferences.txt",
    "logs-graphics-ui-last30m.txt",
    "README.txt",
]

HOST_DIAGNOSTIC_FILES = [
    "sw_vers.txt",
    "uname.txt",
    "arch.txt",
    "csrutil-status.txt",
    "system_profiler-SPHardwareDataType.txt",
    "system_profiler-SPPCIDataType.txt",
    "ioreg-IODeviceTree.txt",
    "ioreg-IOService.txt",
    "ioreg-IOPCIDevice.txt",
    "ioreg-rtx5070-filtered.txt",
]

GRAPHICS_STACK_FILES = [
    "system_profiler-SPDisplaysDataType.txt",
    "system_profiler-SPDisplaysDataType.json",
    "ioreg-IODisplayConnect.txt",
    "ioreg-IOFramebuffer.txt",
    "ioreg-IOAccelerator.txt",
    "ioreg-graphics-filtered.txt",
    "process-windowserver-dock.txt",
    "frameworks-graphics.txt",
    "ui-preferences.txt",
    "logs-graphics-ui-last30m.txt",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE))


def parse_sw_vers(text: str) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        pairs[key.strip()] = value.strip()

    return {
        "product_name": pairs.get("ProductName", ""),
        "product_version": pairs.get("ProductVersion", ""),
        "build_version": pairs.get("BuildVersion", ""),
    }


def first_matching_lines(text: str, patterns: list[str], limit: int = 50) -> list[str]:
    out: list[str] = []
    lowered_patterns = [pattern.lower() for pattern in patterns]

    for line in text.splitlines():
        haystack = line.lower()
        if any(pattern in haystack for pattern in lowered_patterns):
            cleaned = line.strip()
            if cleaned:
                out.append(cleaned)
        if len(out) >= limit:
            break

    return out


def file_inventory(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for rel in EXPECTED_FILES:
        path = root / rel
        items.append(
            {
                "file": rel,
                "present": path.exists() and path.is_file(),
                "bytes": path.stat().st_size if path.exists() and path.is_file() else 0,
            }
        )
    return items


def present_expected_count(root: Path, files: list[str]) -> int:
    return sum(1 for rel in files if (root / rel).exists() and (root / rel).is_file())


def parse_displays_json(text: str) -> list[dict[str, Any]]:
    if not text.strip():
        return []

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    devices: list[dict[str, Any]] = []
    for item in data.get("SPDisplaysDataType", []):
        if not isinstance(item, dict):
            continue
        devices.append(
            {
                "name": item.get("_name", ""),
                "chipset_model": item.get("sppci_model", item.get("spdisplays_chipset", "")),
                "vendor": item.get("spdisplays_vendor", ""),
                "device_id": item.get("spdisplays_device-id", ""),
                "metal_support": item.get("spdisplays_metal", ""),
                "displays": item.get("spdisplays_ndrvs", []),
            }
        )
    return devices


def build_summary(input_dir: Path) -> dict[str, Any]:
    texts = {rel: read_text(input_dir / rel) for rel in EXPECTED_FILES}

    pci_surface = "\n".join(
        [
            texts["system_profiler-SPPCIDataType.txt"],
            texts["system_profiler-SPDisplaysDataType.txt"],
            texts["ioreg-IOPCIDevice.txt"],
            texts["ioreg-rtx5070-filtered.txt"],
        ]
    )
    graphics_surface = "\n".join(
        [
            texts["system_profiler-SPDisplaysDataType.txt"],
            texts["ioreg-IODisplayConnect.txt"],
            texts["ioreg-IOFramebuffer.txt"],
            texts["ioreg-IOAccelerator.txt"],
            texts["ioreg-graphics-filtered.txt"],
            texts["process-windowserver-dock.txt"],
            texts["frameworks-graphics.txt"],
            texts["logs-graphics-ui-last30m.txt"],
        ]
    )
    host_surface = "\n".join(texts[rel] for rel in HOST_DIAGNOSTIC_FILES)

    target_hits = {
        "vendor_10de": count_pattern(pci_surface, r"10de"),
        "device_2f04": count_pattern(pci_surface, r"2f04"),
        "iopcimatch_2f0410de": count_pattern(pci_surface, r"2f0410de"),
        "subsystem_vendor_1458": count_pattern(pci_surface, r"1458"),
        "subsystem_id_417e": count_pattern(pci_surface, r"417e"),
        "nvidia": count_pattern(pci_surface, r"NVIDIA"),
        "rtx5070": count_pattern(pci_surface, r"RTX\s*5070"),
    }
    likely_target_present = (
        target_hits["vendor_10de"] > 0
        and (target_hits["device_2f04"] > 0 or target_hits["iopcimatch_2f0410de"] > 0)
    )

    bar_inventory_hints = {
        "assigned_addresses": count_pattern(pci_surface, r"assigned-addresses"),
        "reg": count_pattern(pci_surface, r"\breg\b"),
        "class_code": count_pattern(pci_surface, r"class-code|Class Code"),
        "device_id": count_pattern(pci_surface, r"device-id|Device ID"),
        "vendor_id": count_pattern(pci_surface, r"vendor-id|Vendor ID"),
        "subsystem": count_pattern(pci_surface, r"subsystem"),
        "iopcimatch": count_pattern(pci_surface, r"IOPCIMatch"),
        "slot_name": count_pattern(pci_surface, r"AAPL,slot-name|Slot"),
    }

    graphics_stack_hits = {
        "iodisplay": count_pattern(graphics_surface, r"IODisplay"),
        "ioframebuffer": count_pattern(graphics_surface, r"IOFramebuffer"),
        "iographics": count_pattern(graphics_surface, r"IOGraphics"),
        "ioaccelerator": count_pattern(graphics_surface, r"IOAccelerator"),
        "metal": count_pattern(graphics_surface, r"Metal"),
        "windowserver": count_pattern(graphics_surface, r"WindowServer"),
        "dock": count_pattern(graphics_surface, r"\bDock\b"),
        "core_animation": count_pattern(graphics_surface, r"CoreAnimation|Core Animation"),
        "quartzcore": count_pattern(graphics_surface, r"QuartzCore"),
        "blur_transparency": count_pattern(graphics_surface, r"blur|transparen|vibrancy|backdrop"),
    }

    host_file_count = present_expected_count(input_dir, HOST_DIAGNOSTIC_FILES)
    graphics_file_count = present_expected_count(input_dir, GRAPHICS_STACK_FILES)
    host_diagnostics_collected = host_file_count >= 6
    graphics_stack_diagnostics_collected = graphics_file_count >= 5

    if likely_target_present:
        host_result = "TARGET_PRESENT_HOST_DIAGNOSTICS"
    elif host_diagnostics_collected:
        host_result = "TARGET_NOT_DETECTED_IN_HOST_DIAGNOSTICS"
    else:
        host_result = "INSUFFICIENT_HOST_DIAGNOSTICS"

    stack_hint_count = sum(1 for value in graphics_stack_hits.values() if value > 0)
    if graphics_stack_diagnostics_collected and stack_hint_count:
        graphics_result = "GRAPHICS_STACK_HINTS_PRESENT"
    elif graphics_stack_diagnostics_collected:
        graphics_result = "GRAPHICS_STACK_CAPTURED_NO_RELEVANT_HINTS"
    else:
        graphics_result = "INSUFFICIENT_GRAPHICS_STACK_DIAGNOSTICS"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "target": TARGET,
        "classification": {
            "host_diagnostics": True,
            "graphics_stack_diagnostics": True,
            "runtime_probe": False,
            "real_gpu_command_execution": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
        "decisions": {
            "host_diagnostics_result": host_result,
            "graphics_stack_diagnostics_result": graphics_result,
            "runtime_probe_result": "NOT_ATTEMPTED",
            "real_gpu_command_execution_result": "NOT_ATTEMPTED",
            "ui_compositor_proof_result": "UNPROVEN",
            "metal_proof_result": "UNPROVEN",
            "rtx5070_ui_acceleration_claim": "NOT_CLAIMED",
            "rtx5070_metal_acceleration_claim": "NOT_CLAIMED",
        },
        "host": {
            "sw_vers": parse_sw_vers(texts["sw_vers.txt"]),
            "uname": texts["uname.txt"].strip(),
            "arch": texts["arch.txt"].strip(),
            "sip": texts["csrutil-status.txt"].strip(),
        },
        "files": file_inventory(input_dir),
        "host_diagnostic_file_count": host_file_count,
        "graphics_stack_file_count": graphics_file_count,
        "target_hits": target_hits,
        "likely_target_present": likely_target_present,
        "bar_inventory_hints": bar_inventory_hints,
        "graphics_stack_hits": graphics_stack_hits,
        "metal_device_observations": parse_displays_json(texts["system_profiler-SPDisplaysDataType.json"]),
        "previews": {
            "rtx5070_ioreg": first_matching_lines(
                texts["ioreg-rtx5070-filtered.txt"],
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
            ),
            "graphics_stack": first_matching_lines(
                texts["ioreg-graphics-filtered.txt"],
                [
                    "IODisplay",
                    "IOFramebuffer",
                    "IOGraphics",
                    "IOAccelerator",
                    "Metal",
                    "display",
                    "accelerator",
                    "GPU",
                ],
            ),
            "windowserver_dock": first_matching_lines(
                texts["process-windowserver-dock.txt"],
                ["WindowServer", "Dock", "loginwindow", "ControlCenter"],
                limit=20,
            ),
            "display_metal": first_matching_lines(
                texts["system_profiler-SPDisplaysDataType.txt"],
                ["Chipset", "Vendor", "Device ID", "Metal", "Displays", "Resolution"],
                limit=40,
            ),
        },
        "safety_boundary": {
            "read_only": True,
            "runs_ioreg": True,
            "runs_system_profiler": True,
            "runs_log_show": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "metal_acceleration_attempt": False,
            "ui_compositor_acceleration_claim": False,
        },
    }


def rows_from_counts(counts: dict[str, Any]) -> list[str]:
    return [f"| `{key}` | `{value}` |" for key, value in counts.items()]


def preview_block(lines: list[str]) -> str:
    if not lines:
        return "- No preview lines found."
    return "\n".join(f"- `{line}`" for line in lines)


def markdown_report(summary: dict[str, Any]) -> str:
    sw = summary["host"]["sw_vers"]
    file_rows = [
        f"| `{item['file']}` | {'yes' if item['present'] else 'no'} | `{item['bytes']}` |"
        for item in summary["files"]
    ]
    metal_rows = []
    for item in summary["metal_device_observations"]:
        metal_rows.append(
            f"| `{item.get('name', '')}` | `{item.get('chipset_model', '')}` | `{item.get('vendor', '')}` | `{item.get('device_id', '')}` | `{item.get('metal_support', '')}` |"
        )
    if not metal_rows:
        metal_rows = ["| `none parsed` |  |  |  |  |"]

    return "\n".join(
        [
            "# Host + UI Compositor Diagnostics Summary",
            "",
            f"Generated UTC: `{summary['generated_at_utc']}`",
            "",
            f"Input: `{summary['input_dir']}`",
            "",
            "## Decisions",
            "",
            f"- Host diagnostics result: `{summary['decisions']['host_diagnostics_result']}`",
            f"- Graphics stack diagnostics result: `{summary['decisions']['graphics_stack_diagnostics_result']}`",
            f"- Runtime probe result: `{summary['decisions']['runtime_probe_result']}`",
            f"- Real GPU command execution result: `{summary['decisions']['real_gpu_command_execution_result']}`",
            f"- UI compositor proof result: `{summary['decisions']['ui_compositor_proof_result']}`",
            f"- Metal proof result: `{summary['decisions']['metal_proof_result']}`",
            f"- RTX 5070 UI acceleration claim: `{summary['decisions']['rtx5070_ui_acceleration_claim']}`",
            f"- RTX 5070 Metal acceleration claim: `{summary['decisions']['rtx5070_metal_acceleration_claim']}`",
            "",
            "## Classification",
            "",
            "| Level | Value |",
            "| --- | --- |",
            *rows_from_counts(summary["classification"]),
            "",
            "## Host",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Product Name | `{sw.get('product_name', '')}` |",
            f"| Product Version | `{sw.get('product_version', '')}` |",
            f"| Build Version | `{sw.get('build_version', '')}` |",
            f"| Kernel | `{summary['host'].get('uname', '')}` |",
            f"| Architecture | `{summary['host'].get('arch', '')}` |",
            f"| SIP | `{summary['host'].get('sip', '')}` |",
            "",
            "## RTX 5070 Target",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| GPU | `{summary['target']['gpu']}` |",
            f"| Vendor ID | `{summary['target']['vendor_id']}` |",
            f"| Device ID | `{summary['target']['device_id']}` |",
            f"| IOPCIMatch | `{summary['target']['iopcimatch']}` |",
            f"| Subsystem Vendor ID | `{summary['target']['subsystem_vendor_id']}` |",
            f"| Subsystem ID | `{summary['target']['subsystem_id']}` |",
            "",
            "## Host Diagnostics Target Hits",
            "",
            "| Signal | Count |",
            "| --- | ---: |",
            *rows_from_counts(summary["target_hits"]),
            "",
            f"Likely target present: `{summary['likely_target_present']}`",
            "",
            "## BAR-Like Inventory Hints",
            "",
            "| Signal | Count |",
            "| --- | ---: |",
            *rows_from_counts(summary["bar_inventory_hints"]),
            "",
            "## Graphics Stack Diagnostics Hints",
            "",
            "| Signal | Count |",
            "| --- | ---: |",
            *rows_from_counts(summary["graphics_stack_hits"]),
            "",
            "## Parsed Display / Metal Observations",
            "",
            "| Name | Chipset | Vendor | Device ID | Metal Support |",
            "| --- | --- | --- | --- | --- |",
            *metal_rows,
            "",
            "## Captured Files",
            "",
            "| File | Present | Bytes |",
            "| --- | --- | ---: |",
            *file_rows,
            "",
            "## Preview: RTX 5070 IORegistry",
            "",
            preview_block(summary["previews"]["rtx5070_ioreg"]),
            "",
            "## Preview: Graphics Stack",
            "",
            preview_block(summary["previews"]["graphics_stack"]),
            "",
            "## Preview: WindowServer / Dock",
            "",
            preview_block(summary["previews"]["windowserver_dock"]),
            "",
            "## Preview: Display / Metal",
            "",
            preview_block(summary["previews"]["display_metal"]),
            "",
            "## Safety Boundary",
            "",
            "This summary is generated from collected diagnostics files.",
            "",
            "It may summarize read-only ioreg, system_profiler, process, defaults, framework path, and log output. It does not activate DriverKit or System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, poke BAR memory, submit RTX 5070 commands, execute RTX 5070 shaders, initialize display/framebuffer paths, or claim RTX 5070 UI compositor or Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize H1mekaRTX host + UI compositor diagnostics.")
    parser.add_argument("--input-dir", required=True, help="Directory created by collect-host-diagnostics.sh")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to input-dir.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else input_dir

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(input_dir)

    json_path = out_dir / "host-diagnostics-summary.json"
    md_path = out_dir / "host-diagnostics-summary.md"

    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(summary) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Host diagnostics: {summary['decisions']['host_diagnostics_result']}")
    print(f"Graphics stack diagnostics: {summary['decisions']['graphics_stack_diagnostics_result']}")
    print("UI compositor proof: UNPROVEN")
    print("Metal proof: UNPROVEN")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
