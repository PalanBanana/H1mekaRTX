#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_compositor_sample_summary.v1"

EXPECTED_FILES = [
    "sample-metadata.json",
    "sw_vers.txt",
    "uptime.txt",
    "system_profiler-SPDisplaysDataType.txt",
    "system_profiler-SPDisplaysDataType.json",
    "ioreg-IODisplayConnect.txt",
    "ioreg-IOFramebuffer.txt",
    "ioreg-IOAccelerator.txt",
    "process-windowserver-dock.txt",
    "ui-preferences.txt",
    "ioreg-graphics-filtered.txt",
    "logs-ui-compositor-window.txt",
    "README.txt",
]

SURFACE_PATTERNS = {
    "dock": [r"\bDock\b", r"magnification"],
    "windowserver": [r"WindowServer"],
    "core_animation": [r"CoreAnimation", r"Core Animation"],
    "quartzcore": [r"QuartzCore"],
    "mission_control": [r"Mission Control", r"expose", r"Spaces"],
    "launchpad": [r"Launchpad"],
    "transparency_blur": [r"transparen", r"blur", r"backdrop", r"vibrancy"],
    "ioaccelerator": [r"IOAccelerator"],
    "iodisplay": [r"IODisplay"],
    "ioframebuffer": [r"IOFramebuffer"],
    "metal": [r"\bMetal\b"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def count_patterns(text: str, patterns: list[str]) -> int:
    return sum(len(re.findall(pattern, text, flags=re.IGNORECASE)) for pattern in patterns)


def first_matching_lines(text: str, patterns: list[str], limit: int = 40) -> list[str]:
    out: list[str] = []
    compiled = [re.compile(pattern, flags=re.IGNORECASE) for pattern in patterns]
    for line in text.splitlines():
        if any(pattern.search(line) for pattern in compiled):
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
        present = path.exists() and path.is_file()
        items.append(
            {
                "file": rel,
                "present": present,
                "bytes": path.stat().st_size if present else 0,
            }
        )
    return items


def parse_metadata(text: str) -> dict[str, Any]:
    if not text.strip():
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def build_summary(input_dir: Path) -> dict[str, Any]:
    texts = {rel: read_text(input_dir / rel) for rel in EXPECTED_FILES}
    metadata = parse_metadata(texts["sample-metadata.json"])

    combined = "\n".join(
        [
            texts["system_profiler-SPDisplaysDataType.txt"],
            texts["ioreg-IODisplayConnect.txt"],
            texts["ioreg-IOFramebuffer.txt"],
            texts["ioreg-IOAccelerator.txt"],
            texts["process-windowserver-dock.txt"],
            texts["ui-preferences.txt"],
            texts["ioreg-graphics-filtered.txt"],
            texts["logs-ui-compositor-window.txt"],
        ]
    )

    surface_hits = {
        name: count_patterns(combined, patterns)
        for name, patterns in SURFACE_PATTERNS.items()
    }

    present_count = sum(1 for item in file_inventory(input_dir) if item["present"])
    diagnostics_collected = present_count >= 8
    surface_hit_count = sum(1 for value in surface_hits.values() if value > 0)

    if diagnostics_collected and surface_hit_count:
        sample_result = "UI_COMPOSITOR_SAMPLE_DIAGNOSTICS_CAPTURED"
    elif diagnostics_collected:
        sample_result = "UI_COMPOSITOR_SAMPLE_CAPTURED_NO_RELEVANT_HINTS"
    else:
        sample_result = "INSUFFICIENT_UI_COMPOSITOR_SAMPLE_DIAGNOSTICS"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir),
        "metadata": {
            "label": metadata.get("label", ""),
            "log_window": metadata.get("logWindow", ""),
        },
        "classification": {
            "static_contract": False,
            "host_diagnostics": False,
            "graphics_stack_diagnostics": True,
            "runtime_probe": False,
            "real_gpu_command_execution": False,
            "ui_compositor_proof": False,
            "metal_proof": False,
        },
        "decisions": {
            "sample_result": sample_result,
            "ui_compositor_proof_result": "UNPROVEN",
            "metal_proof_result": "UNPROVEN",
            "rtx5070_ui_acceleration_claim": "NOT_CLAIMED",
            "rtx5070_metal_acceleration_claim": "NOT_CLAIMED",
        },
        "files": file_inventory(input_dir),
        "surface_hits": surface_hits,
        "previews": {
            "windowserver_dock": first_matching_lines(
                texts["process-windowserver-dock.txt"],
                [r"WindowServer", r"\bDock\b", r"loginwindow", r"ControlCenter"],
            ),
            "logs": first_matching_lines(
                texts["logs-ui-compositor-window.txt"],
                [
                    r"WindowServer",
                    r"\bDock\b",
                    r"CoreAnimation",
                    r"QuartzCore",
                    r"Metal",
                    r"IOAccelerator",
                    r"IODisplay",
                    r"IOFramebuffer",
                    r"blur",
                    r"backdrop",
                    r"vibrancy",
                ],
            ),
            "graphics_ioreg": first_matching_lines(
                texts["ioreg-graphics-filtered.txt"],
                [r"IODisplay", r"IOFramebuffer", r"IOGraphics", r"IOAccelerator", r"Metal", r"GPU"],
            ),
            "ui_preferences": first_matching_lines(
                texts["ui-preferences.txt"],
                [r".*"],
                limit=20,
            ),
        },
        "safety_boundary": {
            "read_only": True,
            "runs_log_show": True,
            "runs_ioreg": True,
            "runs_system_profiler": True,
            "driverkit_activation": False,
            "system_extension_activation": False,
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

    return "\n".join(
        [
            "# UI Compositor Sample Summary",
            "",
            f"Generated UTC: `{summary['generated_at_utc']}`",
            "",
            f"Input: `{summary['input_dir']}`",
            "",
            f"Label: `{summary['metadata']['label']}`",
            "",
            f"Log window: `{summary['metadata']['log_window']}`",
            "",
            "## Decisions",
            "",
            f"- Sample result: `{summary['decisions']['sample_result']}`",
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
            "## Surface Hints",
            "",
            "| Surface | Count |",
            "| --- | ---: |",
            *rows_from_counts(summary["surface_hits"]),
            "",
            "## Captured Files",
            "",
            "| File | Present | Bytes |",
            "| --- | --- | ---: |",
            *file_rows,
            "",
            "## Preview: WindowServer / Dock",
            "",
            preview_block(summary["previews"]["windowserver_dock"]),
            "",
            "## Preview: Logs",
            "",
            preview_block(summary["previews"]["logs"]),
            "",
            "## Preview: Graphics IORegistry",
            "",
            preview_block(summary["previews"]["graphics_ioreg"]),
            "",
            "## Preview: UI Preferences",
            "",
            preview_block(summary["previews"]["ui_preferences"]),
            "",
            "## Safety Boundary",
            "",
            "This report summarizes read-only UI compositor sample diagnostics. It does not activate DriverKit or System Extensions, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, write PCI config space, access MMIO, map BAR memory, submit GPU commands, execute RTX 5070 shaders, or claim RTX 5070 UI compositor or Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize H1mekaRTX UI compositor sample diagnostics.")
    parser.add_argument("--input-dir", required=True, help="Directory created by collect-ui-compositor-sample.sh")
    parser.add_argument("--out-dir", default=None, help="Output directory. Defaults to input-dir.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else input_dir

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary = build_summary(input_dir)

    json_path = out_dir / "ui-compositor-sample-summary.json"
    md_path = out_dir / "ui-compositor-sample-summary.md"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(summary) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Sample result: {summary['decisions']['sample_result']}")
    print("UI compositor proof: UNPROVEN")
    print("Metal proof: UNPROVEN")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
