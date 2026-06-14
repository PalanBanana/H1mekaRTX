#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

SCHEMA = "h1mekartx.provider_match_repair_readiness_bridge_check.v1"

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-repair-readiness-bridge.json"
doc_path = ROOT / "docs/driverkit/provider-match-repair-readiness-bridge.md"
phase60a_summary_path = OUT / "provider-match-evidence-repair-diagnostics-summary.json"
phase60a_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-evidence-repair-diagnostics.json"
phase60_manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json"

manifest = read_json(manifest_path)
phase60a_summary = read_json(phase60a_summary_path)
phase60a_manifest = read_json(phase60a_manifest_path)
phase60_manifest = read_json(phase60_manifest_path)

repair = phase60a_summary.get("repair_decision", {}) if phase60a_summary else {}
derived = phase60a_summary.get("derived", {}) if phase60a_summary else {}

extension_status_observed = bool(repair.get("extension_status_observed"))
pci_identity_observed = bool(repair.get("pci_identity_observed"))
personality_matches = bool(repair.get("personality_matches"))
bundle_ids_match = bool(repair.get("bundle_ids_match"))
provider_open_allowed = bool(repair.get("provider_open_allowed"))
repaired_provider_match_ready = bool(repair.get("repaired_provider_match_ready"))

provider_open_still_blocked = bool(derived.get("provider_open_still_blocked"))
ioserviceopen_still_blocked = bool(derived.get("ioserviceopen_still_blocked"))
bar_mapping_still_blocked = bool(derived.get("bar_mapping_still_blocked"))
gpu_command_submission_still_blocked = bool(derived.get("gpu_command_submission_still_blocked"))
dock_proof_still_blocked = bool(derived.get("dock_transparency_blur_proof_still_blocked"))

bridge_ready = bool(
    phase60a_summary
    and extension_status_observed
    and pci_identity_observed
    and personality_matches
    and bundle_ids_match
    and repaired_provider_match_ready
    and provider_open_allowed is False
    and provider_open_still_blocked
    and ioserviceopen_still_blocked
    and bar_mapping_still_blocked
    and gpu_command_submission_still_blocked
    and dock_proof_still_blocked
)

block_reasons = []
if not phase60a_summary:
    block_reasons.append("phase60a_summary_missing")
if not extension_status_observed:
    block_reasons.append("extension_status_observed_false")
if not pci_identity_observed:
    block_reasons.append("pci_identity_observed_false")
if not personality_matches:
    block_reasons.append("personality_matches_false")
if not bundle_ids_match:
    block_reasons.append("bundle_ids_match_false")
if not repaired_provider_match_ready:
    block_reasons.append("repaired_provider_match_ready_false")
if provider_open_allowed is not False:
    block_reasons.append("provider_open_allowed_not_false")
if not provider_open_still_blocked:
    block_reasons.append("provider_open_still_blocked_false")
if not ioserviceopen_still_blocked:
    block_reasons.append("ioserviceopen_still_blocked_false")
if not bar_mapping_still_blocked:
    block_reasons.append("bar_mapping_still_blocked_false")
if not gpu_command_submission_still_blocked:
    block_reasons.append("gpu_command_submission_still_blocked_false")
if not dock_proof_still_blocked:
    block_reasons.append("dock_transparency_blur_proof_still_blocked_false")

checks = []
add(checks, "manifest_exists", manifest_path.exists(), str(manifest_path))
add(checks, "doc_exists", doc_path.exists(), str(doc_path))
add(checks, "phase60a_summary_exists", phase60a_summary_path.exists(), str(phase60a_summary_path))
add(checks, "phase60a_manifest_exists", phase60a_manifest_path.exists(), str(phase60a_manifest_path))
add(checks, "phase60_manifest_exists", phase60_manifest_path.exists(), str(phase60_manifest_path))
add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provider_match_repair_readiness_bridge.v1"), "manifest schema")
add(checks, "phase60a_summary_schema", bool(phase60a_summary and phase60a_summary.get("schema") == "h1mekartx.provider_match_evidence_repair_diagnostics_summary.v1"), "phase60a summary schema")
add(checks, "phase60a_manifest_schema", bool(phase60a_manifest and phase60a_manifest.get("schema") == "h1mekartx.provider_match_evidence_repair_diagnostics.v1"), "phase60a manifest schema")
add(checks, "phase60_manifest_schema", bool(phase60_manifest and phase60_manifest.get("schema") == "h1mekartx.provider_match_without_open_readiness_gate.v1"), "phase60 manifest schema")

