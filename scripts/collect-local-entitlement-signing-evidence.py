#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_entitlement_signing_evidence.v1"

SAFE_COMMANDS = {
    "xcode_select_path": ["xcode-select", "-p"],
    "xcodebuild_version": ["xcodebuild", "-version"],
    "codesigning_identities": ["security", "find-identity", "-v", "-p", "codesigning"],
    "systemextensionsctl_list": ["systemextensionsctl", "list"],
    "sw_vers": ["sw_vers"],
    "uname": ["uname", "-a"],
}

def run_cmd(cmd: list[str], timeout: int = 20) -> dict:
    try:
        completed = subprocess.run(
            cmd,
            check=False,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": cmd,
            "available": True,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-12000:],
            "stderr": completed.stderr[-4000:],
        }
    except FileNotFoundError:
        return {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except subprocess.TimeoutExpired as exc:
        return {
            "command": cmd,
            "available": True,
            "returncode": None,
            "stdout": (exc.stdout or "")[-12000:] if isinstance(exc.stdout, str) else "",
            "stderr": "timeout",
        }

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Collect local entitlement/signing evidence without build/sign/activation.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="host-report-bundle/local-entitlement-signing-evidence", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    ledger_path = root / "tools" / "driverkit-activation" / "activation-prerequisites-ledger.json"
    ledger = read_json(ledger_path)

    commands = {}
    for name, cmd in SAFE_COMMANDS.items():
        if shutil.which(cmd[0]) is None:
            commands[name] = {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
        else:
            commands[name] = run_cmd(cmd)

    identities_stdout = commands.get("codesigning_identities", {}).get("stdout", "")
    has_codesigning_identity = "valid identities found" in identities_stdout.lower() and not identities_stdout.strip().endswith("0 valid identities found")

    xcode_available = commands.get("xcode_select_path", {}).get("returncode") == 0 and commands.get("xcodebuild_version", {}).get("returncode") == 0

    evidence = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE",
        "secondary_classification": "CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "local_evidence_collector_only": True,
        "read_only_status_collection_only": True,
        "build_attempted": False,
        "signing_attempted": False,
        "install_attempted": False,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "safe_commands": commands,
        "derived_status": {
            "xcode_available": bool(xcode_available),
            "codesigning_identity_detected": bool(has_codesigning_identity),
            "activation_ledger_loaded": ledger is not None,
            "activation_gate_state": ledger.get("activation_gate_state") if ledger else "UNKNOWN",
            "entitlement_approval_claimed": False,
            "signing_readiness_claimed": False,
            "activation_ready_claimed": False,
        },
        "target_pci_provider_matching_manifest": {
            "target_gpu": "NVIDIA RTX 5070",
            "architecture_family": "NVIDIA Blackwell",
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "io_pci_match": "0x2f0410de",
            "expected_provider_class": "IOPCIDevice",
            "expected_driver_family": "PCIDriverKit",
            "expected_pci_transport_entitlement": "com.apple.developer.driverkit.transport.pci",
            "expected_system_extension_entitlement": "com.apple.developer.system-extension.install",
        },
    }

    json_path = out_dir / "local-entitlement-signing-evidence.json"
    json_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{name}` | `{result.get('available')}` | `{result.get('returncode')}` |"
        for name, result in commands.items()
    )

    md = f"""# Local Entitlement / Signing Evidence

- Generated At UTC: `{evidence['generated_at_utc']}`
- Classification: `{evidence['classification']}`
- Read-Only Status Collection Only: `{evidence['read_only_status_collection_only']}`
- Build Attempted: `{evidence['build_attempted']}`
- Signing Attempted: `{evidence['signing_attempted']}`
- Install Attempted: `{evidence['install_attempted']}`
- DriverKit Activation Attempted: `{evidence['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{evidence['system_extension_activation_attempted']}`
- Dext Load Attempted: `{evidence['dext_load_attempted']}`
- Provider Open Attempted: `{evidence['provider_open_attempted']}`
- BAR Mapping Attempted: `{evidence['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{evidence['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{evidence['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{evidence['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{evidence['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{evidence['metal_proof_claimed']}`

## Derived Status

| Field | Value |
| --- | --- |
| xcode_available | `{evidence['derived_status']['xcode_available']}` |
| codesigning_identity_detected | `{evidence['derived_status']['codesigning_identity_detected']}` |
| activation_ledger_loaded | `{evidence['derived_status']['activation_ledger_loaded']}` |
| activation_gate_state | `{evidence['derived_status']['activation_gate_state']}` |
| entitlement_approval_claimed | `{evidence['derived_status']['entitlement_approval_claimed']}` |
| signing_readiness_claimed | `{evidence['derived_status']['signing_readiness_claimed']}` |
| activation_ready_claimed | `{evidence['derived_status']['activation_ready_claimed']}` |

## Safe Commands

| Name | Available | Return Code |
| --- | --- | --- |
{command_rows}

## Conclusion

This collector records local status only. It does not build, sign, install, activate DriverKit/System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "local-entitlement-signing-evidence.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_COLLECTED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
