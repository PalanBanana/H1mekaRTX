#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.real_driverkit_dext_build_gate_report.v1"

def run_cmd(cmd: list[str], timeout: int = 1200) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-60000:] if p.stdout else "",
            "stderr": p.stderr[-60000:] if p.stderr else "",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": exc.stdout or "",
            "stderr": (exc.stderr or "") + "\nTIMEOUT",
        }

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_REAL_DRIVERKIT_DEXT_BUILD_GATE",
        "host_report_bundle_local_only": True,
        "activation_submitted_by_this_phase": False,
        "deactivation_submitted_by_this_phase": False,
        "install_attempted": False,
        "manual_dext_load_attempted": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "firmware_load_attempted": False,
        "gpu_reset_attempted": False,
        "framebuffer_init_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_proof_claimed": False,
    }

def find_dexts(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(p for p in base.rglob("*.dext") if p.is_dir())

def read_plist_identifier(plist_path: Path) -> str:
    if not plist_path.exists():
        return ""
    try:
        import plistlib
        with plist_path.open("rb") as f:
            data = plistlib.load(f)
        return str(data.get("CFBundleIdentifier", ""))
    except Exception:
        return ""

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--i-understand-local-driverkit-build", action="store_true")
    parser.add_argument("--output-under-host-report-bundle", action="store_true")
    parser.add_argument("--project", default="")
    parser.add_argument("--workspace", default="")
    parser.add_argument("--scheme", default="")
    parser.add_argument("--configuration", default="Debug")
    parser.add_argument("--derived-data-path", default="host-report-bundle/real-driverkit-build/DerivedData")
    parser.add_argument("--out-dir", default="host-report-bundle/real-driverkit-build")
    parser.add_argument("--expected-dext-id", default="dev.h1meka.H1mekaRTXDriver")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "real-driverkit-dext-build-gate-report.json"

    project = Path(args.project).resolve() if args.project else None
    workspace = Path(args.workspace).resolve() if args.workspace else None
    derived = (root / args.derived_data_path).resolve()

    hard_optin_ok = bool(
        args.i_understand_local_driverkit_build
        and args.output_under_host_report_bundle
        and args.scheme.strip()
        and ((project and project.exists()) or (workspace and workspace.exists()))
    )
    local_output_scope_ok = str(out_dir).startswith(str((root / "host-report-bundle").resolve()) + os.sep)
    derived_scope_ok = str(derived).startswith(str((root / "host-report-bundle").resolve()) + os.sep)

    if not hard_optin_ok or not local_output_scope_ok or not derived_scope_ok:
        report = {
            **base_report(),
            "decision": "REFUSE_REAL_DRIVERKIT_BUILD_HARDOPTIN_OR_INPUT_NOT_SATISFIED",
            "hard_optin_ok": hard_optin_ok,
            "local_output_scope_ok": local_output_scope_ok,
            "derived_scope_ok": derived_scope_ok,
            "xcodebuild_attempted": False,
            "real_driverkit_dext_built": False,
            "block_reasons": [
                reason for reason, ok in [
                    ("missing_hard_optin_flag", args.i_understand_local_driverkit_build),
                    ("missing_output_under_host_report_bundle_flag", args.output_under_host_report_bundle),
                    ("missing_scheme", bool(args.scheme.strip())),
                    ("missing_existing_project_or_workspace", bool((project and project.exists()) or (workspace and workspace.exists()))),
                    ("output_not_under_host_report_bundle", local_output_scope_ok),
                    ("derived_data_not_under_host_report_bundle", derived_scope_ok),
                ] if not ok
            ],
        }
        write_json(report_path, report)
        print("Decision: REFUSE_REAL_DRIVERKIT_BUILD_HARDOPTIN_OR_INPUT_NOT_SATISFIED")
        return 2

    commands = {}
    if shutil.which("xcodebuild"):
        commands["xcodebuild_version"] = run_cmd(["xcodebuild", "-version"], timeout=60)
    else:
        commands["xcodebuild_version"] = {"command": ["xcodebuild", "-version"], "returncode": None, "stdout": "", "stderr": "xcodebuild not found"}

    commands["driverkit_sdk_path"] = run_cmd(["xcrun", "--sdk", "driverkit", "--show-sdk-path"], timeout=60)
    commands["macosx_sdk_path"] = run_cmd(["xcrun", "--sdk", "macosx", "--show-sdk-path"], timeout=60)

    build_cmd = [
        "xcodebuild",
        "build",
        "-scheme", args.scheme,
        "-configuration", args.configuration,
        "-derivedDataPath", str(derived),
    ]
    if project:
        build_cmd += ["-project", str(project)]
    if workspace:
        build_cmd += ["-workspace", str(workspace)]

    commands["xcodebuild_build"] = run_cmd(build_cmd, timeout=1800)

    dexts = find_dexts(derived)
    matching_dexts = []
    for dext in dexts:
        ident = read_plist_identifier(dext / "Contents/Info.plist")
        if ident == args.expected_dext_id:
            matching_dexts.append(dext)

    selected_dext = matching_dexts[0] if matching_dexts else (dexts[0] if dexts else None)

    dext_exec = None
    if selected_dext:
        exec_dir = selected_dext / "Contents/MacOS"
        if exec_dir.exists():
            candidates = [p for p in exec_dir.iterdir() if p.is_file()]
            dext_exec = candidates[0] if candidates else None

    if selected_dext:
        commands["codesign_verify_selected_dext"] = run_cmd(["codesign", "--verify", "--strict", "--verbose=4", str(selected_dext)], timeout=120)
        commands["codesign_display_selected_dext"] = run_cmd(["codesign", "-dvvv", "--entitlements", ":-", str(selected_dext)], timeout=120)

    if dext_exec:
        commands["file_selected_dext_exec"] = run_cmd(["file", str(dext_exec)], timeout=60)

    build_ok = commands["xcodebuild_build"].get("returncode") == 0
    selected_dext_exists = bool(selected_dext and selected_dext.exists())
    selected_exec_exists = bool(dext_exec and dext_exec.exists())
    selected_identifier_matches = bool(selected_dext and read_plist_identifier(selected_dext / "Contents/Info.plist") == args.expected_dext_id)

    codesign_ok = commands.get("codesign_verify_selected_dext", {}).get("returncode") == 0
    file_text = commands.get("file_selected_dext_exec", {}).get("stdout", "") + commands.get("file_selected_dext_exec", {}).get("stderr", "")
    macho_observed = "Mach-O" in file_text

    display_text = commands.get("codesign_display_selected_dext", {}).get("stdout", "") + commands.get("codesign_display_selected_dext", {}).get("stderr", "")
    driverkit_entitlement_present = "com.apple.developer.driverkit" in display_text
    pci_entitlement_present = "com.apple.developer.driverkit.transport.pci" in display_text

    real_driverkit_dext_built = bool(
        build_ok
        and selected_dext_exists
        and selected_exec_exists
        and selected_identifier_matches
        and codesign_ok
        and macho_observed
        and driverkit_entitlement_present
    )

    if real_driverkit_dext_built:
        decision = "PASS_REAL_DRIVERKIT_DEXT_BUILD_PROVEN"
    elif build_ok and selected_dext_exists:
        decision = "PASS_XCODE_BUILD_COMPLETED_BUT_DRIVERKIT_DEXT_NOT_FULLY_PROVEN"
    else:
        decision = "PASS_REAL_DRIVERKIT_BUILD_ATTEMPTED_NOT_PROVEN"

    report = {
        **base_report(),
        "decision": decision,
        "hard_optin_ok": hard_optin_ok,
        "local_output_scope_ok": local_output_scope_ok,
        "derived_scope_ok": derived_scope_ok,
        "xcodebuild_attempted": True,
        "xcodebuild_build_ok": build_ok,
        "project": str(project) if project else "",
        "workspace": str(workspace) if workspace else "",
        "scheme": args.scheme,
        "configuration": args.configuration,
        "derived_data_path": str(derived),
        "expected_dext_id": args.expected_dext_id,
        "discovered_dext_count": len(dexts),
        "matching_dext_count": len(matching_dexts),
        "selected_dext_present": selected_dext_exists,
        "selected_dext_identifier_matches": selected_identifier_matches,
        "selected_dext_exec_present": selected_exec_exists,
        "selected_dext_codesign_ok": codesign_ok,
        "selected_dext_exec_macho_observed": macho_observed,
        "driverkit_entitlement_present": driverkit_entitlement_present,
        "pci_transport_entitlement_present": pci_entitlement_present,
        "real_driverkit_dext_built": real_driverkit_dext_built,
        "provider_open_allowed_now": False,
        "bar_mapping_allowed_now": False,
        "gpu_command_submission_allowed_now": False,
        "commands": commands,
    }

    write_json(report_path, report)
    print("Decision:", decision)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
