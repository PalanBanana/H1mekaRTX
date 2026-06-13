#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.provider_match_candidate_report.v1"

TARGET_VENDOR = "0x10de"
TARGET_DEVICE = "0x2f04"
TARGET_IOPCIMATCH = "0x2f0410de"

SAFE_COMMANDS = {
    "ioreg_iopcidevice": ["ioreg", "-r", "-c", "IOPCIDevice", "-l", "-w0"],
    "system_profiler_pci": ["system_profiler", "SPPCIDataType"],
    "sw_vers": ["sw_vers"],
    "uname": ["uname", "-a"],
}

def run_cmd(cmd: list[str], timeout: int = 30) -> dict:
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
            "stdout": completed.stdout[-30000:],
            "stderr": completed.stderr[-8000:],
        }
    except FileNotFoundError:
        return {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "command": cmd,
            "available": True,
            "returncode": None,
            "stdout": stdout[-30000:],
            "stderr": (stderr[-8000:] + "\ntimeout").strip(),
        }

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def find_candidate_hints(text: str) -> dict:
    lower = text.lower()
    vendor_hits = lower.count("0x10de") + lower.count("10de")
    device_hits = lower.count("0x2f04") + lower.count("2f04")
    iopci_hits = lower.count("0x2f0410de") + lower.count("2f0410de")

    # Keep only short redacted snippets around exact target markers.
    snippets = []
    for pattern in ["0x10de", "10de", "0x2f04", "2f04", "0x2f0410de", "2f0410de", "nvidia"]:
        for m in re.finditer(re.escape(pattern), lower):
            start = max(0, m.start() - 120)
            end = min(len(text), m.end() + 120)
            snippet = " ".join(text[start:end].split())
            if snippet and snippet not in snippets:
                snippets.append(snippet[:300])
            if len(snippets) >= 12:
                break
        if len(snippets) >= 12:
            break

    return {
        "vendor_marker_hits": vendor_hits,
        "device_marker_hits": device_hits,
        "iopci_match_marker_hits": iopci_hits,
        "nvidia_marker_present": "nvidia" in lower,
        "target_candidate_marker_present": bool(
            ("10de" in lower or "0x10de" in lower)
            and ("2f04" in lower or "0x2f04" in lower or "2f0410de" in lower)
        ),
        "redacted_candidate_snippets": snippets,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Collect read-only provider match candidate evidence.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="host-report-bundle/provider-match-candidate", help="Local output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    proof_schema = read_json(root / "tools" / "driverkit-activation" / "dext-load-provider-match-proof-schema.json")
    gate = read_json(root / "tools" / "driverkit-activation" / "activation-execution-gate.json")
    hardblock = read_json(root / "tools" / "driverkit-activation" / "ledger-override-hardblock-audit.json")

    commands = {}
    for name, cmd in SAFE_COMMANDS.items():
        if shutil.which(cmd[0]) is None:
            commands[name] = {"command": cmd, "available": False, "returncode": None, "stdout": "", "stderr": "command not found"}
        else:
            commands[name] = run_cmd(cmd)

    ioreg_text = commands.get("ioreg_iopcidevice", {}).get("stdout", "")
    profiler_text = commands.get("system_profiler_pci", {}).get("stdout", "")
    combined_text = ioreg_text + "\n" + profiler_text
    hints = find_candidate_hints(combined_text)

    candidate_state = "CANDIDATE_OBSERVED" if hints["target_candidate_marker_present"] else "NO_TARGET_CANDIDATE_OBSERVED"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_COLLECTOR",
        "secondary_classification": "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "provider_match_candidate_collector_only": True,
        "read_only_provider_candidate_collection_only": True,
        "candidate_report_only": True,
        "provider_match_proof_not_claimed": True,
        "execute_mode_still_blocked": True,
        "ledger_ready_required_for_execute": True,
        "activation_execution_gate_decision": gate.get("activation_execution_gate_decision") if gate else "UNKNOWN",
        "proof_schema_loaded": proof_schema is not None,
        "hardblock_loaded": hardblock is not None,
        "provider_match_candidate_state": candidate_state,
        "provider_match_proof_state": "NOT_ATTEMPTED",
        "dext_load_proof_state": "NOT_ATTEMPTED",
        "real_gpu_command_execution_proof_state": "NOT_ATTEMPTED",
        "ui_compositor_proof_state": "NOT_ATTEMPTED",
        "metal_proof_state": "NOT_ATTEMPTED",
        "real_activation_not_attempted": True,
        "real_deactivation_not_attempted": True,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
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
        "target_pci_provider_matching_manifest": {
            "target_gpu": "NVIDIA RTX 5070",
            "architecture_family": "NVIDIA Blackwell",
            "vendor_id": TARGET_VENDOR,
            "device_id": TARGET_DEVICE,
            "io_pci_match": TARGET_IOPCIMATCH,
            "expected_provider_class": "IOPCIDevice",
            "expected_driver_family": "PCIDriverKit",
            "expected_pci_transport_entitlement": "com.apple.developer.driverkit.transport.pci",
            "expected_system_extension_entitlement": "com.apple.developer.system-extension.install",
            "expected_dext_bundle_id": "dev.h1meka.H1mekaRTXDriver",
            "expected_host_bundle_id": "dev.h1meka.H1mekaRTXHost",
        },
        "candidate_hints": hints,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "safe_read_only_commands": commands,
        "dock_transparency_blur_state": "BLOCKED_UNTIL_REAL_GPU_COMMAND_AND_COMPOSITOR_ATTRIBUTION_EVIDENCE",
    }

    json_path = out_dir / "provider-match-candidate-report.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    command_rows = "\n".join(
        f"| `{name}` | `{result.get('available')}` | `{result.get('returncode')}` |"
        for name, result in commands.items()
    )

    md = f"""# Provider Match Candidate Report

- Generated At UTC: `{report['generated_at_utc']}`
- Classification: `{report['classification']}`
- Read-Only Provider Candidate Collection Only: `{report['read_only_provider_candidate_collection_only']}`
- Candidate Report Only: `{report['candidate_report_only']}`
- Provider Match Proof Not Claimed: `{report['provider_match_proof_not_claimed']}`
- Activation Execution Gate Decision: `{report['activation_execution_gate_decision']}`
- Provider Match Candidate State: `{report['provider_match_candidate_state']}`
- Provider Match Proof State: `{report['provider_match_proof_state']}`
- Dext Load Proof State: `{report['dext_load_proof_state']}`
- Real GPU Command Execution Proof State: `{report['real_gpu_command_execution_proof_state']}`
- UI Compositor Proof State: `{report['ui_compositor_proof_state']}`
- Metal Proof State: `{report['metal_proof_state']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`
- Dock / Transparency / Blur State: `{report['dock_transparency_blur_state']}`

## Candidate Hints

| Field | Value |
| --- | --- |
| vendor_marker_hits | `{hints['vendor_marker_hits']}` |
| device_marker_hits | `{hints['device_marker_hits']}` |
| iopci_match_marker_hits | `{hints['iopci_match_marker_hits']}` |
| nvidia_marker_present | `{hints['nvidia_marker_present']}` |
| target_candidate_marker_present | `{hints['target_candidate_marker_present']}` |

## Safe Read-Only Commands

| Name | Available | Return Code |
| --- | --- | --- |
{command_rows}

## Conclusion

This report is local read-only provider candidate evidence. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "provider-match-candidate-report.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: PASS_PROVIDER_MATCH_CANDIDATE_COLLECTED_{candidate_state}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