for field in [
    "provider_match_repair_readiness_bridge_ready",
    "preflight_bridge_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "provider_open_allowed_now",
    "ioserviceopen_allowed_now",
    "bar_mapping_allowed_now",
    "gpu_command_submission_allowed_now",
    "activation_submitted_by_this_phase",
    "deactivation_submitted_by_this_phase",
    "install_attempted",
    "manual_dext_load_attempted",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)

add(checks, "provider_open_still_blocked", provider_open_still_blocked, "provider open boundary")
add(checks, "ioserviceopen_still_blocked", ioserviceopen_still_blocked, "IOServiceOpen boundary")
add(checks, "bar_mapping_still_blocked", bar_mapping_still_blocked, "BAR mapping boundary")
add(checks, "gpu_command_submission_still_blocked", gpu_command_submission_still_blocked, "GPU command boundary")
add(checks, "dock_transparency_blur_proof_still_blocked", dock_proof_still_blocked, "UI proof boundary")

failed = sum(1 for c in checks if not c["passed"])

if failed:
    decision = "FAIL_PROVIDER_MATCH_REPAIR_READINESS_BRIDGE"
elif bridge_ready:
    decision = "PASS_PROVIDER_MATCH_REPAIR_READY_FOR_PHASE61_PREFLIGHT"
else:
    decision = "PASS_PROVIDER_MATCH_REPAIR_BLOCKED_PENDING_FIX"

report = {
    "schema": SCHEMA,
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "provider_match_repair_bridge_ready": bridge_ready,
    "provider_open_allowed_now": False,
    "ioserviceopen_allowed_now": False,
    "bar_mapping_allowed_now": False,
    "gpu_command_submission_allowed_now": False,
    "extension_status_observed": extension_status_observed,
    "pci_identity_observed": pci_identity_observed,
    "personality_matches": personality_matches,
    "bundle_ids_match": bundle_ids_match,
    "repaired_provider_match_ready": repaired_provider_match_ready,
    "provider_open_allowed_from_repair": provider_open_allowed,
    "provider_open_still_blocked": provider_open_still_blocked,
    "ioserviceopen_still_blocked": ioserviceopen_still_blocked,
    "bar_mapping_still_blocked": bar_mapping_still_blocked,
    "gpu_command_submission_still_blocked": gpu_command_submission_still_blocked,
    "dock_transparency_blur_proof_still_blocked": dock_proof_still_blocked,
    "block_reasons": block_reasons,
    "next_gate_if_ready": "phase61-provider-open-hard-optin-preflight-no-bar-no-gpu-commands",
    "next_gate_if_blocked": "phase60c-provider-match-personality-entitlement-fix-plan",
    "checks": checks,
}

(OUT / "provider-match-repair-readiness-bridge-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
block_rows = "\n".join(f"| `{reason}` |" for reason in block_reasons) or "| `none` |"

md = f"""# Provider Match Repair Readiness Bridge Check

- Decision: `{decision}`
- Provider Match Repair Bridge Ready: `{bridge_ready}`
- Provider Open Allowed Now: `False`
- IOServiceOpen Allowed Now: `False`
- BAR Mapping Allowed Now: `False`
- GPU Command Submission Allowed Now: `False`
- Extension Status Observed: `{extension_status_observed}`
- PCI Identity Observed: `{pci_identity_observed}`
- Personality Matches: `{personality_matches}`
- Bundle IDs Match: `{bundle_ids_match}`
- Repaired Provider Match Ready: `{repaired_provider_match_ready}`
- Provider Open Still Blocked: `{provider_open_still_blocked}`
- IOServiceOpen Still Blocked: `{ioserviceopen_still_blocked}`
- BAR Mapping Still Blocked: `{bar_mapping_still_blocked}`
- GPU Command Submission Still Blocked: `{gpu_command_submission_still_blocked}`
- Dock Transparency Blur Proof Still Blocked: `{dock_proof_still_blocked}`

## Block Reasons

| Reason |
| --- |
{block_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "provider-match-repair-readiness-bridge-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
