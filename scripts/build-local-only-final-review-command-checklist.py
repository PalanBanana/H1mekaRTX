#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

COMMANDS = [
    {
        "id": "repo-status",
        "purpose": "Inspect uncommitted and ignored local workspace noise before final human review.",
        "command": "git status --short --ignored",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "phase63j-pr-status",
        "purpose": "Confirm Phase 63J merge and checks without modifying the repository.",
        "command": "gh pr view 245 --repo PalanBanana/H1mekaRTX --json number,state,mergedAt,url,statusCheckRollup --jq '.'",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "final-review-index-json-format",
        "purpose": "Pretty-print the local final review packet index JSON to a temporary review file.",
        "command": "python3 -m json.tool release-readiness/redacted-entitlement-request-final-review-packet-index.json >/tmp/h1mekartx-final-review-index.pretty.json",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "final-review-index-check-json-format",
        "purpose": "Pretty-print the local final review packet index check JSON to a temporary review file.",
        "command": "python3 -m json.tool release-readiness/redacted-entitlement-request-final-review-packet-index-check.json >/tmp/h1mekartx-final-review-index-check.pretty.json",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "final-review-pass-grep",
        "purpose": "Confirm the final review index PASS decision in local release-readiness artifacts.",
        "command": "grep -R \"PASS_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX_READY\" release-readiness/redacted-entitlement-request-final-review-packet-index*.json",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "metal-claim-false-grep",
        "purpose": "Confirm current RTX 5070 Metal acceleration remains unclaimed in local artifacts.",
        "command": "grep -R 'current_rtx5070_metal_acceleration_claimed.*false' release-readiness/redacted-entitlement-request-final-review-packet-index*.json",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "dock-blur-claim-false-grep",
        "purpose": "Confirm Dock/transparency/blur acceleration remains unclaimed in local artifacts.",
        "command": "grep -R 'dock_transparency_blur_acceleration_claimed.*false' release-readiness/redacted-entitlement-request-final-review-packet-index*.json",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "final-review-doc-preview",
        "purpose": "Preview the first 80 lines of the local final review packet index document.",
        "command": "sed -n '1,80p' docs/hackintosh/redacted-entitlement-request-final-review-packet-index.md",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    },
    {
        "id": "recent-ci-runs",
        "purpose": "Inspect recent GitHub Actions runs without changing repository state.",
        "command": "gh run list --repo PalanBanana/H1mekaRTX --limit 5",
        "read_only": True,
        "local_only_review": True,
        "submits_request": False,
    }
]

FORBIDDEN_COMMAND_TOKENS = [
    "IOServiceOpen",
    "ioreg",
    "system_profiler",
    "Apple Developer",
    "developer.apple.com/account",
    "curl ",
    "gh api -X POST",
    "gh api -X PUT",
    "zip ",
    "tar ",
    "cp ",
    "ditto ",
    "codesign",
    "xcrun notarytool",
    "kextload",
    "kmutil",
    "ioregistry",
    "BAR0",
    "mmio",
    "firmware",
    "gpu-reset",
]

def read_json(rel: str):
    p = ROOT / rel
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))

final_index = read_json("release-readiness/redacted-entitlement-request-final-review-packet-index.json")
final_index_check = read_json("release-readiness/redacted-entitlement-request-final-review-packet-index-check.json")

final_index_pass = bool(final_index and final_index.get("decision") == "PASS_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX_READY")
final_index_check_pass = bool(final_index_check and final_index_check.get("decision") == "PASS_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX_READY")
final_index_ready = bool(final_index and final_index.get("redacted_entitlement_request_final_review_packet_index_ready") is True)

def command_safe(cmd: str) -> bool:
    lowered = cmd.lower()
    for token in FORBIDDEN_COMMAND_TOKENS:
        if token.lower() in lowered:
            return False
    return True

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

commands_present = bool(COMMANDS)
commands_all_read_only = commands_present and all(c.get("read_only") is True for c in COMMANDS)
commands_all_local_review = commands_present and all(c.get("local_only_review") is True for c in COMMANDS)
commands_all_no_submit = commands_present and all(c.get("submits_request") is False for c in COMMANDS)
commands_all_safe = commands_present and all(command_safe(c.get("command", "")) for c in COMMANDS)
commands_no_execution = True
commands_no_archive_or_copy = commands_present and all(("zip " not in c["command"] and "tar " not in c["command"] and "cp " not in c["command"] and "ditto " not in c["command"]) for c in COMMANDS)

checks = [
    expect("final_review_packet_index_passed", final_index_pass),
    expect("final_review_packet_index_check_passed", final_index_check_pass),
    expect("final_review_packet_index_ready", final_index_ready),
    expect("commands_present", commands_present),
    expect("commands_all_read_only", commands_all_read_only),
    expect("commands_all_local_review", commands_all_local_review),
    expect("commands_all_no_submit", commands_all_no_submit),
    expect("commands_all_safe", commands_all_safe),
    expect("commands_no_execution_by_this_phase", commands_no_execution),
    expect("commands_no_archive_or_copy", commands_no_archive_or_copy),
]

