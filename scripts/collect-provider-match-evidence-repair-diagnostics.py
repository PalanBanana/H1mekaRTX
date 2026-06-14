#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.provider_match_evidence_repair_local_report.v1"

EXT_ID = "dev.h1meka.H1mekaRTXDriver"
HOST_ID = "dev.h1meka.H1mekaRTXHost"
VENDOR_ID = "0x10de"
DEVICE_ID = "0x2f04"
IOPCIMATCH = "0x2f0410de"
PROVIDER_CLASS = "IOPCIDevice"

def run_cmd(cmd: list[str], timeout: int = 60) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, check=False, timeout=timeout)
        return {
            "command": cmd,
            "available": True,
            "returncode": p.returncode,
            "stdout": p.stdout or "",
            "stderr": p.stderr or "",
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

def read_plist(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            return plistlib.load(f)
    except Exception:
        return {}

def nested_get(obj: dict, keys: list[str]):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur

def collect_personalities(info: dict) -> dict:
    personalities = info.get("IOKitPersonalities") or info.get("IOKitPersonalities".lower()) or {}
    if not isinstance(personalities, dict):
        return {}
    out = {}
    for name, item in personalities.items():
        if isinstance(item, dict):
            out[name] = {
                "IOProviderClass": item.get("IOProviderClass"),
                "IOPCIMatch": item.get("IOPCIMatch"),
                "CFBundleIdentifier": item.get("CFBundleIdentifier"),
                "IOClass": item.get("IOClass"),
                "IOUserClass": item.get("IOUserClass"),
            }
    return out

def contains_any(text: str, needles: list[str]) -> bool:
    lowered = text.lower()
    return any(n.lower() in lowered for n in needles)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/provider-match-evidence-repair")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    app = root / "host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app"
    dext = app / "Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext"

    commands = {}

    commands["systemextensionsctl_list"] = run_cmd(["systemextensionsctl", "list"]) if shutil.which("systemextensionsctl") else {
        "command": ["systemextensionsctl", "list"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "systemextensionsctl not found",
    }

    commands["ioreg_iopcidevice"] = run_cmd(["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"], timeout=90) if shutil.which("ioreg") else {
        "command": ["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "ioreg not found",
    }

    commands["ioreg_h1meka_filtered"] = run_cmd(["ioreg", "-l", "-w0"], timeout=90) if shutil.which("ioreg") else {
        "command": ["ioreg", "-l", "-w0"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "ioreg not found",
    }

    commands["system_profiler_displays"] = run_cmd(["system_profiler", "SPDisplaysDataType", "-json"], timeout=90) if shutil.which("system_profiler") else {
        "command": ["system_profiler", "SPDisplaysDataType", "-json"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "system_profiler not found",
    }

    commands["codesign_display_host"] = run_cmd(["codesign", "-dv", str(app)], timeout=45) if shutil.which("codesign") and app.exists() else {
        "command": ["codesign", "-dv", str(app)],
        "available": bool(shutil.which("codesign")),
        "returncode": None,
        "stdout": "",
        "stderr": "host app missing or codesign not found",
    }

    commands["codesign_display_dext"] = run_cmd(["codesign", "-dv", str(dext)], timeout=45) if shutil.which("codesign") and dext.exists() else {
        "command": ["codesign", "-dv", str(dext)],
        "available": bool(shutil.which("codesign")),
        "returncode": None,
        "stdout": "",
        "stderr": "dext missing or codesign not found",
    }

    host_info = read_plist(app / "Contents/Info.plist")
    dext_info = read_plist(dext / "Contents/Info.plist")
    dext_personalities = collect_personalities(dext_info)

    sys_text = commands["systemextensionsctl_list"].get("stdout", "") + "\n" + commands["systemextensionsctl_list"].get("stderr", "")
    pci_text = commands["ioreg_iopcidevice"].get("stdout", "") + "\n" + commands["ioreg_iopcidevice"].get("stderr", "")
    service_text = commands["ioreg_h1meka_filtered"].get("stdout", "") + "\n" + commands["ioreg_h1meka_filtered"].get("stderr", "")
    display_text = commands["system_profiler_displays"].get("stdout", "") + "\n" + commands["system_profiler_displays"].get("stderr", "")

    systemextension_tokens = []
    sys_lower = sys_text.lower()
    if EXT_ID.lower() in sys_lower:
        systemextension_tokens.append("extension_identifier_observed")
    if "activated" in sys_lower:
        systemextension_tokens.append("activated")
    if "enabled" in sys_lower:
        systemextension_tokens.append("enabled")
    if any(t in sys_lower for t in ["waiting", "needs user", "user approval", "awaiting"]):
        systemextension_tokens.append("needs_user_approval")
    if "terminated" in sys_lower:
        systemextension_tokens.append("terminated")

    personality_values = json.dumps(dext_personalities, sort_keys=True).lower()

    derived = {
        "host_bundle_exists": app.exists(),
        "dext_bundle_exists": dext.exists(),
        "host_info_parse_ok": bool(host_info),
        "dext_info_parse_ok": bool(dext_info),
        "host_bundle_id_matches": host_info.get("CFBundleIdentifier") == HOST_ID,
        "dext_bundle_id_matches": dext_info.get("CFBundleIdentifier") == EXT_ID,
        "dext_personalities_present": bool(dext_personalities),
        "dext_personality_provider_class_matches": PROVIDER_CLASS.lower() in personality_values,
        "dext_personality_iopcimatch_matches": IOPCIMATCH.lower() in personality_values,
        "systemextensionsctl_available": commands["systemextensionsctl_list"].get("available") is True,
        "systemextensionsctl_returncode": commands["systemextensionsctl_list"].get("returncode"),
        "extension_identifier_observed_in_systemextensionsctl": EXT_ID.lower() in sys_lower,
        "systemextension_status_tokens": sorted(set(systemextension_tokens)),
        "ioreg_available": commands["ioreg_iopcidevice"].get("available") is True,
        "ioreg_iopcidevice_returncode": commands["ioreg_iopcidevice"].get("returncode"),
        "rtx_vendor_10de_observed_in_ioreg": contains_any(pci_text, ["0x10de", "10de"]),
        "rtx_device_2f04_observed_in_ioreg": contains_any(pci_text, ["0x2f04", "2f04"]),
        "rtx_iopcimatch_2f0410de_observed_in_ioreg": contains_any(pci_text, ["0x2f0410de", "2f0410de"]),
        "extension_identifier_observed_in_ioreg": EXT_ID.lower() in service_text.lower(),
        "h1meka_string_observed_in_ioreg": "h1mekartx" in service_text.lower(),
        "nvidia_string_observed_in_ioreg": "nvidia" in pci_text.lower(),
        "display_profiler_nvidia_observed": "nvidia" in display_text.lower(),
        "display_profiler_rtx_observed": "rtx" in display_text.lower(),
        "provider_match_blocked_reason_hint": [],
        "provider_open_still_blocked": True,
        "ioserviceopen_still_blocked": True,
        "bar_mapping_still_blocked": True,
        "gpu_command_submission_still_blocked": True,
        "dock_transparency_blur_proof_still_blocked": True,
    }

    if not derived["extension_identifier_observed_in_systemextensionsctl"]:
        derived["provider_match_blocked_reason_hint"].append("extension_identifier_not_observed_in_systemextensionsctl")
    if not derived["rtx_vendor_10de_observed_in_ioreg"]:
        derived["provider_match_blocked_reason_hint"].append("rtx_vendor_10de_not_observed_in_ioreg")
    if not derived["rtx_device_2f04_observed_in_ioreg"]:
        derived["provider_match_blocked_reason_hint"].append("rtx_device_2f04_not_observed_in_ioreg")
    if not derived["dext_personality_iopcimatch_matches"]:
        derived["provider_match_blocked_reason_hint"].append("dext_iopcimatch_personality_mismatch")
    if not derived["dext_personality_provider_class_matches"]:
        derived["provider_match_blocked_reason_hint"].append("dext_ioproviderclass_personality_mismatch")

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS",
        "read_only_diagnostics_only": True,
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
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "commands": commands,
        "bundle_parse": {
            "host_info_keys": sorted(host_info.keys()) if host_info else [],
            "dext_info_keys": sorted(dext_info.keys()) if dext_info else [],
            "dext_personalities": dext_personalities,
        },
        "derived": derived,
    }

    json_path = out_dir / "provider-match-evidence-repair-local-report.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{name}` | `{cmd.get('available')}` | `{cmd.get('returncode')}` | `{bool(cmd.get('stdout'))}` | `{bool(cmd.get('stderr'))}` |"
        for name, cmd in commands.items()
    )
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in derived.items())

    md = f"""# Provider Match Evidence Repair Local Report

- Generated At UTC: `{report['generated_at_utc']}`
- Read-Only Diagnostics Only: `True`
- Host Report Bundle Local Only: `True`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
- Install Attempted: `False`
- Manual Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Commands

| Command | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- |
{rows}

## Derived

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "provider-match-evidence-repair-local-report.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_PROVIDER_MATCH_EVIDENCE_REPAIR_LOCAL_REPORT_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
