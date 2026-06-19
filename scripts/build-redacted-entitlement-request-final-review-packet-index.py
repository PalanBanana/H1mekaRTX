#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

ARTIFACT_GROUPS = [
    {
        "phase": "phase62z",
        "description": "local submission readiness gate",
        "candidates": [
            "release-readiness/entitlement-request-local-submission-readiness-gate-check.json",
            "release-readiness/*local-submission-readiness*check.json",
        ],
        "expected_decisions": ["PASS_ENTITLEMENT_REQUEST_LOCAL_SUBMISSION_READINESS_GATE_READY"],
    },
    {
        "phase": "phase63a",
        "description": "manual entitlement request packet export checklist",
        "candidates": [
            "release-readiness/manual-entitlement-request-packet-export-checklist-check.json",
            "docs/hackintosh/manual-entitlement-request-packet-export-checklist.md",
            "release-readiness/*manual*entitlement*export*check*.json",
        ],
        "expected_decisions": None,
    },
    {
        "phase": "phase63b",
        "description": "redacted manual export bundle manifest",
        "candidates": [
            "release-readiness/redacted-manual-export-bundle-manifest-check.json",
            "release-readiness/redacted-export-bundle-manifest-check.json",
            "release-readiness/*redacted*export*bundle*manifest*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_MANUAL_EXPORT_BUNDLE_MANIFEST_READY", "PASS_REDACTED_EXPORT_BUNDLE_MANIFEST_READY"],
    },
    {
        "phase": "phase63c",
        "description": "redacted bundle manifest consistency gate",
        "candidates": [
            "release-readiness/redacted-bundle-manifest-consistency-gate-check.json",
            "release-readiness/*redacted*bundle*manifest*consistency*gate*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_BUNDLE_MANIFEST_CONSISTENCY_GATE_READY"],
    },
    {
        "phase": "phase63d",
        "description": "redacted export bundle dry-run plan",
        "candidates": [
            "release-readiness/redacted-export-bundle-dry-run-plan-check.json",
            "release-readiness/*redacted*export*bundle*dry*run*plan*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_PLAN_READY"],
    },
    {
        "phase": "phase63e",
        "description": "redacted export dry-run plan consistency gate",
        "candidates": [
            "release-readiness/redacted-export-dry-run-plan-consistency-gate-check.json",
            "release-readiness/*redacted*export*dry*run*plan*consistency*gate*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_EXPORT_DRY_RUN_PLAN_CONSISTENCY_GATE_READY"],
    },
    {
        "phase": "phase63f",
        "description": "redacted export bundle dry-run inventory ledger",
        "candidates": [
            "release-readiness/redacted-export-bundle-dry-run-inventory-ledger-check.json",
            "release-readiness/*redacted*export*bundle*dry*run*inventory*ledger*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_EXPORT_BUNDLE_DRY_RUN_INVENTORY_LEDGER_READY"],
    },
    {
        "phase": "phase63g",
        "description": "redacted export inventory consistency gate",
        "candidates": [
            "release-readiness/redacted-export-inventory-consistency-gate-check.json",
            "release-readiness/*redacted*export*inventory*consistency*gate*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_EXPORT_INVENTORY_CONSISTENCY_GATE_READY"],
    },
    {
        "phase": "phase63h",
        "description": "redacted export bundle assembly dry-run manifest",
        "candidates": [
            "release-readiness/redacted-export-bundle-assembly-dry-run-manifest-check.json",
            "release-readiness/*redacted*export*bundle*assembly*dry*run*manifest*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_EXPORT_BUNDLE_ASSEMBLY_DRY_RUN_MANIFEST_READY"],
    },
    {
        "phase": "phase63i",
        "description": "redacted bundle assembly dry-run consistency gate",
        "candidates": [
            "release-readiness/redacted-bundle-assembly-dry-run-consistency-gate-check.json",
            "release-readiness/*redacted*bundle*assembly*dry*run*consistency*gate*check*.json",
        ],
        "expected_decisions": ["PASS_REDACTED_BUNDLE_ASSEMBLY_DRY_RUN_CONSISTENCY_GATE_READY"],
    },
]

