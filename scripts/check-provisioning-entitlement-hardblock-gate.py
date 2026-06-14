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

manifest_path = ROOT / "tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json"
doc_path = ROOT / "docs/driverkit/provisioning-entitlement-hardblock-gate.md"
phase60l_manifest = ROOT / "tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json"
phase60k_manifest = ROOT / "tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json"

manifest = read_json(manifest_path)
phase60l = read_json(phase60l_manifest)
phase60k = read_json(phase60k_manifest)

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("phase60l_manifest_exists", phase60l_manifest),
    ("phase60k_manifest_exists", phase60k_manifest),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.provisioning_entitlement_hardblock_gate.v1"), "manifest schema")
add(checks, "phase60l_schema", bool(phase60l and phase60l.get("schema") == "h1mekartx.real_driverkit_dext_build_gate.v1"), "phase60l schema")
add(checks, "phase60k_schema", bool(phase60k and phase60k.get("schema") == "h1mekartx.validationfailed_root_cause_gate.v1"), "phase60k schema")

for field in [
    "provisioning_entitlement_hardblock_gate_ready",
    "paid_developer_team_required",
    "personal_team_blocked",
    "driverkit_entitlement_approval_required",
    "system_extension_capability_required",
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

doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
for token in [
    "Please enable Driverkit",
    "Personal development teams do not support the System Extension capability",
    "paid Apple Developer Program",
    "DriverKit entitlement approval",
    "System Extension capability",
    "PCI transport entitlement",
    "provider open remains blocked",
    "GPU command submission",
    "Dock/transparency/blur",
]:
    add(checks, "doc_contains_" + token.replace(" ", "_").replace("/", "_"), token in doc, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_PROVISIONING_ENTITLEMENT_HARDBLOCK_GATE_READY" if failed == 0 else "FAIL_PROVISIONING_ENTITLEMENT_HARDBLOCK_GATE"

report = {
    "schema": "h1mekartx.provisioning_entitlement_hardblock_gate_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "paid_developer_team_required": True,
    "personal_team_blocked": True,
    "driverkit_entitlement_approval_required": True,
    "system_extension_capability_required": True,
    "driverkit_pci_transport_entitlement_required": True,
    "host_profile_required": True,
    "dext_profile_required": True,
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

(OUT / "provisioning-entitlement-hardblock-gate-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
md = f"""# Provisioning Entitlement Hardblock Gate Check

- Decision: `{decision}`
- Paid Developer Team Required: `True`
- Personal Team Blocked: `True`
- DriverKit Entitlement Approval Required: `True`
- System Extension Capability Required: `True`
- DriverKit PCI Transport Entitlement Required: `True`
- Host Profile Required: `True`
- Dext Profile Required: `True`
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
(OUT / "provisioning-entitlement-hardblock-gate-check.md").write_text(md, encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
