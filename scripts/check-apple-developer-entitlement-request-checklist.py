#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/apple-developer-entitlement-request-checklist.json"
manual_path = ROOT / "tools/driverkit-buildable-scaffold/apple-developer-portal-manual-checklist.json"
doc_path = ROOT / "docs/driverkit/apple-developer-entitlement-request-checklist.md"
phase60q_manifest = ROOT / "tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json"

manifest = read_json(manifest_path)
manual = read_json(manual_path)
phase60q = read_json(phase60q_manifest)

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("manual_checklist_exists", manual_path),
    ("doc_exists", doc_path),
    ("phase60q_manifest_exists", phase60q_manifest),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.apple_developer_entitlement_request_checklist.v1"), "manifest schema")
add(checks, "manual_schema", bool(manual and manual.get("schema") == "h1mekartx.apple_developer_portal_manual_checklist.v1"), "manual schema")
add(checks, "phase60q_schema", bool(phase60q and phase60q.get("schema") == "h1mekartx.provisioning_entitlement_hardblock_gate.v1"), "phase60q schema")

for field in [
    "apple_developer_entitlement_request_checklist_ready",
    "portal_preparation_only",
    "paid_developer_team_required",
    "personal_team_blocked",
    "system_extension_capability_required",
    "driverkit_entitlement_approval_required",
    "driverkit_pci_transport_entitlement_required",
    "host_profile_required",
    "dext_profile_required",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "xcodebuild_attempted_by_this_phase",
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

expected = {
    "host_bundle_id": "dev.h1meka.H1mekaRTXHost",
    "dext_bundle_id": "dev.h1meka.H1mekaRTXDriver",
    "system_extension_entitlement": "com.apple.developer.system-extension.install",
    "driverkit_entitlement": "com.apple.developer.driverkit",
    "driverkit_pci_transport_entitlement": "com.apple.developer.driverkit.transport.pci",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
}
for key, value in expected.items():
    add(checks, f"manifest_{key}", bool(manifest and manifest.get(key) == value), f"{key}={value}")

if manual:
    items = manual.get("items", [])
    item_ids = {item.get("id") for item in items}
    for required_id in [
        "paid_team",
        "host_app_id",
        "host_system_extension_capability",
        "dext_app_id",
        "driverkit_entitlement",
        "driverkit_pci_transport",
        "host_profile",
        "dext_profile",
    ]:
        add(checks, f"manual_item_{required_id}", required_id in item_ids, required_id)

doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
for token in [
    "Paid Apple Developer Program",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "com.apple.developer.system-extension.install",
    "com.apple.developer.driverkit",
    "com.apple.developer.driverkit.transport.pci",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "provider open remains blocked",
    "GPU command submission remains blocked",
    "Dock/transparency/blur proof remains blocked",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_").replace("/", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_APPLE_DEVELOPER_ENTITLEMENT_REQUEST_CHECKLIST_READY" if failed == 0 else "FAIL_APPLE_DEVELOPER_ENTITLEMENT_REQUEST_CHECKLIST"

report = {
    "schema": "h1mekartx.apple_developer_entitlement_request_checklist_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "portal_preparation_only": True,
    "paid_developer_team_required": True,
    "personal_team_blocked": True,
    "driverkit_entitlement_approval_required": True,
    "system_extension_capability_required": True,
    "driverkit_pci_transport_entitlement_required": True,
    "phase61_allowed_now": False,
    "xcodebuild_attempted_by_this_phase": False,
    "activation_submitted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "checks": checks,
}

(OUT / "apple-developer-entitlement-request-checklist-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Apple Developer Entitlement Request Checklist Check

- Decision: `{decision}`
- Portal Preparation Only: `True`
- Paid Developer Team Required: `True`
- Personal Team Blocked: `True`
- DriverKit Entitlement Approval Required: `True`
- System Extension Capability Required: `True`
- DriverKit PCI Transport Entitlement Required: `True`
- Phase 61 Allowed Now: `False`
- Xcodebuild Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
(OUT / "apple-developer-entitlement-request-checklist-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
