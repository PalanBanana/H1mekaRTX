#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_resolver.v1"

DEFAULT_EVIDENCE = "evidence-templates/entitlement-evidence.sample.json"

ACCEPTED_STATUSES = {
    "PROVIDED_REDACTED",
    "APPROVED_REDACTED",
    "CONFIRMED_REDACTED",
}

REQUIRED_STATUS_KEYS = [
    "apple_developer_program_membership_status",
    "driverkit_entitlement_request_status",
    "driverkit_entitlement_group_status",
    "device_interface_scope_status",
    "extension_install_entitlement_status",
    "driverkit_development_profile_status",
    "distribution_signing_path_status",
    "notarization_path_status",
]

REQUIRED_REDACTED_KEYS = [
    "team_identifier_redacted",
    "host_app_bundle_identifier_redacted",
    "driver_extension_bundle_identifier_redacted",
]

TARGET_KEYS = [
    "gpu",
    "vendor_id",
    "device_id",
    "iopcimatch",
    "subsystem_vendor_id",
    "subsystem_id",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def status_ok(value: Any) -> bool:
    return isinstance(value, str) and value in ACCEPTED_STATUSES


def redacted_ok(value: Any) -> bool:
    return isinstance(value, str) and value not in {
        "",
        "REDACTED_OR_NOT_PROVIDED",
        "NOT_PROVIDED",
    }


def build_resolution(root: Path, evidence_rel: str) -> dict[str, Any]:
    evidence_path = (root / evidence_rel).resolve()
    data = load_json(evidence_path)

    target = data.get("target", {})
    evidence = data.get("evidence", {})

    if not isinstance(target, dict):
        target = {}
    if not isinstance(evidence, dict):
        evidence = {}

    missing_status_keys = [
        key for key in REQUIRED_STATUS_KEYS
        if not status_ok(evidence.get(key))
    ]

    missing_redacted_keys = [
        key for key in REQUIRED_REDACTED_KEYS
        if not redacted_ok(evidence.get(key))
    ]

    missing_target_keys = [
        key for key in TARGET_KEYS
        if not target.get(key)
    ]

    local_scope_ack = evidence.get("local_research_scope_acknowledged") is True
    metal_goal = evidence.get("metal_injection_goal") is True
    evidence_claims_runtime = evidence.get("metal_injection_runtime_allowed_now") is True or evidence.get("rtx5070_metal_runtime_allowed") is True

    blockers = []
    blockers.extend(f"missing_status:{key}" for key in missing_status_keys)
    blockers.extend(f"missing_redacted:{key}" for key in missing_redacted_keys)
    blockers.extend(f"missing_target:{key}" for key in missing_target_keys)

    if not local_scope_ack:
        blockers.append("missing_local_research_scope_acknowledgement")

    if not metal_goal:
        blockers.append("missing_metal_goal_acknowledgement")

    if evidence_claims_runtime:
        blockers.append("evidence_file_attempts_to_enable_runtime")

    evidence_ready_for_review = len(blockers) == 0

    if evidence_ready_for_review:
        gate = "GO_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME"
        decision = "EVIDENCE_PRESENT_RUNTIME_STILL_DISABLED"
    else:
        gate = "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE"
        decision = "NO_GO_ENTITLEMENT_EVIDENCE_INCOMPLETE"

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "evidence_path": evidence_rel,
        "evidence_schema": data.get("schema"),
        "redaction_required": data.get("redaction_required") is True,
        "target": target,
        "decision": decision,
        "gate": gate,
        "plain_answer": "The redacted evidence file is incomplete, so RTX 5070 Metal runtime remains blocked." if not evidence_ready_for_review else "Evidence appears present for manual review, but runtime remains blocked by separate safety gates.",
        "evidence_ready_for_review": evidence_ready_for_review,
        "blockers": blockers,
        "missing_status_keys": missing_status_keys,
        "missing_redacted_keys": missing_redacted_keys,
        "missing_target_keys": missing_target_keys,
        "local_research_scope_acknowledged": local_scope_ack,
        "metal_injection_goal": metal_goal,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_resolver": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "required_status_keys": REQUIRED_STATUS_KEYS,
        "required_redacted_keys": REQUIRED_REDACTED_KEYS,
        "accepted_statuses": sorted(ACCEPTED_STATUSES),
        "next_stage_recommendation": "Stage 69 should add a resolver static contract checker and a redacted-ready fixture that still keeps runtime disabled.",
        "safety_boundary": {
            "read_only": True,
            "redacted_evidence_resolution_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    blocker_rows = [f"- `{item}`" for item in data["blockers"]] or ["- none"]
    status_rows = [f"- `{item}`" for item in data["required_status_keys"]]
    redacted_rows = [f"- `{item}`" for item in data["required_redacted_keys"]]

    return "\n".join(
        [
            "# Entitlement Evidence Resolver Report",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Gate: `{data['gate']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Evidence path: `{data['evidence_path']}`",
            "",
            f"Evidence ready for review: `{data['evidence_ready_for_review']}`",
            "",
            f"Runtime allowed after resolver: `{data['runtime_allowed_after_resolver']}`",
            "",
            f"Metal injection goal: `{data['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{data['metal_injection_runtime_allowed_now']}`",
            "",
            f"Driver runtime allowed: `{data['driver_runtime_allowed']}`",
            "",
            f"Driver installation allowed: `{data['driver_installation_allowed']}`",
            "",
            f"Driver activation allowed: `{data['driver_activation_allowed']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Low-level hardware path allowed: `{data['low_level_hardware_path_allowed']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{data['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Required Status Keys",
            "",
            *status_rows,
            "",
            "## Required Redacted Keys",
            "",
            *redacted_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage resolves redacted entitlement evidence only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve redacted entitlement evidence into GO/NO-GO.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--evidence", default=DEFAULT_EVIDENCE, help="Redacted evidence JSON path relative to root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_resolution(root, args.evidence)

    json_path = out_dir / "entitlement-evidence-resolver-report.json"
    md_path = out_dir / "entitlement-evidence-resolver-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    print(f"Gate: {data['gate']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
