#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.swiftui_local_report_file_picker_stub.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

SOURCE_FILES = [
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalReportFilePickerView.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/LocalReportFilePickerViewModel.swift",
    "tools/host-app-no-runtime-swiftui/Sources/H1mekaRTXHostApp/ContentView.swift",
]


def build_report(root: Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "target": TARGET,
        "decision": "SWIFTUI_LOCAL_REPORT_FILE_PICKER_STUB_READY",
        "plain_answer": "SwiftUI host app can present a local JSON report picker stub while keeping all driver and hardware paths disabled.",
        "goal": "RTX 5070 Metal full graphics acceleration research path",
        "actual_app_code_continues": True,
        "file_picker_stub_ready": True,
        "local_file_only": True,
        "json_only": True,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "source_files": SOURCE_FILES,
        "next_stage_recommendation": "Stage 59 should add a file-picker static contract checker and optional Swift build probe. Keep it local-file-only and no-runtime.",
        "safety_boundary": {
            "read_only": True,
            "swiftui_source_only": True,
            "file_picker_stub_only": True,
            "local_file_only": True,
            "json_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    files = [f"- `{item}`" for item in data["source_files"]]
    return "\n".join(
        [
            "# SwiftUI Local Report File Picker Stub",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Goal: {data['goal']}",
            "",
            f"Actual app code continues: `{data['actual_app_code_continues']}`",
            "",
            f"File picker stub ready: `{data['file_picker_stub_ready']}`",
            "",
            f"Local file only: `{data['local_file_only']}`",
            "",
            f"JSON only: `{data['json_only']}`",
            "",
            f"Live system queries allowed: `{data['live_system_queries_allowed']}`",
            "",
            f"Runtime buttons enabled: `{data['runtime_buttons_enabled']}`",
            "",
            f"Driver runtime allowed: `{data['driver_runtime_allowed']}`",
            "",
            f"Driver installation allowed: `{data['driver_installation_allowed']}`",
            "",
            f"Driver activation allowed: `{data['driver_activation_allowed']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Low-level hardware path allowed: `{data['low_level_hardware_path_allowed']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{data['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Source Files",
            "",
            *files,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a SwiftUI local JSON file picker stub only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate SwiftUI local report file picker stub report.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_report(root)

    json_path = out_dir / "swiftui-local-report-file-picker-stub-report.json"
    md_path = out_dir / "swiftui-local-report-file-picker-stub-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