false_fields = [
    "checklist_commands_executed_by_this_phase",
    "bundle_archive_created_by_this_phase",
    "files_copied_to_export_bundle_by_this_phase",
    "certificates_exported",
    "private_keys_exported",
    "provisioning_assets_exported",
    "raw_ioregistry_exported",
    "provider_handles_exported",
    "actual_apple_entitlement_request_submitted",
    "contacted_apple_by_this_phase",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar0_read_attempted",
    "bar0_write_attempted",
    "gpu_command_submission_attempted",
    "current_rtx5070_metal_acceleration_claimed",
    "dock_transparency_blur_acceleration_claimed",
    "absolute_paths_recorded",
]

fail_count = sum(1 for c in checks if c["status"] == "FAIL")
pass_count = sum(1 for c in checks if c["status"] == "PASS")
ready = fail_count == 0

out = {
    "schema": "h1mekartx.local_only_final_review_command_checklist_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST_OUTPUT",
    "decision": "PASS_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST_READY" if ready else "FAIL_LOCAL_ONLY_FINAL_REVIEW_COMMAND_CHECKLIST",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "local_final_review_command_checklist_only": True,
    "local_only_final_review_command_checklist_ready": ready,
    "input_final_review_packet_index_present": final_index is not None,
    "input_final_review_packet_index_check_present": final_index_check is not None,
    "input_final_review_packet_index_pass": final_index_pass,
    "input_final_review_packet_index_check_pass": final_index_check_pass,
    "input_final_review_packet_index_ready": final_index_ready,
    "checklist_commands": COMMANDS,
    "checklist_command_count": len(COMMANDS),
    "commands_all_read_only": commands_all_read_only,
    "commands_all_local_review": commands_all_local_review,
    "commands_all_no_submit": commands_all_no_submit,
    "commands_all_safe": commands_all_safe,
    "commands_no_execution_by_this_phase": commands_no_execution,
    "commands_no_archive_or_copy": commands_no_archive_or_copy,
    "checks": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63l-local-only-final-review-command-checklist-consistency-gate",
}
for field in false_fields:
    out[field] = False
for field in [
    "driverkit_entitlement_requested_by_this_phase",
    "driverkit_pci_entitlement_requested_by_this_phase",
    "driverkit_entitlement_approved",
    "app_id_created_by_this_phase",
    "provisioning_profile_created_by_this_phase",
    "driverkit_profile_created",
    "driverkit_profile_ready",
    "driverkit_extension_signed_by_this_phase",
    "driverkit_extension_loaded",
    "driverkit_extension_activated",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "firmware_load_attempted",
    "gpu_reset_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "metal_proof_claimed",
    "current_rtx5070_ui_smoothness_claimed",
]:
    out[field] = False

json_path = OUT / "local-only-final-review-command-checklist.json"
md_path = OUT / "local-only-final-review-command-checklist.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

command_rows = "\n".join(
    f"| `{c['id']}` | `{c['command']}` | `{c['read_only']}` | `{c['submits_request']}` |"
    for c in COMMANDS
)
check_rows = "\n".join(f"| `{c['id']}` | `{c['status']}` |" for c in checks)

md_path.write_text(f"""# Local-Only Final Review Command Checklist

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Local Final Review Command Checklist Only: `True`
- Input Final Review Packet Index PASS: `{out['input_final_review_packet_index_pass']}`
- Input Final Review Packet Index Check PASS: `{out['input_final_review_packet_index_check_pass']}`
- Input Final Review Packet Index Ready: `{out['input_final_review_packet_index_ready']}`
- Checklist Command Count: `{out['checklist_command_count']}`
- Commands All Read-Only: `{out['commands_all_read_only']}`
- Commands All Local Review: `{out['commands_all_local_review']}`
- Commands All No Submit: `{out['commands_all_no_submit']}`
- Commands All Safe: `{out['commands_all_safe']}`
- Commands Executed By This Phase: `False`
- Bundle Archive Created By This Phase: `False`
- Files Copied To Export Bundle By This Phase: `False`
- Certificates Exported: `False`
- Private Keys Exported: `False`
- Provisioning Assets Exported: `False`
- Raw IORegistry Exported: `False`
- Provider Handles Exported: `False`
- Actual Apple Entitlement Request Submitted: `False`
- Contacted Apple By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- BAR0 Read Attempted: `False`
- BAR0 Write Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Dock/Transparency/Blur Acceleration Claimed: `False`
- Next Gate: `{out['next_gate']}`

## Commands

| ID | Command | Read Only | Submits Request |
| --- | --- | --- | --- |
{command_rows}

## Checks

| Check | Status |
| --- | --- |
{check_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
if not ready:
    for c in checks:
        if c["status"] == "FAIL":
            print("FAIL:", c["id"])
