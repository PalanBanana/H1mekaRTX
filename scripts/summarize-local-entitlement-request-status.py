#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_entitlement_request_status_summary.v1"

PRIVATE_PATTERNS = [
    re.compile(r"/Users/[^/\s\"'`]+(?:/[^\s\"'`]*)?"),
    re.compile(r"/private/var/folders/[^\s\"'`]+"),
    re.compile(r"/var/folders/[^\s\"'`]+"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    re.compile(r"[A-Fa-f0-9]{40,64}"),
    re.compile(r"TEAMID|Team ID:|Apple ID|APPLE_ID", re.IGNORECASE),
]

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        return None

def has_private_text(text: str) -> bool:
    return any(p.search(str(text or "")) for p in PRIVATE_PATTERNS)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-entitlement-request-status/local-entitlement-request-status-report.json")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = root / args.input
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    local = read_json(input_path)
    status = local.get("status", {}) if local else {}

    private_raw_detected = has_private_text(json.dumps(local or {}, sort_keys=True))

    summary = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_LOCAL_ENTITLEMENT_REQUEST_STATUS_COLLECTOR",
        "summary_only": True,
        "host_report_bundle_local_only": True,
        "local_status_report_present": local is not None,
        "local_status_decision": local.get("decision") if local else "NO_LOCAL_STATUS_REPORT_PRESENT",
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "entitlement_status_only": True,
        "ready_for_provider_match": bool(local and local.get("ready_for_provider_match")),
        "missing_ready_field_count": len(local.get("missing_ready_fields", [])) if local else 0,
        "missing_ready_fields": local.get("missing_ready_fields", []) if local else [],
        "apple_developer_program_active": bool(status.get("apple_developer_program_active", False)),
        "apple_team_id_available": bool(status.get("apple_team_id_available", False)),
        "driverkit_entitlement_request_submitted": bool(status.get("driverkit_entitlement_request_submitted", False)),
        "pcidriverkit_transport_entitlement_request_submitted": bool(status.get("pcidriverkit_transport_entitlement_request_submitted", False)),
        "system_extension_capability_requested": bool(status.get("system_extension_capability_requested", False)),
        "host_app_id_configured": bool(status.get("host_app_id_configured", False)),
        "driver_app_id_configured": bool(status.get("driver_app_id_configured", False)),
        "driverkit_entitlement_approved": bool(status.get("driverkit_entitlement_approved", False)),
        "pcidriverkit_transport_entitlement_approved": bool(status.get("pcidriverkit_transport_entitlement_approved", False)),
        "system_extension_capability_approved": bool(status.get("system_extension_capability_approved", False)),
        "provisioning_profiles_regenerated_after_approval": bool(status.get("provisioning_profiles_regenerated_after_approval", False)),
        "apple_request_case_id_available": bool(status.get("apple_request_case_id_available", False)),
        "apple_response_received": bool(status.get("apple_response_received", False)),
        "apple_response_requires_more_info": bool(status.get("apple_response_requires_more_info", False)),
        "apple_private_data_committed": False,
        "apple_team_id_value_committed": False,
        "apple_email_committed": False,
        "private_raw_detected_locally": private_raw_detected,
        "private_text_committed": False,
        "submission_to_apple_performed_by_this_phase": False,
        "provider_match_attempted_by_this_phase": False,
        "provider_open_attempted": False,
        "ioserviceopen_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "configuration_writes_attempted": False,
        "gpu_command_submission_attempted": False,
        "framebuffer_init_attempted": False,
        "display_engine_init_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "current_rtx5070_metal_acceleration_claimed": False,
        "current_rtx5070_ui_smoothness_claimed": False,
        "next_gate": "phase62d-provider-match-readiness-gate",
    }

    json_path = out_dir / "local-entitlement-request-status-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{k}` | `{v}` |" for k, v in summary.items() if k not in ["schema", "generated_at_utc", "missing_ready_fields"])
    missing = "\n".join(f"- `{x}`" for x in summary["missing_ready_fields"]) or "- none"

    md = f"""# Local Entitlement Request Status Summary

- Generated At UTC: `{summary['generated_at_utc']}`
- Summary Only: `True`
- Host Report Bundle Local Only: `True`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Entitlement Status Only: `True`
- Ready For Provider Match: `{summary['ready_for_provider_match']}`
- Missing Ready Field Count: `{summary['missing_ready_field_count']}`
- Submission To Apple Performed By This Phase: `False`
- Provider Match Attempted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Next Gate: `phase62d-provider-match-readiness-gate`

## Missing Ready Fields

{missing}

## Summary

| Key | Value |
| --- | --- |
{rows}
"""
    (out_dir / "local-entitlement-request-status-summary.md").write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {out_dir / 'local-entitlement-request-status-summary.md'}")
    print("Decision: PASS_LOCAL_ENTITLEMENT_REQUEST_STATUS_SUMMARY_WRITTEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
