#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.codesign_identity_entitlement_dryrun_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def has_private_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in PRIVATE_PATTERNS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/codesign-entitlement-dryrun/codesign-identity-entitlement-dryrun.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    derived = local_report.get("derived", {}) if local_report else {}
    commands = local_report.get("commands", {}) if local_report else {}

    private_raw_present = False
    command_summary = {}
    for key, item in commands.items():
        stdout = str(item.get("stdout", ""))
        stderr = str(item.get("stderr", ""))
        private_raw_present = private_raw_present or has_private_text(stdout) or has_private_text(stderr)
        command_summary[key] = {
            "available": bool(item.get("available")),
            "returncode": item.get("returncode"),
            "stdout_present": bool(stdout),
            "stderr_present": bool(stderr),
            "raw_stdout_committed": False,
            "raw_stderr_committed": False,
        }

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_EVIDENCE",
        "dryrun_summary_only": True,
        "host_report_bundle_local_only": True,
        "local_input_present": local_report is not None,
        "raw_stdout_not_committed": True,
        "raw_stderr_not_committed": True,
        "private_raw_output_detected_locally": private_raw_present,
        "private_text_committed": False,
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
        "command_summary": command_summary,
        "derived": {
            "codesigning_identity_detected": bool(derived.get("codesigning_identity_detected")),
            "codesigning_identity_line_count": int(derived.get("codesigning_identity_line_count", 0) or 0),
            "codesign_available": bool(derived.get("codesign_available")),
            "security_available": bool(derived.get("security_available")),
            "host_info_parse_ok": bool(derived.get("host_info_parse_ok")),
            "dext_info_parse_ok": bool(derived.get("dext_info_parse_ok")),
            "host_entitlements_parse_ok": bool(derived.get("host_entitlements_parse_ok")),
            "dext_entitlements_parse_ok": bool(derived.get("dext_entitlements_parse_ok")),
            "host_bundle_id_matches": bool(derived.get("host_bundle_id_matches")),
            "dext_bundle_id_matches": bool(derived.get("dext_bundle_id_matches")),
            "host_system_extension_entitlement_present": bool(derived.get("host_system_extension_entitlement_present")),
            "dext_driverkit_entitlement_present": bool(derived.get("dext_driverkit_entitlement_present")),
            "dext_pci_transport_entitlement_present": bool(derived.get("dext_pci_transport_entitlement_present")),
        },
    }

    json_path = out_dir / "codesign-identity-entitlement-dryrun-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{key}` | `{value['available']}` | `{value['returncode']}` | `{value['stdout_present']}` | `{value['stderr_present']}` |"
        for key, value in command_summary.items()
    )
    derived_rows = "\n".join(f"| `{key}` | `{value}` |" for key, value in summary["derived"].items())

    md = f"""# Codesign Identity + Entitlement Dry-Run Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Dry-Run Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Private Text Committed: `False`
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

## Command Summary

| Command Key | Available | Return Code | Stdout Present | Stderr Present |
| --- | --- | --- | --- | --- |
{cmd_rows}

## Derived Summary

| Key | Value |
| --- | --- |
{derived_rows}
"""
    md_path = out_dir / "codesign-identity-entitlement-dryrun-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
