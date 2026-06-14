#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.manual_activation_approval_readiness_gate_check.v1"

REQUIRED_BEFORE_SUBMIT = [
    "signed host app exists",
    "signed dext exists",
    "host app contains the dext under Contents/Library/SystemExtensions",
    "entitlements are valid",
    "DriverKit entitlement is approved",
    "PCI transport entitlement is approved",
    "rollback/deactivation command is available",
    "disposable test environment is confirmed",
    "no provider-open path is enabled",
    "no BAR mapping path is enabled",
    "no GPU command submission path is enabled",
]

REQUIRED_DOCK_TIMING = [
    "signed host+dext packaging proof",
    "manual user-approved activation proof",
    "manual deactivation/rollback proof",
    "dext load proof",
    "provider match proof",
    "safe provider-open proof",
    "real GPU command execution proof",
    "RTX 5070 workload attribution proof",
    "WindowServer/Core Animation/QuartzCore/Metal compositor attribution proof",
    "before/after UI frame pacing and latency measurement proof",
    "Dock/transparency/blur scenario proof",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools/driverkit-buildable-scaffold/manual-activation-approval-readiness-gate.json"
    doc_path = root / "docs/driverkit/manual-activation-approval-readiness-gate.md"
    phase46_manifest_path = root / "tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json"
    host_swift_path = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift"

    manifest = read_json(manifest_path)
    phase46 = read_json(phase46_manifest_path)
    host_text = host_swift_path.read_text(encoding="utf-8", errors="replace") if host_swift_path.exists() else ""

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase46_manifest_exists", phase46_manifest_path.exists(), str(phase46_manifest_path)),
        make_check("host_swift_exists", host_swift_path.exists(), str(host_swift_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.manual_activation_approval_readiness_gate.v1"), "manifest schema"),
        make_check("phase46_schema", bool(phase46 and phase46.get("schema") == "h1mekartx.user_approved_system_extension_activation_path.v1"), "phase46 schema"),
        make_check("activation_path_present", "activationRequest(forExtensionWithIdentifier:" in host_text, "activation request"),
        make_check("deactivation_path_present", "deactivationRequest(forExtensionWithIdentifier:" in host_text, "deactivation request"),
        make_check("manual_submit_activation_flag_present", "--submit-activation" in host_text, "--submit-activation"),
        make_check("manual_submit_deactivation_flag_present", "--submit-deactivation" in host_text, "--submit-deactivation"),
    ]

    for field in [
        "manual_activation_approval_readiness_gate_ready",
        "user_will_approve_future_local_prompt",
        "manual_approval_allowed_for_future_local_test",
        "auto_approval_not_possible",
        "user_must_approve_in_system_settings_if_prompted",
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    for field in [
        "submit_activation_allowed_now",
        "submit_deactivation_allowed_now",
        "ci_activation_attempted",
        "ci_deactivation_attempted",
        "system_extension_activation_attempted",
        "system_extension_deactivation_attempted",
        "dext_load_attempted",
        "provider_open_attempted",
        "bar_mapping_attempted",
        "bar_mmio_mutation_attempted",
        "configuration_writes_attempted",
        "gpu_command_submission_attempted",
        "ui_compositor_proof_claimed",
        "metal_proof_claimed",
    ]:
        checks.append(make_check(f"manifest_{field}_false", bool(manifest and manifest.get(field) is False), field))

    before_submit = "\n".join(manifest.get("required_before_submit_mode", []) if manifest else [])
    for item in REQUIRED_BEFORE_SUBMIT:
        checks.append(make_check("before_submit_contains_" + item.replace(" ", "_").replace("/", "_"), item in before_submit, item))

    dock_timing = "\n".join(manifest.get("dock_transparency_blur_timing", []) if manifest else [])
    for item in REQUIRED_DOCK_TIMING:
        checks.append(make_check("dock_timing_contains_" + item.replace(" ", "_").replace("/", "_"), item in dock_timing, item))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_MANUAL_ACTIVATION_APPROVAL_READINESS_GATE_READY" if failed == 0 else "FAIL_MANUAL_ACTIVATION_APPROVAL_READINESS_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_MANUAL_ACTIVATION_APPROVAL_READINESS_GATE",
        "user_will_approve_future_local_prompt": True,
        "manual_approval_allowed_for_future_local_test": True,
        "submit_activation_allowed_now": False,
        "submit_deactivation_allowed_now": False,
        "ci_activation_attempted": False,
        "ci_deactivation_attempted": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "dock_transparency_blur_next_after": manifest.get("dock_transparency_blur_timing", []) if manifest else [],
        "checks": checks,
    }

    json_path = out_dir / "manual-activation-approval-readiness-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check_rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    timing_rows = "\n".join(f"| {idx + 1} | {item} |" for idx, item in enumerate(report["dock_transparency_blur_next_after"]))

    md = f"""# Manual Activation Approval Readiness Gate Check

- Decision: `{decision}`
- User Will Approve Future Local Prompt: `True`
- Manual Approval Allowed For Future Local Test: `True`
- Submit Activation Allowed Now: `False`
- Submit Deactivation Allowed Now: `False`
- CI Activation Attempted: `False`
- CI Deactivation Attempted: `False`
- System Extension Activation Attempted: `False`
- System Extension Deactivation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Dock / Transparency / Blur Timing

| Step | Required Proof Before UI Claim |
| ---: | --- |
{timing_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{check_rows}
"""
    md_path = out_dir / "manual-activation-approval-readiness-gate-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
