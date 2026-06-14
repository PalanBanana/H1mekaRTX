#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.provider_match_evidence_repair_diagnostics_summary.v1"

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
    parser.add_argument("--input", default="host-report-bundle/provider-match-evidence-repair/provider-match-evidence-repair-local-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = (root / args.input).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    local_report = read_json(input_path)
    commands = local_report.get("commands", {}) if local_report else {}
    derived = local_report.get("derived", {}) if local_report else {}
    bundle_parse = local_report.get("bundle_parse", {}) if local_report else {}

    private_raw_detected = False
    for item in commands.values():
        private_raw_detected = private_raw_detected or has_private_text(item.get("stdout")) or has_private_text(item.get("stderr")) or has_private_text(" ".join(map(str, item.get("command", []))))

    extension_status_observed = bool(derived.get("extension_identifier_observed_in_systemextensionsctl"))
    pci_identity_observed = bool(derived.get("rtx_vendor_10de_observed_in_ioreg") and derived.get("rtx_device_2f04_observed_in_ioreg"))
    personality_matches = bool(derived.get("dext_personality_provider_class_matches") and derived.get("dext_personality_iopcimatch_matches"))
    bundle_ids_match = bool(derived.get("host_bundle_id_matches") and derived.get("dext_bundle_id_matches"))

    repaired_provider_match_ready = bool(
        extension_status_observed
        and pci_identity_observed
        and personality_matches
        and bundle_ids_match
        and derived.get("provider_open_still_blocked", True)
        and derived.get("ioserviceopen_still_blocked", True)
        and derived.get("bar_mapping_still_blocked", True)
        and derived.get("gpu_command_submission_still_blocked", True)
    )

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_report_present": local_report is not None,
        "read_only_diagnostics_only": True,
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
        "sanitized_commands": {name: command_summary(cmd) for name, cmd in commands.items()},
        "bundle_parse_summary": {
            "host_info_key_count": len(bundle_parse.get("host_info_keys", [])),
            "dext_info_key_count": len(bundle_parse.get("dext_info_keys", [])),
            "dext_personality_count": len(bundle_parse.get("dext_personalities", {})),
        },
        "derived": {
            "host_bundle_exists": bool(derived.get("host_bundle_exists")),
            "dext_bundle_exists": bool(derived.get("dext_bundle_exists")),
            "host_info_parse_ok": bool(derived.get("host_info_parse_ok")),
            "dext_info_parse_ok": bool(derived.get("dext_info_parse_ok")),
            "host_bundle_id_matches": bool(derived.get("host_bundle_id_matches")),
            "dext_bundle_id_matches": bool(derived.get("dext_bundle_id_matches")),
            "dext_personalities_present": bool(derived.get("dext_personalities_present")),
            "dext_personality_provider_class_matches": bool(derived.get("dext_personality_provider_class_matches")),
            "dext_personality_iopcimatch_matches": bool(derived.get("dext_personality_iopcimatch_matches")),
            "systemextensionsctl_available": bool(derived.get("systemextensionsctl_available")),
            "systemextensionsctl_returncode": derived.get("systemextensionsctl_returncode"),
            "extension_identifier_observed_in_systemextensionsctl": extension_status_observed,
            "systemextension_status_tokens": derived.get("systemextension_status_tokens", []),
            "ioreg_available": bool(derived.get("ioreg_available")),
            "ioreg_iopcidevice_returncode": derived.get("ioreg_iopcidevice_returncode"),
            "rtx_vendor_10de_observed_in_ioreg": bool(derived.get("rtx_vendor_10de_observed_in_ioreg")),
            "rtx_device_2f04_observed_in_ioreg": bool(derived.get("rtx_device_2f04_observed_in_ioreg")),
            "rtx_iopcimatch_2f0410de_observed_in_ioreg": bool(derived.get("rtx_iopcimatch_2f0410de_observed_in_ioreg")),
            "extension_identifier_observed_in_ioreg": bool(derived.get("extension_identifier_observed_in_ioreg")),
            "h1meka_string_observed_in_ioreg": bool(derived.get("h1meka_string_observed_in_ioreg")),
            "nvidia_string_observed_in_ioreg": bool(derived.get("nvidia_string_observed_in_ioreg")),
            "display_profiler_nvidia_observed": bool(derived.get("display_profiler_nvidia_observed")),
            "display_profiler_rtx_observed": bool(derived.get("display_profiler_rtx_observed")),
            "provider_match_blocked_reason_hint": derived.get("provider_match_blocked_reason_hint", []),
            "provider_open_still_blocked": bool(derived.get("provider_open_still_blocked", True)),
            "ioserviceopen_still_blocked": bool(derived.get("ioserviceopen_still_blocked", True)),
            "bar_mapping_still_blocked": bool(derived.get("bar_mapping_still_blocked", True)),
            "gpu_command_submission_still_blocked": bool(derived.get("gpu_command_submission_still_blocked", True)),
            "dock_transparency_blur_proof_still_blocked": bool(derived.get("dock_transparency_blur_proof_still_blocked", True)),
        },
        "repair_decision": {
            "extension_status_observed": extension_status_observed,
            "pci_identity_observed": pci_identity_observed,
            "personality_matches": personality_matches,
            "bundle_ids_match": bundle_ids_match,
            "provider_open_allowed": False,
            "repaired_provider_match_ready": repaired_provider_match_ready,
            "next_gate_if_ready": "rerun provider-match-without-open readiness gate",
            "next_gate_if_blocked": "fix system extension activation/provider personality/PCI identity evidence"
        }
    }

    json_path = out_dir / "provider-match-evidence-repair-diagnostics-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd_rows = "\n".join(
        f"| `{name}` | `{item['available']}` | `{item['returncode']}` | `{item['stdout_present']}` | `{item['stderr_present']}` |"
        for name, item in summary["sanitized_commands"].items()
    ) or "| `none` | `False` | `—` | `False` | `False` |"
    derived_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["derived"].items())
    repair_rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary["repair_decision"].items())

    md = f"""# Provider Match Evidence Repair Diagnostics Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Read-Only Diagnostics Only: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
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

## Repair Decision

| Key | Value |
| --- | --- |
{repair_rows}
"""
    md_path = out_dir / "provider-match-evidence-repair-diagnostics-summary.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
