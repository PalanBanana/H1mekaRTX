#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.manual_activation_preflight_after_signed_verification_check.v1"

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

    manifest_path = root / "tools/driverkit-buildable-scaffold/manual-activation-preflight-after-signed-verification.json"
    doc_path = root / "docs/driverkit/manual-activation-preflight-after-signed-verification.md"

    signed_summary_path = root / "release-readiness/signed-artifact-verification-report-summary.json"
    phase55_path = root / "tools/driverkit-buildable-scaffold/signed-artifact-verification-report-sanitizer.json"
    phase54_path = root / "tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json"
    phase47_path = root / "tools/driverkit-buildable-scaffold/manual-activation-approval-readiness-gate.json"
    phase46_path = root / "tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json"

    manifest = read_json(manifest_path)
    signed_summary = read_json(signed_summary_path)
    phase55 = read_json(phase55_path)
    phase54 = read_json(phase54_path)
    phase47 = read_json(phase47_path)
    phase46 = read_json(phase46_path)

    boundary = signed_summary.get("boundary_summary", {}) if signed_summary else {}

    signed_artifact_verification_ok = bool(signed_summary and signed_summary.get("signed_artifact_verification_ok") is True)
    signed_package_created_locally = bool(signed_summary and signed_summary.get("signed_package_created_locally") is True)
    hard_optin_ok = bool(signed_summary and signed_summary.get("hard_optin_ok") is True)
    local_scope_ok = bool(signed_summary and signed_summary.get("local_scope_ok") is True)

    boundary_ok = bool(
        boundary.get("activation_still_blocked", True)
        and boundary.get("provider_open_still_blocked", True)
        and boundary.get("bar_mapping_still_blocked", True)
        and boundary.get("gpu_command_submission_still_blocked", True)
    )

    user_approval_allowed = bool(phase47 and phase47.get("manual_approval_allowed_for_future_local_test") is True)
    phase46_activation_path_exists = bool(phase46 and phase46.get("activation_capable_code_added") is True)

    activation_preflight_ready = bool(
        signed_artifact_verification_ok
        and signed_package_created_locally
        and hard_optin_ok
        and local_scope_ok
        and boundary_ok
        and user_approval_allowed
        and phase46_activation_path_exists
    )

    activation_block_reason = []
    if not signed_artifact_verification_ok:
        activation_block_reason.append("signed_artifact_verification_ok_false_or_missing")
    if not signed_package_created_locally:
        activation_block_reason.append("signed_package_created_locally_false_or_missing")
    if not hard_optin_ok:
        activation_block_reason.append("hard_optin_ok_false_or_missing")
    if not local_scope_ok:
        activation_block_reason.append("local_scope_ok_false_or_missing")
    if not boundary_ok:
        activation_block_reason.append("runtime_boundary_not_blocked_correctly")
    if not user_approval_allowed:
        activation_block_reason.append("user_approval_allowed_false_or_missing")
    if not phase46_activation_path_exists:
        activation_block_reason.append("phase46_activation_path_missing")

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("signed_summary_exists", signed_summary_path.exists(), str(signed_summary_path)),
        make_check("phase55_manifest_exists", phase55_path.exists(), str(phase55_path)),
        make_check("phase54_manifest_exists", phase54_path.exists(), str(phase54_path)),
        make_check("phase47_manifest_exists", phase47_path.exists(), str(phase47_path)),
        make_check("phase46_manifest_exists", phase46_path.exists(), str(phase46_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.manual_activation_preflight_after_signed_verification.v1"), "manifest schema"),
        make_check("phase55_schema", bool(phase55 and phase55.get("schema") == "h1mekartx.signed_artifact_verification_report_sanitizer.v1"), "phase55 schema"),
        make_check("phase54_schema", bool(phase54 and phase54.get("schema") == "h1mekartx.actual_local_signing_hard_optin.v1"), "phase54 schema"),
        make_check("phase47_user_approval_allowed", user_approval_allowed, "manual approval allowed"),
        make_check("phase46_activation_path_exists", phase46_activation_path_exists, "activation capable code"),
        make_check("signed_summary_schema", bool(signed_summary and signed_summary.get("schema") == "h1mekartx.signed_artifact_verification_report_summary.v1"), "signed summary schema"),
        make_check("boundary_activation_still_blocked", bool(boundary.get("activation_still_blocked", True)), "activation still blocked"),
        make_check("boundary_provider_open_still_blocked", bool(boundary.get("provider_open_still_blocked", True)), "provider open still blocked"),
        make_check("boundary_bar_mapping_still_blocked", bool(boundary.get("bar_mapping_still_blocked", True)), "bar mapping still blocked"),
        make_check("boundary_gpu_command_submission_still_blocked", bool(boundary.get("gpu_command_submission_still_blocked", True)), "gpu command still blocked"),
    ]

    for field in [
        "manual_activation_preflight_gate_ready",
        "preflight_gate_only",
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    for field in [
        "activation_allowed_now",
        "deactivation_allowed_now",
        "install_attempted",
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

    decision = "PASS_ACTIVATION_PREFLIGHT_READY" if activation_preflight_ready else "PASS_ACTIVATION_PREFLIGHT_BLOCKED_UNTIL_SIGNED_VERIFICATION"
    failed = sum(1 for c in checks if not c["passed"])
    if failed:
        decision = "FAIL_MANUAL_ACTIVATION_PREFLIGHT_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "classification": "CLASSIFICATION_MANUAL_ACTIVATION_PREFLIGHT_AFTER_SIGNED_VERIFICATION",
        "preflight_gate_only": True,
        "activation_preflight_ready": activation_preflight_ready,
        "activation_allowed_now": False,
        "deactivation_allowed_now": False,
        "activation_block_reason": activation_block_reason,
        "signed_artifact_verification_ok": signed_artifact_verification_ok,
        "signed_package_created_locally": signed_package_created_locally,
        "hard_optin_ok": hard_optin_ok,
        "local_scope_ok": local_scope_ok,
        "user_approval_allowed_for_future_local_test": user_approval_allowed,
        "phase46_activation_path_exists": phase46_activation_path_exists,
        "boundary_ok": boundary_ok,
        "install_attempted": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "next_phase_if_ready": "actual local activation script with hard opt-in flags",
        "next_phase_if_blocked": "perform actual local signing with Phase 54 hard opt-in flags, then rerun Phase 55 sanitizer",
        "checks": checks,
    }

    json_path = out_dir / "manual-activation-preflight-after-signed-verification-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    block_rows = "\n".join(f"| `{reason}` |" for reason in activation_block_reason) or "| `none` |"

    md = f"""# Manual Activation Preflight After Signed Verification Check

- Decision: `{decision}`
- Preflight Gate Only: `True`
- Activation Preflight Ready: `{activation_preflight_ready}`
- Activation Allowed Now: `False`
- Deactivation Allowed Now: `False`
- Signed Artifact Verification OK: `{signed_artifact_verification_ok}`
- Signed Package Created Locally: `{signed_package_created_locally}`
- Hard Opt-In OK: `{hard_optin_ok}`
- Local Scope OK: `{local_scope_ok}`
- User Approval Allowed For Future Local Test: `{user_approval_allowed}`
- Phase 46 Activation Path Exists: `{phase46_activation_path_exists}`
- Boundary OK: `{boundary_ok}`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Activation Block Reasons

| Reason |
| --- |
{block_rows}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "manual-activation-preflight-after-signed-verification-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
