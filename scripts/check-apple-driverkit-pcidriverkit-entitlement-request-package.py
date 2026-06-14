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

manifest_path = ROOT / "tools/hackintosh/apple-driverkit-pcidriverkit-entitlement-request-package.json"
doc_path = ROOT / "docs/hackintosh/apple-driverkit-pcidriverkit-entitlement-request-package.md"
draft_path = ROOT / "docs/hackintosh/apple-entitlement-request-draft.md"
phase62a_path = ROOT / "tools/hackintosh/rtx5070-accelerated-bringup-critical-path-gate.json"

manifest = read_json(manifest_path)
phase62a = read_json(phase62a_path)
doc = doc_path.read_text(encoding="utf-8", errors="replace") if doc_path.exists() else ""
draft = draft_path.read_text(encoding="utf-8", errors="replace") if draft_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("draft_exists", draft_path),
    ("phase62a_manifest_exists", phase62a_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.apple_driverkit_pcidriverkit_entitlement_request_package.v1"), "schema")
if phase62a:
    add(checks, "phase62a_schema_if_present", phase62a.get("schema") == "h1mekartx.rtx5070_accelerated_bringup_critical_path_gate.v1", "phase62a schema")
else:
    add(checks, "phase62a_schema_if_present", True, "phase62a absent; request package remains valid")

for field in [
    "rtx5070_target_retained",
    "entitlement_package_not_hardware_access",
    "apple_developer_program_required",
]:
    add(checks, f"{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "submission_to_apple_performed_by_this_phase",
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
    "phase62c_allowed_now",
    "provider_open_attempted",
    "ioserviceopen_attempted",
    "bar_mapping_attempted",
    "bar_mmio_mutation_attempted",
    "configuration_writes_attempted",
    "gpu_command_submission_attempted",
    "framebuffer_init_attempted",
    "display_engine_init_attempted",
    "ui_compositor_proof_claimed",
    "metal_proof_claimed",
]:
    add(checks, f"{field}_false", bool(manifest and manifest.get(field) is False), field)

for key, value in [
    ("apple_developer_program_official_annual_fee_usd", 99),
    ("apple_team_id_placeholder", "<APPLE_TEAM_ID>"),
    ("host_bundle_id", "dev.h1meka.H1mekaRTXHost"),
    ("driver_bundle_id", "dev.h1meka.H1mekaRTXDriver"),
    ("rtx5070_vendor_id", "0x10de"),
    ("rtx5070_device_id", "0x2f04"),
    ("rtx5070_iopcimatch", "0x2f0410de"),
    ("rtx5070_subsystem_vendor_id", "0x1458"),
    ("rtx5070_subsystem_id", "0x417e"),
    ("next_gate", "phase62c-local-entitlement-request-status-collector"),
]:
    add(checks, f"{key}_recorded", bool(manifest and manifest.get(key) == value), f"{key}={value}")

for capability in [
    "DriverKit",
    "PCIDriverKit PCI transport",
    "System Extension",
    "DriverKit communicates with drivers",
]:
    add(checks, f"requested_capability_{capability}", bool(manifest and capability in manifest.get("requested_capabilities", [])), capability)
    add(checks, f"doc_mentions_{capability}", capability in doc or capability in draft, capability)

for token in [
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "0x1458",
    "0x417e",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "<APPLE_TEAM_ID>",
    "BAR/MMIO writes",
    "PCI configuration writes",
    "GPU command submission",
    "Metal acceleration claims",
    "Dock/transparency/blur acceleration claims",
]:
    add(checks, "request_text_contains_" + token.replace("/", "_").replace(" ", "_"), token in doc and token in draft, token)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_APPLE_DRIVERKIT_PCIDRIVERKIT_ENTITLEMENT_REQUEST_PACKAGE_READY" if failed == 0 else "FAIL_APPLE_DRIVERKIT_PCIDRIVERKIT_ENTITLEMENT_REQUEST_PACKAGE"

report = {
    "schema": "h1mekartx.apple_driverkit_pcidriverkit_entitlement_request_package_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "entitlement_package_not_hardware_access": True,
    "apple_developer_program_required": True,
    "submission_to_apple_performed_by_this_phase": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "ui_compositor_proof_claimed": False,
    "metal_proof_claimed": False,
    "next_gate": "phase62c-local-entitlement-request-status-collector",
    "checks": checks,
}

(OUT / "apple-driverkit-pcidriverkit-entitlement-request-package-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "apple-driverkit-pcidriverkit-entitlement-request-package-check.md").write_text(f"""# Apple DriverKit / PCIDriverKit Entitlement Request Package Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Entitlement Package Not Hardware Access: `True`
- Apple Developer Program Required: `True`
- Submission To Apple Performed By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase62c-local-entitlement-request-status-collector`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
