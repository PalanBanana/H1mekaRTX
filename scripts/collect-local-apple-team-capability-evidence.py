#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_apple_team_capability_evidence_report.v1"

def run_cmd(cmd: list[str], timeout: int = 120) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "returncode": p.returncode,
            "stdout": p.stdout[-60000:] if p.stdout else "",
            "stderr": p.stderr[-60000:] if p.stderr else "",
        }
    except Exception as exc:
        return {
            "command": cmd,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }

def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        obj, _ = json.JSONDecoder().raw_decode(text.lstrip())
        return obj if isinstance(obj, dict) else None

def contains(text: str, needle: str) -> bool:
    return needle.lower() in str(text or "").lower()

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def base_report() -> dict:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE",
        "host_report_bundle_local_only": True,
        "xcodebuild_build_attempted_by_this_phase": False,
        "activation_submitted_by_this_phase": False,
        "deactivation_submitted_by_this_phase": False,
        "install_attempted": False,
        "manual_dext_load_attempted": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_proof_claimed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/local-apple-team-capability-evidence")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}

    commands["xcodebuild_version"] = run_cmd(["xcodebuild", "-version"]) if shutil.which("xcodebuild") else {
        "command": ["xcodebuild", "-version"],
        "returncode": None,
        "stdout": "",
        "stderr": "xcodebuild not found",
    }

    commands["driverkit_sdk_path"] = run_cmd(["xcrun", "--sdk", "driverkit", "--show-sdk-path"]) if shutil.which("xcrun") else {
        "command": ["xcrun", "--sdk", "driverkit", "--show-sdk-path"],
        "returncode": None,
        "stdout": "",
        "stderr": "xcrun not found",
    }

    commands["macosx_sdk_path"] = run_cmd(["xcrun", "--sdk", "macosx", "--show-sdk-path"]) if shutil.which("xcrun") else {
        "command": ["xcrun", "--sdk", "macosx", "--show-sdk-path"],
        "returncode": None,
        "stdout": "",
        "stderr": "xcrun not found",
    }

    commands["codesigning_identities"] = run_cmd(["security", "find-identity", "-v", "-p", "codesigning"]) if shutil.which("security") else {
        "command": ["security", "find-identity", "-v", "-p", "codesigning"],
        "returncode": None,
        "stdout": "",
        "stderr": "security not found",
    }

    project = root / "apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj"
    if project.exists():
        commands["xcodebuild_list_project"] = run_cmd([
            "xcodebuild", "-list", "-project", str(project)
        ])

        commands["xcodebuild_show_build_settings"] = run_cmd([
            "xcodebuild",
            "-showBuildSettings",
            "-project", str(project),
            "-scheme", "H1mekaRTXHost",
            "-configuration", "Debug",
        ])

    build_log = read_text(root / "host-report-bundle/real-driverkit-build/xcodebuild-allow-provisioning.log")
    build_report = read_json(root / "host-report-bundle/real-driverkit-build/real-driverkit-dext-build-gate-report.json")
    hardblock_check = read_json(root / "release-readiness/provisioning-entitlement-hardblock-gate-check.json")
    checklist_check = read_json(root / "release-readiness/apple-developer-entitlement-request-checklist-check.json")

    combined = "\n".join([
        build_log,
        json.dumps(build_report or {}),
        json.dumps(hardblock_check or {}),
        json.dumps(checklist_check or {}),
        commands["xcodebuild_version"].get("stdout", ""),
        commands["xcodebuild_version"].get("stderr", ""),
        commands["driverkit_sdk_path"].get("stdout", ""),
        commands["driverkit_sdk_path"].get("stderr", ""),
        commands["macosx_sdk_path"].get("stdout", ""),
        commands["macosx_sdk_path"].get("stderr", ""),
        commands["codesigning_identities"].get("stdout", ""),
        commands["codesigning_identities"].get("stderr", ""),
        commands.get("xcodebuild_list_project", {}).get("stdout", ""),
        commands.get("xcodebuild_list_project", {}).get("stderr", ""),
        commands.get("xcodebuild_show_build_settings", {}).get("stdout", ""),
        commands.get("xcodebuild_show_build_settings", {}).get("stderr", ""),
    ])

    personal_team_blocker = contains(combined, "Personal development teams") or contains(combined, "personal team")
    system_extension_capability_blocker = contains(combined, "do not support the System Extension capability")
    driverkit_enable_blocker = contains(combined, "Please enable Driverkit") or contains(combined, "DriverKit profile")
    host_profile_missing = contains(combined, "No profiles for 'dev.h1meka.H1mekaRTXHost'")
    dext_profile_missing = contains(combined, "No profiles for 'dev.h1meka.H1mekaRTXDriver'")
    apple_dev_identity_present = contains(commands["codesigning_identities"].get("stdout", ""), "Apple Development:")
    paid_team_proven = False
    driverkit_entitlement_approval_proven = False
    pci_transport_entitlement_approval_proven = False
    system_extension_capability_proven = False

    report = {
        **base_report(),
        "decision": "PASS_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE_CAPTURED",
        "xcode_present": commands["xcodebuild_version"].get("returncode") == 0,
        "driverkit_sdk_present": commands["driverkit_sdk_path"].get("returncode") == 0,
        "macosx_sdk_present": commands["macosx_sdk_path"].get("returncode") == 0,
        "apple_development_identity_present": apple_dev_identity_present,
        "xcode_project_present": project.exists(),
        "phase60q_hardblock_check_present": hardblock_check is not None,
        "phase60r_checklist_check_present": checklist_check is not None,
        "previous_build_log_present": bool(build_log),
        "personal_team_blocker_observed": personal_team_blocker,
        "system_extension_capability_blocker_observed": system_extension_capability_blocker,
        "driverkit_enable_blocker_observed": driverkit_enable_blocker,
        "host_profile_missing_observed": host_profile_missing,
        "dext_profile_missing_observed": dext_profile_missing,
        "paid_team_proven": paid_team_proven,
        "driverkit_entitlement_approval_proven": driverkit_entitlement_approval_proven,
        "pci_transport_entitlement_approval_proven": pci_transport_entitlement_approval_proven,
        "system_extension_capability_proven": system_extension_capability_proven,
        "phase61_allowed_now": False,
        "provider_open_allowed_now": False,
        "next_gate": "wait_for_paid_team_and_apple_entitlement_approval",
        "commands": commands,
    }

    write_json(out_dir / "local-apple-team-capability-evidence-report.json", report)
    print("Decision: PASS_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE_CAPTURED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
