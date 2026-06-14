#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "release-readiness"
OUT.mkdir(parents=True, exist_ok=True)

FORBIDDEN_PATTERNS = {
    "home_path": re.compile(r"/Users/[^/\s\"'`]+"),
    "tmp_path": re.compile(r"/private/var/folders/[^\s\"'`]+|/var/folders/[^\s\"'`]+"),
    "email_like": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "team_id_label": re.compile(r"Team ID:|Apple ID|APPLE_ID", re.IGNORECASE),
}

def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def add(checks, name, ok, detail=""):
    checks.append({"name": name, "passed": bool(ok), "detail": detail})

manifest_path = ROOT / "tools/hackintosh/local-entitlement-request-status-collector.json"
doc_path = ROOT / "docs/hackintosh/local-entitlement-request-status-collector.md"
collector_path = ROOT / "scripts/collect-local-entitlement-request-status.py"
summary_json = OUT / "local-entitlement-request-status-summary.json"
summary_md = OUT / "local-entitlement-request-status-summary.md"
package_path = ROOT / "tools/hackintosh/apple-driverkit-pcidriverkit-entitlement-request-package.json"

manifest = read_json(manifest_path)
summary = read_json(summary_json)
package = read_json(package_path)
collector_text = collector_path.read_text(encoding="utf-8", errors="replace") if collector_path.exists() else ""

checks = []

for name, path in [
    ("manifest_exists", manifest_path),
    ("doc_exists", doc_path),
    ("collector_exists", collector_path),
    ("summary_json_exists", summary_json),
    ("summary_md_exists", summary_md),
    ("package_manifest_exists", package_path),
]:
    add(checks, name, path.exists(), str(path))

add(checks, "manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.local_entitlement_request_status_collector.v1"), "schema")
add(checks, "summary_schema", bool(summary and summary.get("schema") == "h1mekartx.local_entitlement_request_status_summary.v1"), "schema")
if package:
    add(checks, "package_schema_if_present", package.get("schema") == "h1mekartx.apple_driverkit_pcidriverkit_entitlement_request_package.v1", "package schema")
else:
    add(checks, "package_schema_if_present", True, "package absent; status collector remains valid")

for field in [
    "local_entitlement_request_status_collector_ready",
    "entitlement_status_only",
    "rtx5070_target_retained",
    "raw_outputs_local_only",
]:
    add(checks, f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field)

for field in [
    "fallback_gpu_substitution_allowed",
    "apple_private_data_committed",
    "apple_team_id_value_committed",
    "apple_email_committed",
    "submission_to_apple_performed_by_this_phase",
    "provider_match_attempted_by_this_phase",
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
    "current_rtx5070_metal_acceleration_claimed",
    "current_rtx5070_ui_smoothness_claimed",
]:
    add(checks, f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field)
    add(checks, f"summary_{field}_false", bool(summary and summary.get(field) is False), field)

for field in [
    "apple_developer_program_active",
    "apple_team_id_available",
    "driverkit_entitlement_request_submitted",
    "pcidriverkit_transport_entitlement_request_submitted",
    "system_extension_capability_requested",
    "host_app_id_configured",
    "driver_app_id_configured",
    "driverkit_entitlement_approved",
    "pcidriverkit_transport_entitlement_approved",
    "system_extension_capability_approved",
    "provisioning_profiles_regenerated_after_approval",
]:
    add(checks, f"required_ready_field_{field}", bool(manifest and field in manifest.get("required_ready_fields", [])), field)
    add(checks, f"summary_records_{field}", bool(summary and field in summary), field)
    add(checks, f"collector_template_has_{field}", field in collector_text, field)

add(checks, "summary_ready_for_provider_match_recorded", bool(summary and "ready_for_provider_match" in summary), "ready flag")
add(checks, "summary_next_gate", bool(summary and summary.get("next_gate") == "phase62d-provider-match-readiness-gate"), "next gate")
add(checks, "manifest_next_gate", bool(manifest and manifest.get("next_gate") == "phase62d-provider-match-readiness-gate"), "next gate")

for path in [summary_json, summary_md]:
    text = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
    for name, pattern in FORBIDDEN_PATTERNS.items():
        add(checks, f"no_{name}_in_{path.name}", not pattern.search(text), name)

failed = sum(1 for c in checks if not c["passed"])
decision = "PASS_LOCAL_ENTITLEMENT_REQUEST_STATUS_COLLECTOR_READY" if failed == 0 else "FAIL_LOCAL_ENTITLEMENT_REQUEST_STATUS_COLLECTOR"

report = {
    "schema": "h1mekartx.local_entitlement_request_status_collector_check.v1",
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    "decision": decision,
    "rtx5070_target_retained": True,
    "fallback_gpu_substitution_allowed": False,
    "entitlement_status_only": True,
    "submission_to_apple_performed_by_this_phase": False,
    "provider_match_attempted_by_this_phase": False,
    "provider_open_attempted": False,
    "ioserviceopen_attempted": False,
    "bar_mapping_attempted": False,
    "gpu_command_submission_attempted": False,
    "current_rtx5070_metal_acceleration_claimed": False,
    "current_rtx5070_ui_smoothness_claimed": False,
    "next_gate": "phase62d-provider-match-readiness-gate",
    "checks": checks,
}

(OUT / "local-entitlement-request-status-collector-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
(OUT / "local-entitlement-request-status-collector-check.md").write_text(f"""# Local Entitlement Request Status Collector Check

- Decision: `{decision}`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Entitlement Status Only: `True`
- Submission To Apple Performed By This Phase: `False`
- Provider Match Attempted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Next Gate: `phase62d-provider-match-readiness-gate`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
""", encoding="utf-8")

print("Decision:", decision)
raise SystemExit(0 if failed == 0 else 1)
