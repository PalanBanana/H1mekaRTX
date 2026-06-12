#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.signed_extension_packaging_plan_static_contract.v1"

SAMPLE_PLAN = "packaging-plan/signed-extension-packaging-plan.sample.json"
READY_PLAN = "packaging-plan/signed-extension-packaging-plan.redacted-ready.fixture.json"

SOURCE_FILES = [
    SAMPLE_PLAN,
    READY_PLAN,
    "scripts/generate-signed-extension-packaging-plan-matrix.py",
    "scripts/check-signed-extension-packaging-plan-matrix.py",
    "docs/metal/signed-extension-packaging-plan-matrix.md",
]

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

ACCEPTED_READY_STATUSES = {
    "PROVIDED_REDACTED",
    "CONFIRMED_REDACTED",
    "APPROVED_REDACTED",
    "READY_FOR_MANUAL_REVIEW",
}

FORBIDDEN_SOURCE_TOKENS = [
    "".join(["activation", "Request(forExtensionWithIdentifier"]),
    "".join(["deactivation", "Request(forExtensionWithIdentifier"]),
    "".join([".", "submit", "Request"]),
    "".join(["OSSystem", "Extension", "Manager.shared"]),
    "".join(["OSSystem", "Extension", "Request"]),
    "".join(["IOPCI", "Device"]),
    "".join(["IOService", "GetMatchingServices"]),
    "".join(["Configuration", "Read"]),
    "".join(["Configuration", "Write"]),
    "".join(["Memory", "Read"]),
    "".join(["Memory", "Write"]),
    "".join(["map", "DeviceMemory"]),
    "".join(["Create", "MemoryMap"]),
    "".join(["sub", "process.run([\"", "io", "reg", "\""]),
    "".join(["sub", "process.run([\"", "system", "_", "profiler", "\""]),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="replace")
    except FileNotFoundError:
        return ""


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def runtime_policy_is_disabled(runtime_policy: dict[str, Any]) -> bool:
    return (
        runtime_policy.get("metal_injection_goal") is True
        and all(runtime_policy.get(key) is False for key in RUNTIME_FALSE_KEYS)
    )


def evaluate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    packaging_plan = plan.get("packaging_plan", {})
    runtime_policy = plan.get("runtime_policy", {})

    if not isinstance(packaging_plan, dict):
        packaging_plan = {}
    if not isinstance(runtime_policy, dict):
        runtime_policy = {}

    missing_plan_keys = [key for key in REQUIRED_PLAN_KEYS if key not in packaging_plan]
    runtime_disabled = runtime_policy_is_disabled(runtime_policy)

    not_ready_statuses = [
        key for key in REQUIRED_PLAN_KEYS
        if packaging_plan.get(key) in {"NOT_PROVIDED", "NOT_READY", None}
    ]

    ready_statuses_invalid = [
        key for key in REQUIRED_PLAN_KEYS
        if packaging_plan.get(key) not in ACCEPTED_READY_STATUSES
    ]

    sample_style_not_ready = len(not_ready_statuses) > 0
    ready_style_complete = len(missing_plan_keys) == 0 and len(ready_statuses_invalid) == 0

    return {
        "schema": plan.get("schema"),
        "missing_plan_keys": missing_plan_keys,
        "not_ready_statuses": not_ready_statuses,
        "ready_statuses_invalid": ready_statuses_invalid,
        "sample_style_not_ready": sample_style_not_ready,
        "ready_style_complete": ready_style_complete,
        "runtime_disabled": runtime_disabled,
        "metal_injection_goal": runtime_policy.get("metal_injection_goal") is True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_packaging_static_contract": False,
        "rtx5070_metal_runtime_allowed": False,
    }


