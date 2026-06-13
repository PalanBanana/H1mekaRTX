#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_gpu_attribution_summary.v1"

EXPECTED_FILES = [
    "attribution-metadata.json",
    "sw_vers.txt",
    "system_profiler-SPDisplaysDataType.txt",
    "system_profiler-SPDisplaysDataType.json",
    "ioreg-IOFramebuffer.txt",
    "ioreg-IOAccelerator.txt",
    "ioreg-IODisplayConnect.txt",
    "process-windowserver-dock.txt",
    "ioreg-display-accelerator-filtered.txt",
    "logs-ui-gpu-attribution.txt",
    "README.txt",
]

PATTERNS = {
    "windowserver": [r"WindowServer"],
    "dock": [r"\bDock\b"],
    "display": [r"IODisplay", r"display"],
    "framebuffer": [r"IOFramebuffer", r"framebuffer"],
    "accelerator": [r"IOAccelerator", r"accelerator"],
    "metal": [r"\bMetal\b"],
    "gpu": [r"\bGPU\b"],
    "nvidia": [r"NVIDIA", r"10de"],
    "rtx5070": [r"RTX\s*5070", r"2f04"],
    "apple_gpu": [r"AGX", r"AppleCLCD", r"Apple"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def parse_json_object(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def parse_display_devices(text: str) -> list[dict[str, Any]]:
    data = parse_json_object(text)
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


def file_inventory(root: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for rel in EXPECTED_FILES:
        path = root / rel
        present = path.exists() and path.is_file()
        items.append(
            {
                "file": rel,
                "present": present,
                "bytes": path.stat().st_size if present else 0,
            }
        )
    return items


def first_matching_lines(text: str, patterns: list[str], limit: int = 40) -> list[str]:
    compiled = [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
    out: list[str] = []
    for line in text.splitlines():
        if any(pattern.search(line) for pattern in compiled):
            cleaned = line.strip()
            if cleaned:
                out.append(cleaned)
        if len(out) >= limit:
            break
    return out


def build_summary(input_dir: Path) -> dict[str, Any]:
    texts = {rel: read_text(input_dir / rel) for rel in EXPECTED_FILES}
    metadata = parse_json_object(texts["attribution-metadata.json"])
    combined = "\n".join(
        [
            texts["system_profiler-SPDisplaysDataType.txt"],
            texts["ioreg-IOFramebuffer.txt"],
            texts["ioreg-IOAccelerator.txt"],
            texts["ioreg-IODisplayConnect.txt"],
            texts["process-windowserver-dock.txt"],
            texts["ioreg-display-accelerator-filtered.txt"],
            texts["logs-ui-gpu-attribution.txt"],
        ]
    )
    candidate_hits = {key: count_patterns(combined, patterns) for key, patterns in PATTERNS.items()}
    present_count = sum(1 for item in file_inventory(input_dir) if item["present"])
    candidates_captured = (
        present_count >= 7
        and candidate_hits["windowserver"] > 0
        and (candidate_hits["display"] > 0 or candidate_hits["framebuffer"] > 0)
        and candidate_hits["accelerator"] > 0
    )

    if candidates_captured:
        attribution_result = "UI_GPU_ATTRIBUTION_CANDIDATES_CAPTURED"
    elif present_count >= 7:
        attribution_result = "UI_GPU_ATTRIBUTION_CAPTURED_NO_RELEVANT_HINTS"
    else:
        attribution_result = "INSUFFICIENT_UI_GPU_ATTRIBUTION_DIAGNOSTICS"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "metadata": {
            "log_window": metadata.get("logWindow", ""),
        },
        "classification": {
            "graphics_stack_diagnostics": True,
            "trusted_ui_gpu_attribution": False,
            "runtime_probe": False,
            "real_gpu_command_execution": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
        "decisions": {
            "ui_gpu_attribution_result": attribution_result,
            "trusted_ui_gpu_attribution_result": "UNPROVEN",
            "rtx5070_ui_gpu_attribution_result": "UNPROVEN",
            "ui_compositor_proof_result": "UNPROVEN",
            "metal_proof_result": "UNPROVEN",
            "rtx5070_ui_acceleration_claim": "NOT_CLAIMED",
            "rtx5070_metal_acceleration_claim": "NOT_CLAIMED",
        },
        "files": file_inventory(input_dir),
        "candidate_hits": candidate_hits,
        "display_devices": parse_display_devices(texts["system_profiler-SPDisplaysDataType.json"]),
        "previews": {
            "display_accelerator_ioreg": first_matching_lines(
                texts["ioreg-display-accelerator-filtered.txt"],
                [r"IOFramebuffer", r"IOAccelerator", r"IODisplay", r"Metal", r"GPU", r"NVIDIA", r"10de", r"2f04", r"AGX", r"Apple"],
            ),
            "windowserver_dock": first_matching_lines(
                texts["process-windowserver-dock.txt"],
                [r"WindowServer", r"\bDock\b", r"loginwindow", r"ControlCenter"],
            ),
            "logs": first_matching_lines(
                texts["logs-ui-gpu-attribution.txt"],
                [r"WindowServer", r"\bDock\b", r"IOAccelerator", r"IOFramebuffer", r"IODisplay", r"Metal", r"GPU", r"display"],
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
            "process_injection": False,
            "windowserver_injection": False,
            "dock_injection": False,
            "private_framework_patching": False,
            "sip_bypass": False,
            "amfi_bypass": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "gpu_command_submission": False,
            "rtx5070_shader_execution": False,
            "trusted_ui_gpu_attribution_claim": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def rows_from_counts(counts: dict[str, Any]) -> list[str]:
    return [f"| `{key}` | `{value}` |" for key, value in counts.items()]


def preview_block(lines: list[str]) -> str:
    if not lines:
        return "- No preview lines found."
    return "\n".join(f"- `{line}`" for line in lines)


def markdown_report(summary: dict[str, Any]) -> str:
    file_rows = [
        f"| `{item['file']}` | {'yes' if item['present'] else 'no'} | `{item['bytes']}` |"
        for item in summary["files"]
    ]
    device_rows = []
    for item in summary["display_devices"]:
        device_rows.append(
            f"| `{item.get('name', '')}` | `{item.get('chipset_model', '')}` | `{item.get('vendor', '')}` | `{item.get('device_id', '')}` | `{item.get('metal_support', '')}` |"
        )
    if not device_rows:
        device_rows = ["| `none parsed` |  |  |  |  |"]

    return "\n".join(
        [
            "# UI GPU Attribution Summary",
            "",
            f"Generated UTC: `{summary['generated_at_utc']}`",
            "",
            f"Input: `{summary['input_dir']}`",
            "",
            f"Log window: `{summary['metadata']['log_window']}`",
            "",
            "## Decisions",
            "",
            f"- UI GPU attribution result: `{summary['decisions']['ui_gpu_attribution_result']}`",
            f"- Trusted UI GPU attribution result: `{summary['decisions']['trusted_ui_gpu_attribution_result']}`",
            f"- RTX 5070 UI GPU attribution result: `{summary['decisions']['rtx5070_ui_gpu_attribution_result']}`",
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
            "## Candidate Hits",
            "",
            "| Candidate | Count |",
            "| --- | ---: |",
            *rows_from_counts(summary["candidate_hits"]),
            "",
            "## Parsed Display Devices",
            "",
            "| Name | Chipset | Vendor | Device ID | Metal Support |",
            "| --- | --- | --- | --- | --- |",
            *device_rows,
            "",
            "## Captured Files",
            "",
            "| File | Present | Bytes |",
            "| --- | --- | ---: |",
            *file_rows,
            "",
            "## Preview: Display / Accelerator IORegistry",
            "",
            preview_block(summary["previews"]["display_accelerator_ioreg"]),
            "",
            "## Preview: WindowServer / Dock",
            "",
            preview_block(summary["previews"]["windowserver_dock"]),
            "",
            "## Preview: Logs",
            "",
            preview_block(summary["previews"]["logs"]),
            "",
            "## Safety Boundary",
            "",
            "This report summarizes read-only candidate attribution diagnostics. It does not activate DriverKit or System Extensions, request device ownership, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, write PCI config space, access MMIO, map BAR memory, submit GPU commands, execute RTX 5070 shaders, or claim trusted UI GPU attribution, RTX 5070 UI compositor acceleration, or RTX 5070 Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize H1mekaRTX UI GPU attribution diagnostics.")
    parser.add_argument("--input-dir", required=True, help="Directory created by collect-ui-gpu-attribution.sh")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to input-dir.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else input_dir
    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(input_dir)

    json_path = out_dir / "ui-gpu-attribution-summary.json"
    md_path = out_dir / "ui-gpu-attribution-summary.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(summary) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"UI GPU attribution: {summary['decisions']['ui_gpu_attribution_result']}")
    print("Trusted UI GPU attribution: UNPROVEN")
    print("UI compositor proof: UNPROVEN")
    print("Metal proof: UNPROVEN")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
