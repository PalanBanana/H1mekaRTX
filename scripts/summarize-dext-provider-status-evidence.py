#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.dext_load_provider_match_status_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"Developer ID Application:[^\n\r]+"),
    re.compile(r"Apple Development:[^\n\r]+"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def has_private_text(value: str) -> bool:
    return any(pattern.search(str(value or "")) for pattern in PRIVATE_PATTERNS)

def command_summary(cmd: dict | None) -> dict:
    cmd = cmd or {}
    stdout = str(cmd.get("stdout", ""))
    stderr = str(cmd.get("stderr", ""))
    return {
        "available": bool(cmd.get("available")),
        "returncode": cmd.get("returncode"),
        "stdout_present": bool(stdout),
        "stderr_present": bool(stderr),
        "raw_stdout_committed": False,
        "raw_stderr_committed": False,
        "command_body_committed": False,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/dext-provider-status/dext-provider-status-local-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    sanitized_commands = {name: command_summary(cmd) for name, cmd in commands.items()}

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_report_present": local_report is not None,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
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
        "sanitized_commands": sanitized_commands,
        "derived": {
            "activation_report_present": bool(derived.get("activation_report_present")),
            "activation_command_completed": bool(derived.get("activation_command_completed")),
            "activation_submitted_locally": bool(derived.get("activation_submitted_locally")),
            "systemextensionsctl_available": bool(derived.get("systemextensionsctl_available")),
            "systemextensionsctl_returncode": derived.get("systemextensionsctl_returncode"),
            "extension_identifier_observed_in_systemextensionsctl": bool(derived.get("extension_identifier_observed_in_systemextensionsctl")),
            "status_contains_activated": bool(derived.get("status_contains_activated")),
            "status_contains_enabled": bool(derived.get("status_contains_enabled")),
            "status_contains_waiting_or_needs_user": bool(derived.get("status_contains_waiting_or_needs_user")),
            "ioreg_available": bool(derived.get("ioreg_available")),
            "ioreg_iopcidevice_returncode": derived.get("ioreg_iopcidevice_returncode"),
            "rtx_vendor_10de_observed": bool(derived.get("rtx_vendor_10de_observed")),
            "rtx_device_2f04_observed": bool(derived.get("rtx_device_2f04_observed")),
            "rtx_iopcimatch_2f0410de_observed": bool(derived.get("rtx_iopcimatch_2f0410de_observed")),
            "extension_identifier_observed_in_ioreg": bool(derived.get("extension_identifier_observed_in_ioreg")),
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "ioserviceopen_still_blocked": bool(derived.get("ioserviceopen_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
            "dock_transparency_blur_proof_still_blocked": bool(derived.get("dock_transparency_blur_proof_still_blocked", True)),
        },
        "provider_match_readiness": {
            "system_extension_status_observed": bool(derived.get("extension_identifier_observed_in_systemextensionsctl")),
            "rtx_pci_identity_observed": bool(derived.get("rtx_vendor_10de_observed") and derived.get("rtx_device_2f04_observed")),
            "provider_open_allowed": False,
            "next_gate": "provider_match_without_open_readiness_gate"
        }
    }

    json_path = out_dir / "dext-load-provider-match-status-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{name}` | `{item['available']}` | `{item['returncode']}` | `{item['stdout_present']}` | `{item['stderr_present']}` |"
        for name, item in sanitized_commands.items()
    ) or "| `none` | `False` | `—` | `False` | `False` |"
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["derived"].items())
    readiness_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["provider_match_readiness"].items())

    md = f"""# Dext Load + Provider Match Status Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Local Report Present: `{summary['local_report_present']}`
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

## Sanitized Commands

| Command | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- |
{cmd_rows}

## Derived Evidence

| Key | Value |
| --- | --- |
{derived_rows}

## Provider Match Readiness

| Key | Value |
| --- | --- |
{readiness_rows}
"""
    md_path = out_dir / "dext-load-provider-match-status-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_DEXT_LOAD_PROVIDER_MATCH_STATUS_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
