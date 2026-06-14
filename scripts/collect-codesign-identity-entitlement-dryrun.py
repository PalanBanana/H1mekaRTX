#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.codesign_identity_entitlement_dryrun_local_report.v1"

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
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

def load_plist(path: Path) -> dict:
    with path.open("rb") as f:
        return plistlib.load(f)

def safe_plist(path: Path) -> dict:
    try:
        obj = load_plist(path)
        return {
            "present": path.exists(),
            "parse_ok": True,
            "keys": sorted(obj.keys()),
            "value": obj,
            "error": "",
        }
    except Exception as exc:
        return {
            "present": path.exists(),
            "parse_ok": False,
            "keys": [],
            "value": {},
            "error": str(exc),
        }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/codesign-entitlement-dryrun")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    commands = {}
    if shutil.which("security"):
        commands["security_find_identity_codesigning"] = run_cmd(["security", "find-identity", "-v", "-p", "codesigning"])
    else:
        commands["security_find_identity_codesigning"] = {
            "command": ["security", "find-identity", "-v", "-p", "codesigning"],
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "security not found",
        }

    if shutil.which("codesign"):
        commands["codesign_help_probe"] = run_cmd(["codesign", "--help"])
    else:
        commands["codesign_help_probe"] = {
            "command": ["codesign", "--help"],
            "available": False,
            "returncode": None,
            "stdout": "",
            "stderr": "codesign not found",
        }

    host_info = safe_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist")
    dext_info = safe_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist")
    host_ent = safe_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements")
    dext_ent = safe_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements")

    security_stdout = commands["security_find_identity_codesigning"].get("stdout", "")
    identity_lines = [
        line.strip()
        for line in security_stdout.splitlines()
        if line.strip() and ")" in line and '"' in line
    ]

    derived = {
        "security_available": commands["security_find_identity_codesigning"]["available"],
        "security_find_identity_returncode": commands["security_find_identity_codesigning"]["returncode"],
        "codesign_available": commands["codesign_help_probe"]["available"],
        "codesign_help_returncode": commands["codesign_help_probe"]["returncode"],
        "codesigning_identity_line_count": len(identity_lines),
        "codesigning_identity_detected": len(identity_lines) > 0,
        "host_info_parse_ok": host_info["parse_ok"],
        "dext_info_parse_ok": dext_info["parse_ok"],
        "host_entitlements_parse_ok": host_ent["parse_ok"],
        "dext_entitlements_parse_ok": dext_ent["parse_ok"],
        "host_bundle_id_matches": host_info["value"].get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost",
        "dext_bundle_id_matches": dext_info["value"].get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver",
        "host_system_extension_entitlement_present": host_ent["value"].get("com.apple.developer.system-extension.install") is True,
        "dext_driverkit_entitlement_present": dext_ent["value"].get("com.apple.developer.driverkit") is True,
        "dext_pci_transport_entitlement_present": "com.apple.developer.driverkit.transport.pci" in dext_ent["value"],
    }

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_EVIDENCE",
        "local_evidence_only": True,
        "host_report_bundle_local_only": True,
        "codesign_identity_discovery_attempted": True,
        "codesign_signing_attempted": False,
        "signed_package_created": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
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
        "plist_status": {
            "host_info": host_info,
            "dext_info": dext_info,
            "host_entitlements": host_ent,
            "dext_entitlements": dext_ent,
        },
        "derived": derived,
    }

    json_path = out_dir / "codesign-identity-entitlement-dryrun.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{key}` | `{value['available']}` | `{value['returncode']}` | `{bool(value.get('stdout'))}` | `{bool(value.get('stderr'))}` |"
        for key, value in commands.items()
    )
    derived_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in derived.items())

    md = f"""# Codesign Identity + Entitlement Dry-Run Local Evidence

- Generated At UTC: `{report['generated_at_utc']}`
- Local Evidence Only: `True`
- Host Report Bundle Local Only: `True`
- Codesign Identity Discovery Attempted: `True`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Commands

| Command Key | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- |
{cmd_rows}

## Derived Summary

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "codesign-identity-entitlement-dryrun.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_RECORDED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
