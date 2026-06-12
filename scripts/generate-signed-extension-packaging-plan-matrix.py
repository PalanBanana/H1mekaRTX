#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.signed_extension_packaging_plan_matrix.v1"

PLAN_PATH = "packaging-plan/signed-extension-packaging-plan.sample.json"

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

REQUIRED_RUNTIME_KEYS = [
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "driver_runtime_allowed",
    "driver_installation_allowed",
    "driver_activation_allowed",
    "provider_attach_allowed",
    "device_ownership_allowed",
    "low_level_hardware_path_allowed",
    "rtx5070_metal_runtime_allowed",
]

MATRIX_ITEMS = [
    {
        "id": "host_app_bundle_id",
        "label": "Host app Bundle ID",
        "status_key": "host_app_bundle_id_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "driver_extension_bundle_id",
        "label": "Driver extension Bundle ID",
        "status_key": "driver_extension_bundle_id_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "bundle_pairing",
        "label": "Bundle ID pairing",
        "status_key": "bundle_id_pairing_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "driverkit_entitlement",
        "label": "DriverKit entitlement",
        "status_key": "driverkit_entitlement_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "driverkit_development_profile",
        "label": "DriverKit development profile",
        "status_key": "driverkit_development_profile_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "extension_install_permission",
        "label": "Extension install permission",
        "status_key": "extension_install_permission_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "developer_certificate",
        "label": "Developer certificate",
        "status_key": "developer_certificate_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "distribution_signing",
        "label": "Distribution signing",
        "status_key": "distribution_signing_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "notarization",
        "label": "Notarization",
        "status_key": "notarization_status",
        "required_before_runtime": True,
        "expected_status": "NOT_PROVIDED"
    },
    {
        "id": "manual_review",
        "label": "Manual review",
        "status_key": "manual_review_status",
        "required_before_runtime": True,
        "expected_status": "NOT_READY"
    }
]


def load_plan(root: Path) -> dict[str, Any]:
    return json.loads((root / PLAN_PATH).read_text())


def build_report(root: Path) -> dict[str, Any]:
    plan = load_plan(root)
    packaging_plan = plan.get("packaging_plan", {})
    runtime_policy = plan.get("runtime_policy", {})

    if not isinstance(packaging_plan, dict):
        packaging_plan = {}
    if not isinstance(runtime_policy, dict):
        runtime_policy = {}

    missing_plan_keys = [key for key in REQUIRED_PLAN_KEYS if key not in packaging_plan]
    missing_runtime_keys = [key for key in REQUIRED_RUNTIME_KEYS if key not in runtime_policy]

    matrix_rows = []
    blockers = []

    for item in MATRIX_ITEMS:
        status = packaging_plan.get(item["status_key"])
        ready = status not in {"NOT_PROVIDED", "NOT_READY", None}
        row = {
            "id": item["id"],
            "label": item["label"],
            "status_key": item["status_key"],
            "status": status,
            "required_before_runtime": item["required_before_runtime"],
            "ready": ready
        }
        matrix_rows.append(row)

        if item["required_before_runtime"] and not ready:
            blockers.append(f"packaging_not_ready:{item['id']}")

    runtime_claims_enabled = any(
        runtime_policy.get(key) is True
        for key in [
            "metal_injection_runtime_allowed_now",
            "driver_runtime_allowed",
            "driver_installation_allowed",
            "driver_activation_allowed",
            "provider_attach_allowed",
            "device_ownership_allowed",
            "low_level_hardware_path_allowed",
            "rtx5070_metal_runtime_allowed",
        ]
    )

    if runtime_claims_enabled:
        blockers.append("runtime_policy_attempts_to_enable_runtime")

    packaging_ready_for_review = (
        not missing_plan_keys
        and not missing_runtime_keys
        and not runtime_claims_enabled
        and len(blockers) == 0
    )

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "plan_path": PLAN_PATH,
        "plan_schema": plan.get("schema"),
        "decision": "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED",
        "plain_answer": "Signed host app and driver extension packaging is planned, but required evidence is not provided. Runtime remains disabled.",
        "goal": "RTX 5070 Metal full graphics acceleration research path",
        "packaging_plan_matrix_ready": True,
        "packaging_ready_for_review": packaging_ready_for_review,
        "missing_plan_keys": missing_plan_keys,
        "missing_runtime_keys": missing_runtime_keys,
        "blockers": blockers,
        "matrix_rows": matrix_rows,
        "manual_review_only": True,
        "metal_injection_goal": runtime_policy.get("metal_injection_goal") is True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_packaging_plan": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 72 should add a static contract checker for the signed-extension packaging plan matrix. Keep it packaging-plan-only and no-runtime.",
        "safety_boundary": {
            "read_only": True,
            "packaging_plan_only": True,
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
    rows = []
    for item in data["matrix_rows"]:
        rows.append(
            "| `{id}` | {status} | {ready} | {required} |".format(
                id=item["id"],
                status=item["status"],
                ready=item["ready"],
                required=item["required_before_runtime"]
            )
        )

    blocker_rows = [f"- `{item}`" for item in data["blockers"]] or ["- none"]

    return "\n".join(
        [
            "# Signed Extension Packaging Plan Matrix",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Goal: {data['goal']}",
            "",
            f"Plan path: `{data['plan_path']}`",
            "",
            f"Packaging plan matrix ready: `{data['packaging_plan_matrix_ready']}`",
            "",
            f"Packaging ready for review: `{data['packaging_ready_for_review']}`",
            "",
            f"Runtime allowed after packaging plan: `{data['runtime_allowed_after_packaging_plan']}`",
            "",
            f"Metal injection goal: `{data['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{data['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{data['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Matrix Rows",
            "",
            "| ID | Status | Ready | Required Before Runtime |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Blockers",
            "",
            *blocker_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a signed-extension packaging plan matrix only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate signed extension packaging plan matrix.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_report(root)

    json_path = out_dir / "signed-extension-packaging-plan-matrix-report.json"
    md_path = out_dir / "signed-extension-packaging-plan-matrix-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
