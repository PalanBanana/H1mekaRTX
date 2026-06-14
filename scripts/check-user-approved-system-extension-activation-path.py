#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.user_approved_system_extension_activation_path_check.v1"

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

    manifest_path = root / "tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json"
    doc_path = root / "docs/driverkit/user-approved-system-extension-activation-path.md"
    host_swift_path = root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift"

    manifest = read_json(manifest_path)
    host_text = host_swift_path.read_text(encoding="utf-8", errors="replace") if host_swift_path.exists() else ""

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("host_swift_exists", host_swift_path.exists(), str(host_swift_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.user_approved_system_extension_activation_path.v1"), "manifest schema"),
        make_check("activation_request_code_present", "activationRequest(forExtensionWithIdentifier:" in host_text, "activation request"),
        make_check("deactivation_request_code_present", "deactivationRequest(forExtensionWithIdentifier:" in host_text, "deactivation request"),
        make_check("submit_request_code_present", "OSSystemExtensionManager.shared.submitRequest" in host_text, "submitRequest"),
        make_check("manual_submit_activation_flag_present", "--submit-activation" in host_text, "--submit-activation"),
        make_check("manual_submit_deactivation_flag_present", "--submit-deactivation" in host_text, "--submit-deactivation"),
        make_check("default_status_only_present", "status-only: no OSSystemExtensionRequest submitted" in host_text, "status only"),
        make_check("dry_run_non_submitting_present", "dry-run: request object not created and not submitted" in host_text, "dry-run"),
        make_check("provider_open_false_marker", "providerOpenAttempted=false" in host_text, "provider open false"),
        make_check("bar_mapping_false_marker", "barMappingAttempted=false" in host_text, "bar mapping false"),
        make_check("gpu_command_false_marker", "gpuCommandSubmissionAttempted=false" in host_text, "gpu command false"),
    ]

    for field in [
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

    for field in [
        "activation_capable_code_added",
        "deactivation_capable_code_added",
        "default_mode_status_only",
        "dry_run_mode_non_submitting",
        "manual_approval_allowed_for_future_local_test",
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH_READY" if failed == 0 else "FAIL_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH",
        "activation_capable_code_added": True,
        "deactivation_capable_code_added": True,
        "default_mode_status_only": True,
        "dry_run_mode_non_submitting": True,
        "manual_approval_allowed_for_future_local_test": True,
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
        "checks": checks,
    }

    json_path = out_dir / "user-approved-system-extension-activation-path-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    md = f"""# User-Approved System Extension Activation Path Check

- Decision: `{decision}`
- Activation Capable Code Added: `True`
- Deactivation Capable Code Added: `True`
- Default Mode Status Only: `True`
- Dry-Run Mode Non-Submitting: `True`
- Manual Approval Allowed For Future Local Test: `True`
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

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "user-approved-system-extension-activation-path-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