def build_report(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    for rel in SOURCE_FILES:
        add_check(checks, f"source_exists:{rel}", (root / rel).exists(), "present" if (root / rel).exists() else "missing")

    source = "\n".join(read_text(root / rel) for rel in SOURCE_FILES)

    for token in FORBIDDEN_SOURCE_TOKENS:
        add_check(checks, f"forbidden_token_absent:{token}", token not in source, "absent" if token not in source else "present")

    sample_plan = load_json(root / SAMPLE_PLAN)
    ready_plan = load_json(root / READY_PLAN)

    sample_eval = evaluate_plan(sample_plan)
    ready_eval = evaluate_plan(ready_plan)

    add_check(checks, "sample_schema", sample_eval["schema"] == "h1mekartx.signed_extension_packaging_plan.v1", f"schema={sample_eval['schema']!r}")
    add_check(checks, "ready_schema", ready_eval["schema"] == "h1mekartx.signed_extension_packaging_plan.v1", f"schema={ready_eval['schema']!r}")

    add_check(checks, "sample_is_not_ready_style", sample_eval["sample_style_not_ready"] is True, f"value={sample_eval['sample_style_not_ready']!r}")
    add_check(checks, "sample_runtime_disabled", sample_eval["runtime_disabled"] is True, f"value={sample_eval['runtime_disabled']!r}")

    add_check(checks, "ready_is_complete_style", ready_eval["ready_style_complete"] is True, f"value={ready_eval['ready_style_complete']!r}")
    add_check(checks, "ready_runtime_disabled", ready_eval["runtime_disabled"] is True, f"value={ready_eval['runtime_disabled']!r}")
    add_check(checks, "ready_runtime_after_contract_false", ready_eval["runtime_allowed_after_packaging_static_contract"] is False, f"value={ready_eval['runtime_allowed_after_packaging_static_contract']!r}")

    passed_count = sum(1 for item in checks if item["passed"])
    failed_count = len(checks) - passed_count

    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "decision": "PASS_SIGNED_EXTENSION_PACKAGING_PLAN_STATIC_CONTRACT" if failed_count == 0 else "FAIL_SIGNED_EXTENSION_PACKAGING_PLAN_STATIC_CONTRACT",
        "passed_count": passed_count,
        "failed_count": failed_count,
        "checks": checks,
        "sample_plan": {
            "path": SAMPLE_PLAN,
            "expected_decision": "NOT_READY_SIGNED_EXTENSION_PACKAGING_EVIDENCE_REQUIRED",
            "sample_style_not_ready": sample_eval["sample_style_not_ready"],
            "runtime_disabled": sample_eval["runtime_disabled"],
        },
        "ready_plan": {
            "path": READY_PLAN,
            "expected_decision": "PACKAGING_EVIDENCE_PRESENT_FOR_MANUAL_REVIEW_NO_RUNTIME",
            "ready_style_complete": ready_eval["ready_style_complete"],
            "runtime_disabled": ready_eval["runtime_disabled"],
            "runtime_allowed_after_packaging_static_contract": False,
        },
        "static_contract_ready": failed_count == 0,
        "redacted_ready_packaging_fixture_added": True,
        "manual_review_only": True,
        "packaging_plan_only": True,
        "metal_injection_goal": True,
        "metal_injection_runtime_allowed_now": False,
        "runtime_allowed_after_packaging_static_contract": False,
        "live_system_queries_allowed": False,
        "runtime_buttons_enabled": False,
        "driver_runtime_allowed": False,
        "driver_installation_allowed": False,
        "driver_activation_allowed": False,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_path_allowed": False,
        "rtx5070_metal_runtime_allowed": False,
        "next_stage_recommendation": "Stage 73 should add a packaging-plan resolver that emits NOT_READY or MANUAL_REVIEW_ONLY without enabling runtime.",
        "safety_boundary": {
            "read_only": True,
            "static_contract_only": True,
            "packaging_plan_only": True,
            "redacted_fixture_only": True,
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


def markdown_report(report: dict[str, Any]) -> str:
    rows = []
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        detail = item["detail"].replace("|", "\\|")
        rows.append(f"| `{item['name']}` | {status} | {detail} |")

    return "\n".join(
        [
            "# Signed Extension Packaging Plan Static Contract Report",
            "",
            f"Generated UTC: `{report['generated_at_utc']}`",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Passed: `{report['passed_count']}`",
            "",
            f"Failed: `{report['failed_count']}`",
            "",
            f"Static contract ready: `{report['static_contract_ready']}`",
            "",
            f"Redacted-ready packaging fixture added: `{report['redacted_ready_packaging_fixture_added']}`",
            "",
            f"Packaging plan only: `{report['packaging_plan_only']}`",
            "",
            f"Manual review only: `{report['manual_review_only']}`",
            "",
            f"Runtime allowed after packaging static contract: `{report['runtime_allowed_after_packaging_static_contract']}`",
            "",
            f"Metal injection goal: `{report['metal_injection_goal']}`",
            "",
            f"Metal injection runtime allowed now: `{report['metal_injection_runtime_allowed_now']}`",
            "",
            f"RTX 5070 Metal runtime allowed: `{report['rtx5070_metal_runtime_allowed']}`",
            "",
            "## Sample Plan",
            "",
            f"- Path: `{report['sample_plan']['path']}`",
            f"- Expected decision: `{report['sample_plan']['expected_decision']}`",
            f"- Runtime disabled: `{report['sample_plan']['runtime_disabled']}`",
            "",
            "## Ready Plan",
            "",
            f"- Path: `{report['ready_plan']['path']}`",
            f"- Expected decision: `{report['ready_plan']['expected_decision']}`",
            f"- Runtime disabled: `{report['ready_plan']['runtime_disabled']}`",
            f"- Runtime allowed after contract: `{report['ready_plan']['runtime_allowed_after_packaging_static_contract']}`",
            "",
            "## Checks",
            "",
            "| Check | Status | Detail |",
            "| --- | --- | --- |",
            *rows,
            "",
            "## Safety Boundary",
            "",
            "This stage validates the signed-extension packaging plan static contract and redacted-ready fixture only. It adds no driver installation, no driver activation, no provider transition, no device ownership transition, no hardware-path code, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            report["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate signed extension packaging plan static contract.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Repository root does not exist: {root}")

    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(root)

    json_path = out_dir / "signed-extension-packaging-plan-static-contract-report.json"
    md_path = out_dir / "signed-extension-packaging-plan-static-contract-report.md"

    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(report) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {report['decision']}")

    return 0 if report["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
