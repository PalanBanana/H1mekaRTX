#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.compile_only_target_smoke_test_report.v1"

def run_cmd(cmd: list[str], timeout: int = 60) -> dict:
    try:
        result = subprocess.run(cmd, check=False, text=True, capture_output=True, timeout=timeout)
        return {
            "command": cmd,
            "available": True,
            "returncode": result.returncode,
            "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:],
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

def plist_status(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            plistlib.load(f)
        return {
            "path": str(path),
            "present": path.exists(),
            "parse_ok": True,
            "error": "",
        }
    except Exception as exc:
        return {
            "path": str(path),
            "present": path.exists(),
            "parse_ok": False,
            "error": str(exc),
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/compile-only-smoke")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    host_swift = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift"
    driver_cpp = root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Sources/H1mekaRTXDriver.cpp"

    commands = {}

    if shutil.which("xcrun"):
        commands["host_swift_typecheck"] = run_cmd([
            "xcrun",
            "swiftc",
            "-typecheck",
            str(host_swift),
        ])
        commands["driverkit_cpp_fsyntax_only"] = run_cmd([
            "xcrun",
            "--sdk",
            "driverkit",
            "clang++",
            "-fsyntax-only",
            "-std=c++17",
            str(driver_cpp),
        ])
    else:
        commands["host_swift_typecheck"] = {
            "command": ["xcrun", "swiftc", "-typecheck", str(host_swift)],
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "xcrun not found",
        }
        commands["driverkit_cpp_fsyntax_only"] = {
            "command": ["xcrun", "--sdk", "driverkit", "clang++", "-fsyntax-only", "-std=c++17", str(driver_cpp)],
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "xcrun not found",
        }

    plist_paths = [
        root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist",
        root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements",
        root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist",
        root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements",
    ]

    plist_results = {str(path.relative_to(root)): plist_status(path) for path in plist_paths}

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_COMPILE_ONLY_TARGET_SMOKE_TEST",
        "compile_only_evidence_only": True,
        "host_report_bundle_local_only": True,
        "build_artifact_created": False,
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
        "commands": commands,
        "plist_results": plist_results,
        "derived": {
            "host_swift_typecheck_ran": commands["host_swift_typecheck"]["available"],
            "host_swift_typecheck_returncode": commands["host_swift_typecheck"]["returncode"],
            "driverkit_cpp_fsyntax_only_ran": commands["driverkit_cpp_fsyntax_only"]["available"],
            "driverkit_cpp_fsyntax_only_returncode": commands["driverkit_cpp_fsyntax_only"]["returncode"],
            "plist_parse_all_ok": all(item["parse_ok"] for item in plist_results.values()),
            "compile_only_attempts_recorded": True,
            "compile_failures_allowed_at_preflight_stage": True,
        },
    }

    json_path = out_dir / "compile-only-target-smoke-test.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{key}` | `{value['available']}` | `{value['returncode']}` |"
        for key, value in commands.items()
    )
    plist_rows = "\n".join(
        f"| `{key}` | `{value['present']}` | `{value['parse_ok']}` |"
        for key, value in plist_results.items()
    )
    derived_text = json.dumps(report["derived"], indent=2, sort_keys=True)

    md = f"""# Compile-Only Target Smoke Test

- Generated At UTC: `{report['generated_at_utc']}`
- Compile Only Evidence Only: `True`
- Build Artifact Created: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Compile-Only Commands

| Key | Available | Return Code |
| --- | --- | --- |
{cmd_rows}

## Plist Parse Results

| Path | Present | Parse OK |
| --- | --- | --- |
{plist_rows}

## Derived Status

{derived_text}
"""
    md_path = out_dir / "compile-only-target-smoke-test.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_COMPILE_ONLY_TARGET_SMOKE_RECORDED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
