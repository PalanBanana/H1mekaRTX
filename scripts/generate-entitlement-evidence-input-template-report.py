#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.entitlement_evidence_input_template_report.v1"

TEMPLATE_PATH = "evidence-templates/entitlement-evidence.sample.json"

REQUIRED_EVIDENCE_KEYS = [
    "apple_developer_program_membership_status",
    "team_identifier_redacted",
    "host_app_bundle_identifier_redacted",
    "driver_extension_bundle_identifier_redacted",
    "driverkit_entitlement_request_status",
    "driverkit_entitlement_group_status",
    "device_interface_scope_status",
    "extension_install_entitlement_status",
    "driverkit_development_profile_status",
    "distribution_signing_path_status",
    "notarization_path_status",
    "local_research_scope_acknowledged",
    "metal_injection_goal",
    "metal_injection_runtime_allowed_now",
    "rtx5070_metal_runtime_allowed",
]


def load_template(root: Path) -> dict[str, Any]:
    path = root / TEMPLATE_PATH
    return json.loads(path.read_text())


def build_report(root: Path) -> dict[str, Any]:
    template = load_template(root)
    evidence = template.get("evidence", {})
    if not isinstance(evidence, dict):
        evidence = {}

    missing_keys = [key for key in REQUIRED_EVIDENCE_KEYS if key not in evidence]

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "template_path": TEMPLATE_PATH,
        "template_schema": template.get("schema"),
        "decision": "ENTITLEMENT_EVIDENCE_INPUT_TEMPLATE_READY" if not missing_keys else "FAIL_ENTITLEMENT_EVIDENCE_INPUT_TEMPLATE",
        "plain_answer": "A redacted entitlement evidence input template is available. Runtime work remains blocked until real evidence is provided and validated.",
        "goal": "RTX 5070 Metal full graphics acceleration research path",
        "template_ready": not missing_keys,
        "redaction_required": template.get("redaction_required") is True,
        "missing_evidence_keys": missing_keys,
        "required_evidence_keys": REQUIRED_EVIDENCE_KEYS,
        "default_status": "NOT_PROVIDED",
        "evidence_runtime_summary": {
            "local_research_scope_acknowledged": evidence.get("local_research_scope_acknowledged"),
            "metal_injection_goal": evidence.get("metal_injection_goal"),
            "metal_injection_runtime_allowed_now": evidence.get("metal_injection_runtime_allowed_now"),
            "rtx5070_metal_runtime_allowed": evidence.get("rtx5070_metal_runtime_allowed")
        },
        "runtime_allowed_after_template": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 68 should add an entitlement evidence resolver that reads a redacted evidence file and emits GO/NO-GO without starting runtime work.",
        "safety_boundary": {
            "read_only": True,
            "evidence_template_only": True,
            "redacted_inputs_only": True,
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
    key_rows = [f"- `{key}`" for key in data["required_evidence_keys"]]

    return "\n".join(
        [
            "# Entitlement Evidence Input Template Report",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Goal: {data['goal']}",
            "",
            f"Template path: `{data['template_path']}`",
            "",
            f"Template ready: `{data['template_ready']}`",
            "",
            f"Redaction required: `{data['redaction_required']}`",
            "",
            f"Runtime allowed after template: `{data['runtime_allowed_after_template']}`",
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
            "## Required Evidence Keys",
            "",
            *key_rows,
            "",
            "## Safety Boundary",
            "",
            "This stage adds a redacted evidence input template only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate entitlement evidence input template report.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_report(root)

    json_path = out_dir / "entitlement-evidence-input-template-report.json"
    md_path = out_dir / "entitlement-evidence-input-template-report.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0 if data["template_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
