#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.driverkit_local_toolchain_build_preflight_report.v1"

COMMANDS = {
    "xcode_select_path": ["xcode-select", "-p"],
    "xcodebuild_version": ["xcodebuild", "-version"],
    "xcrun_show_sdk_path_macosx": ["xcrun", "--sdk", "macosx", "--show-sdk-path"],
    "xcrun_show_sdk_path_driverkit": ["xcrun", "--sdk", "driverkit", "--show-sdk-path"],
    "swiftc_version": ["xcrun", "swiftc", "--version"],
    "clangxx_version": ["xcrun", "clang++", "--version"],
}

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
    try:
        result = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout)
        return {
            "command": cmd,
            "available": True,
            "returncode": result.returncode,
            "stdout": result.stdout[-8000:],
            "stderr": result.stderr[-8000:],
        }
    except FileNotFoundError:
        return {
            "command": cmd,
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "command not found",
        }
    except subprocess.TimeoutExpired:
        return {
            "command": cmd,
            "available": True,
            "returncode": None,
            "stdout": "",
            "stderr": "timeout",
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/driverkit-toolchain-preflight")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}
    for key, cmd in COMMANDS.items():
        if shutil.which(cmd[0]):
            commands[key] = run_cmd(cmd)
        else:
            commands[key] = {
                "command": cmd,
                "available": False,
                "returncode": None,
                "stdout": "",
                "stderr": "command not found",
            }

    scaffold_inputs = [
        "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist",
        "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift",
        "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist",
        "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Sources/H1mekaRTXDriver.cpp",
        "tools/driverkit-buildable-scaffold/build-plan.json",
    ]

    scaffold_status = {rel: (root / rel).exists() for rel in scaffold_inputs}

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_DRIVERKIT_LOCAL_TOOLCHAIN_BUILD_PREFLIGHT",
        "local_preflight_only": True,
        "host_report_bundle_local_only": True,
        "build_attempted": False,
        "signing_attempted": False,
        "install_attempted": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "toolchain_commands": commands,
        "scaffold_inputs": scaffold_status,
        "derived": {
            "xcodebuild_available": commands["xcodebuild_version"]["available"] and commands["xcodebuild_version"]["returncode"] == 0,
            "xcrun_available": commands["xcrun_show_sdk_path_macosx"]["available"],
            "macos_sdk_available": commands["xcrun_show_sdk_path_macosx"]["returncode"] == 0,
            "driverkit_sdk_available": commands["xcrun_show_sdk_path_driverkit"]["returncode"] == 0,
            "swiftc_available": commands["swiftc_version"]["returncode"] == 0,
            "clangxx_available": commands["clangxx_version"]["returncode"] == 0,
            "scaffold_inputs_present": all(scaffold_status.values()),
        },
    }

    json_path = out_dir / "driverkit-local-toolchain-build-preflight.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{k}` | `{v['available']}` | `{v['returncode']}` |"
        for k, v in commands.items()
    )
    scaffold_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in scaffold_status.items())

    md = f"""# DriverKit Local Toolchain Build Preflight

- Generated At UTC: `{report['generated_at_utc']}`
- Local Preflight Only: `True`
- Build Attempted: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Toolchain Commands

| Key | Available | Return Code |
| --- | --- | --- |
{rows}

## Scaffold Inputs

| Path | Present |
| --- | --- |
{scaffold_rows}

## Derived Toolchain Status

{json.dumps(report['derived'], indent=2, sort_keys=True)}
"""
    md_path = out_dir / "driverkit-local-toolchain-build-preflight.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_DRIVERKIT_LOCAL_TOOLCHAIN_PREFLIGHT_RECORDED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
