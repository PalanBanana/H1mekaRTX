#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.signed_extension_packaging_plan_resolver.v1"

DEFAULT_PLAN = "packaging-plan/signed-extension-packaging-plan.sample.json"

REQUIRED_PLAN_KEYS = [
    "host_app_bundle_id_status",
    "driver_extension_bundle_id_status",
    "bundle_id_pairing_status",
    "driverkit_entitlement_status",
    "driverkit_development_profile_status",
    "extension_install_permission_status",
    "developer_certificate_status",
    "distribution_signing_status",
    "notarization_status",
    "manual_review_status",
]

ACCEPTED_READY_STATUSES = {
    "PROVIDED_REDACTED",
    "CONFIRMED_REDACTED",
    "APPROVED_REDACTED",
    "READY_FOR_MANUAL_REVIEW",
}

RUNTIME_FALSE_KEYS = [
    "metal_injection_runtime_allowed_now",
    "driver_runtime_allowed",
    "driver_installation_allowed",
    "driver_activation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "low_level_hardware_path_allowed",
    "rtx5070_metal_runtime_allowed",
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


def ready_status(value: Any) -> bool:
    return isinstance(value, str) and value in ACCEPTED_READY_STATUSES


def build_resolution(root: Path, plan_rel: str) -> dict[str, Any]:
    plan_path = (root / plan_rel).resolve()
    plan = load_json(plan_path)

    target = plan.get("target", {})
    packaging_plan = plan.get("packaging_plan", {})
    runtime_policy = plan.get("runtime_policy", {})

    if not isinstance(target, dict):
        target = {}
    if not isinstance(packaging_plan, dict):
        packaging_plan = {}
    if not isinstance(runtime_policy, dict):
        runtime_policy = {}

    missing_target_keys = [key for key in TARGET_KEYS if not target.get(key)]
    missing_plan_keys = [key for key in REQUIRED_PLAN_KEYS if key not in packaging_plan]

    not_ready_plan_keys = [
        key for key in REQUIRED_PLAN_KEYS
        if packaging_plan.get(key) in {"NOT_PROVIDED", "NOT_READY", None}
    ]

    invalid_ready_status_keys = [
        key for key in REQUIRED_PLAN_KEYS
        if key in packaging_plan and not ready_status(packaging_plan.get(key))
    ]

    runtime_claims_enabled = any(
        runtime_policy.get(key) is True
        for key in RUNTIME_FALSE_KEYS
    )

    metal_goal = runtime_policy.get("metal_injection_goal") is True

    blockers: list[str] = []
    blockers.extend(f"missing_target:{key}" for key in missing_target_keys)
    blockers.extend(f"missing_plan:{key}" for key in missing_plan_keys)
    blockers.extend(f"not_ready_plan:{key}" for key in not_ready_plan_keys)
    blockers.extend(f"invalid_ready_status:{key}" for key in invalid_ready_status_keys)

    if not metal_goal:
        blockers.append("missing_metal_goal_acknowledgement")

    if runtime_claims_enabled:
        blockers.append("packaging_plan_attempts_to_enable_runtime")

    packaging_ready_for_manual_review = len(blockers) == 0

    if packaging_ready_for_manual_review:
        gate = "GO_PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME"
        decision = "PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME"
        plain_answer = "Packaging evidence appears present for manual review, but runtime remains disabled."
    else:
        gate = "NO_GO_SIGNED_EXTENSION_PACKAGING_EVIDENCE_INCOMPLETE"
        decision = "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED"
        plain_answer = "Signed-extension packaging evidence is incomplete or unsafe, so runtime remains blocked."

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "plan_path": plan_rel,
        "plan_schema": plan.get("schema"),
        "target": target,
        "decision": decision,
        "gate": gate,
        "plain_answer": plain_answer,
        "packaging_ready_for_manual_review": packaging_ready_for_manual_review,
        "blockers": blockers,
        "missing_target_keys": missing_target_keys,
        "missing_plan_keys": missing_plan_keys,
        "not_ready_plan_keys": not_ready_plan_keys,
        "invalid_ready_status_keys": invalid_ready_status_keys,
        "required_plan_keys": REQUIRED_PLAN_KEYS,
        "accepted_ready_statuses": sorted(ACCEPTED_READY_STATUSES),
        "manual_review_only": True,
        "packaging_plan_only": True,
        "metal_injection_goal": metal_goal,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_packaging_resolver": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 74 should add packaging-plan resolver fixture matrix coverage while keeping runtime disabled.",
        "safety_boundary": {
            "read_only": True,
            "packaging_plan_resolution_only": True,
            "manual_review_only": True,
            "no_runtime": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_path": True,
            "no_rtx5070_metal_runtime": True
        }
    }


def markdown_report(data: dict[str, Any]) -> str:
    blocker_rows = [f"- `{item}`" for item in data["blockers"]] or ["- none"]
    required_rows = [f"- `{item}`" for item in data["required_plan_keys"]]

    return "\n".join(
        [
            "# Signed Extension Packaging Plan Resolver Report",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Gate: `{data['gate']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Plan path: `{data['plan_path']}`",
            "",
            f"Packaging ready for manual review: `{data['packaging_ready_for_manual_review']}`",
            "",
            f"Packaging plan only: `{data['packaging_plan_only']}`",
            "",
            f"Manual review only: `{data['manual_review_only']}`",
            "",
            f"Runtime allowed after packaging resolver: `{data['runtime_allowed_after_packaging_resolver']}`",
            "",
            f"Metal injection goal: `{data['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{data['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{data['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Required Plan Keys",
            "",
            *required_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage resolves packaging-plan evidence only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve signed-extension packaging plan into NOT_READY or MANUAL_REVIEW_ONLY.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--plan", default=DEFAULT_PLAN, help="Packaging plan JSON path relative to root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_resolution(root, args.plan)

    json_path = out_dir / "signed-extension-packaging-plan-resolver-report.json"
    md_path = out_dir / "signed-extension-packaging-plan-resolver-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")
    print(f"Gate: {data['gate']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