PATH_FORBIDDEN_TOKENS = [
    "/Users/",
    "/private/var/folders/",
    "/var/folders/",
    "host-report-bundle",
    "raw-ioregistry",
    "ioregistry-raw",
    "bar-dump",
    "mmio-dump",
    ".p12",
    ".mobileprovision",
    "private-key",
    "provider-handle",
]

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None

def rel_ok(path: str) -> bool:
    pp = Path(path)
    return not pp.is_absolute() and ".." not in pp.parts

def resolve_candidate(patterns: list[str]) -> str | None:
    matches: list[str] = []
    for pattern in patterns:
        direct = ROOT / pattern
        if any(ch in pattern for ch in "*?[]"):
            matches.extend(str(p.relative_to(ROOT)) for p in sorted(ROOT.glob(pattern)) if p.is_file())
        elif direct.is_file():
            matches.append(pattern)
    seen = []
    for m in matches:
        if m not in seen:
            seen.append(m)
    return seen[0] if seen else None

def decision_ok(data, expected):
    if expected is None:
        return True
    if not isinstance(data, dict):
        return False
    return data.get("decision") in expected

index_entries = []
for group in ARTIFACT_GROUPS:
    rel = resolve_candidate(group["candidates"])
    if rel is None:
        index_entries.append({
            "phase": group["phase"],
            "description": group["description"],
            "relative_path": None,
            "exists": False,
            "is_relative_path": False,
            "sha256": None,
            "byte_count": None,
            "expected_decisions": group["expected_decisions"],
            "actual_decision": None,
            "decision_ok": False,
            "forbidden_path_hit": False,
            "copied_by_this_phase": False,
            "archived_by_this_phase": False,
            "request_submitted_by_this_phase": False,
        })
        continue
    p = ROOT / rel
    data = read_json(p) if p.suffix == ".json" else None
    actual_decision = data.get("decision") if isinstance(data, dict) else None
    forbidden = any(tok.lower() in rel.lower() for tok in PATH_FORBIDDEN_TOKENS)
    index_entries.append({
        "phase": group["phase"],
        "description": group["description"],
        "relative_path": rel,
        "exists": p.exists(),
        "is_relative_path": rel_ok(rel),
        "sha256": sha256(p) if p.exists() else None,
        "byte_count": p.stat().st_size if p.exists() else None,
        "expected_decisions": group["expected_decisions"],
        "actual_decision": actual_decision,
        "decision_ok": decision_ok(data, group["expected_decisions"]),
        "forbidden_path_hit": forbidden,
        "copied_by_this_phase": False,
        "archived_by_this_phase": False,
        "request_submitted_by_this_phase": False,
    })

entries_present = bool(index_entries)
all_exist = entries_present and all(e["exists"] for e in index_entries)
all_relative = entries_present and all(e["is_relative_path"] for e in index_entries)
all_decisions_ok = entries_present and all(e["decision_ok"] for e in index_entries)
all_sha256_present = entries_present and all(isinstance(e["sha256"], str) and len(e["sha256"]) == 64 for e in index_entries)
all_byte_count_present = entries_present and all(isinstance(e["byte_count"], int) and e["byte_count"] >= 0 for e in index_entries)
forbidden_absent = entries_present and all(e["forbidden_path_hit"] is False for e in index_entries)
all_not_copied = entries_present and all(e["copied_by_this_phase"] is False and e["archived_by_this_phase"] is False for e in index_entries)

def expect(name: str, ok: bool):
    return {"id": name, "status": "PASS" if ok else "FAIL"}

