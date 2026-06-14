#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.dext_provider_status_local_report.v1"
EXT_ID = "dev.h1meka.H1mekaRTXDriver"

def run_cmd(cmd: list[str], timeout: int = 45) -> dict:
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

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="host-report-bundle/dext-provider-status")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    activation_report = read_json(root / "host-report-bundle/local-activation/actual-local-activation-hard-optin-report.json")

    commands = {}
    commands["systemextensionsctl_list"] = run_cmd(["systemextensionsctl", "list"]) if shutil.which("systemextensionsctl") else {
        "command": ["systemextensionsctl", "list"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "systemextensionsctl not found",
    }

    commands["ioreg_iopcidevice"] = run_cmd(["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"], timeout=60) if shutil.which("ioreg") else {
        "command": ["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "ioreg not found",
    }

    commands["ioreg_ioservice_h1meka"] = run_cmd(["ioreg", "-l", "-w0"], timeout=60) if shutil.which("ioreg") else {
        "command": ["ioreg", "-l", "-w0"],
        "available": False,
        "returncode": None,
        "stdout": "",
        "stderr": "ioreg not found",
    }

    sys_text = commands["systemextensionsctl_list"].get("stdout", "") + "\n" + commands["systemextensionsctl_list"].get("stderr", "")
    pci_text = commands["ioreg_iopcidevice"].get("stdout", "") + "\n" + commands["ioreg_iopcidevice"].get("stderr", "")
    service_text = commands["ioreg_ioservice_h1meka"].get("stdout", "") + "\n" + commands["ioreg_ioservice_h1meka"].get("stderr", "")

    derived = {
        "activation_report_present": activation_report is not None,
        "activation_command_completed": bool(activation_report and activation_report.get("decision") == "PASS_LOCAL_ACTIVATION_COMMAND_COMPLETED"),
        "activation_submitted_locally": bool(activation_report and activation_report.get("activation_submitted") is True),
        "systemextensionsctl_available": commands["systemextensionsctl_list"].get("available") is True,
        "systemextensionsctl_returncode": commands["systemextensionsctl_list"].get("returncode"),
        "extension_identifier_observed_in_systemextensionsctl": EXT_ID in sys_text,
        "status_contains_activated": "activated" in sys_text.lower(),
        "status_contains_enabled": "enabled" in sys_text.lower(),
        "status_contains_waiting_or_needs_user": any(token in sys_text.lower() for token in ["waiting", "needs user", "user approval", "awaiting"]),
        "ioreg_available": commands["ioreg_iopcidevice"].get("available") is True,
        "ioreg_iopcidevice_returncode": commands["ioreg_iopcidevice"].get("returncode"),
        "rtx_vendor_10de_observed": "0x10de" in pci_text.lower() or "10de" in pci_text.lower(),
        "rtx_device_2f04_observed": "0x2f04" in pci_text.lower() or "2f04" in pci_text.lower(),
        "rtx_iopcimatch_2f0410de_observed": "0x2f0410de" in pci_text.lower() or "2f0410de" in pci_text.lower(),
        "extension_identifier_observed_in_ioreg": EXT_ID in service_text,
        "provider_open_still_blocked": True,
        "ioserviceopen_still_blocked": True,
        "bar_mapping_still_blocked": True,
        "gpu_command_submission_still_blocked": True,
        "dock_transparency_blur_proof_still_blocked": True,
    }

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE",
        "host_report_bundle_local_only": True,
        "read_only_status_evidence_only": True,
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
        "extension_identifier": EXT_ID,
        "commands": commands,
        "derived": derived,
    }

    json_path = out_dir / "dext-provider-status-local-report.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{name}` | `{cmd.get('available')}` | `{cmd.get('returncode')}` | `{bool(cmd.get('stdout'))}` | `{bool(cmd.get('stderr'))}` |"
        for name, cmd in commands.items()
    )
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in derived.items())

    md = f"""# Dext Provider Status Local Report

- Generated At UTC: `{report['generated_at_utc']}`
- Host Report Bundle Local Only: `True`
- Read-Only Status Evidence Only: `True`
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
    md_path = out_dir / "dext-provider-status-local-report.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_DEXT_PROVIDER_STATUS_LOCAL_REPORT_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
