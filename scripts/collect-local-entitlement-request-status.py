#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.local_entitlement_request_status_report.v1"

REQUIRED_READY_FIELDS = [
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
]

OPTIONAL_FIELDS = [
    "apple_request_case_id_available",
    "apple_response_received",
    "apple_response_requires_more_info",
]

def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except Exception:
        return None

def template() -> dict:
    data = {k: False for k in REQUIRED_READY_FIELDS}
    for k in OPTIONAL_FIELDS:
        data[k] = False
    data["notes_local_only"] = "Set booleans only. Do not put Apple ID, email, Team ID value, private path, or screenshots here."
    return data

def sanitize_bool_map(data: dict | None) -> dict:
    out = {}
    data = data or {}
    for k in REQUIRED_READY_FIELDS + OPTIONAL_FIELDS:
        out[k] = bool(data.get(k, False))
    return out

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--input", default="host-report-bundle/local-entitlement-request-status/status-input.json")
    parser.add_argument("--out-dir", default="host-report-bundle/local-entitlement-request-status")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    input_path = root / args.input
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        write_json(input_path, template())

    local_input = read_json(input_path)
    status = sanitize_bool_map(local_input)

    ready_for_provider_match = all(status[k] for k in REQUIRED_READY_FIELDS)
    missing_ready_fields = [k for k in REQUIRED_READY_FIELDS if not status[k]]

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "PASS_LOCAL_ENTITLEMENT_REQUEST_STATUS_CAPTURED",
        "classification": "CLASSIFICATION_LOCAL_ENTITLEMENT_REQUEST_STATUS_COLLECTOR",
        "host_report_bundle_local_only": True,
        "input_template_created_if_missing": True,
        "local_input_present": input_path.exists(),
        "rtx5070_target_retained": True,
        "fallback_gpu_substitution_allowed": False,
        "entitlement_status_only": True,
        "ready_for_provider_match": ready_for_provider_match,
        "missing_ready_fields": missing_ready_fields,
        "status": status,
        "apple_private_data_committed": False,
        "apple_team_id_value_committed": False,
        "apple_email_committed": False,
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

    write_json(out_dir / "local-entitlement-request-status-report.json", report)
    print("Decision: PASS_LOCAL_ENTITLEMENT_REQUEST_STATUS_CAPTURED")
    print("ready_for_provider_match =", ready_for_provider_match)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