checks = [
    expect("index_entries_present", entries_present),
    expect("index_entry_count_10", len(index_entries) == 10),
    expect("index_all_exist", all_exist),
    expect("index_all_relative", all_relative),
    expect("index_all_decisions_ok", all_decisions_ok),
    expect("index_all_sha256_present", all_sha256_present),
    expect("index_all_byte_count_present", all_byte_count_present),
    expect("index_forbidden_path_absent", forbidden_absent),
    expect("index_all_not_copied", all_not_copied),
]

false_fields = [
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
    "schema": "h1mekartx.redacted_entitlement_request_final_review_packet_index_output.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "classification": "CLASSIFICATION_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX_OUTPUT",
    "decision": "PASS_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX_READY" if ready else "FAIL_REDACTED_ENTITLEMENT_REQUEST_FINAL_REVIEW_PACKET_INDEX",
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "final_review_packet_index_only": True,
    "redacted_entitlement_request_final_review_packet_index_ready": ready,
    "index_entries": index_entries,
    "index_entry_count": len(index_entries),
    "index_all_exist": all_exist,
    "index_all_relative": all_relative,
    "index_all_decisions_ok": all_decisions_ok,
    "index_all_sha256_present": all_sha256_present,
    "index_all_byte_count_present": all_byte_count_present,
    "index_forbidden_absent": forbidden_absent,
    "index_all_not_copied": all_not_copied,
    "checks": checks,
    "pass_count": pass_count,
    "fail_count": fail_count,
    "expected_vendor_id": "0x10de",
    "expected_device_id": "0x2f04",
    "expected_iopcimatch": "0x2f0410de",
    "expected_driverkit_bundle_identifier": "dev.h1meka.H1mekaRTXDriver",
    "expected_host_app_bundle_identifier": "dev.h1meka.H1mekaRTXHost",
    "next_gate": "phase63k-local-only-final-review-command-checklist",
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

json_path = OUT / "redacted-entitlement-request-final-review-packet-index.json"
md_path = OUT / "redacted-entitlement-request-final-review-packet-index.md"
json_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

entry_rows = "\n".join(
    f"| `{e['phase']}` | `{e['relative_path']}` | `{e['exists']}` | `{e['decision_ok']}` | `{e['byte_count']}` | `{e['sha256']}` |"
    for e in index_entries
)
check_rows = "\n".join(f"| `{c['id']}` | `{c['status']}` |" for c in checks)

md_path.write_text(f"""# Redacted Entitlement Request Final Review Packet Index

- Decision: `{out['decision']}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Final Review Packet Index Only: `True`
- Index Entry Count: `{out['index_entry_count']}`
- Index All Exist: `{out['index_all_exist']}`
- Index All Relative: `{out['index_all_relative']}`
- Index All Decisions OK: `{out['index_all_decisions_ok']}`
- Index All SHA-256 Present: `{out['index_all_sha256_present']}`
- Index All Byte Count Present: `{out['index_all_byte_count_present']}`
- Index Forbidden Absent: `{out['index_forbidden_absent']}`
- Index All Not Copied: `{out['index_all_not_copied']}`
- PASS Count: `{out['pass_count']}`
- FAIL Count: `{out['fail_count']}`
- Redacted Entitlement Request Final Review Packet Index Ready: `{out['redacted_entitlement_request_final_review_packet_index_ready']}`
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

## Indexed Artifacts

| Phase | Relative Path | Exists | Decision OK | Bytes | SHA-256 |
| --- | --- | --- | --- | ---: | --- |
{entry_rows}

## Checks

| Check | Status |
| --- | --- |
{check_rows}
""", encoding="utf-8")

print("Decision:", out["decision"])
if not ready:
    for e in index_entries:
        if not e["exists"] or not e["decision_ok"] or e["forbidden_path_hit"]:
            print("ENTRY_PROBLEM:", e["phase"], e["relative_path"], "exists=", e["exists"], "decision_ok=", e["decision_ok"], "forbidden_path_hit=", e["forbidden_path_hit"], "actual=", e["actual_decision"])
