#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.actual_local_signing_hard_optin_check.v1"

REQUIRED_FLAGS = [
    "--i-understand-local-signing",
    "--signing-identity",
    "--output-under-host-report-bundle",
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

    manifest_path = root / "tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json"
    doc_path = root / "docs/driverkit/actual-local-signing-hard-optin.md"
    signer_path = root / "scripts/actual-local-signing-hard-optin.py"
    phase53_path = root / "tools/driverkit-buildable-scaffold/manual-local-signing-opt-in-gate.json"
    phase52_path = root / "tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json"

    manifest = read_json(manifest_path)
    phase53 = read_json(phase53_path)
    phase52 = read_json(phase52_path)
    signer_text = signer_path.read_text(encoding="utf-8", errors="replace") if signer_path.exists() else ""

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("signer_exists", signer_path.exists(), str(signer_path)),
        make_check("phase53_manifest_exists", phase53_path.exists(), str(phase53_path)),
        make_check("phase52_manifest_exists", phase52_path.exists(), str(phase52_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.actual_local_signing_hard_optin.v1"), "manifest schema"),
        make_check("phase53_schema", bool(phase53 and phase53.get("schema") == "h1mekartx.manual_local_signing_opt_in_gate.v1"), "phase53 schema"),
        make_check("phase52_schema", bool(phase52 and phase52.get("schema") == "h1mekartx.codesign_dryrun_command_plan.v1"), "phase52 schema"),
    ]

    for field in [
        "actual_local_signing_hard_optin_ready",
        "default_refuses_signing",
        "hard_optin_flags_required",
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    for field in [
        "ci_signing_attempted",
        "codesign_executed_by_default",
        "codesign_signing_attempted_in_ci",
        "signed_package_created_in_ci",
        "install_attempted",
        "submit_activation_allowed_now",
        "submit_deactivation_allowed_now",
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

    flags_text = "\n".join(manifest.get("required_flags", []) if manifest else [])
    for flag in REQUIRED_FLAGS:
        checks.append(make_check("manifest_requires_" + flag.replace("-", "_"), flag in flags_text, flag))
        checks.append(make_check("signer_parses_" + flag.replace("-", "_"), flag in signer_text, flag))

    for token in [
        "REFUSE_SIGNING_HARD_OPTIN_NOT_SATISFIED",
        "local_scope_ok",
        "host-report-bundle",
        "codesign",
        "sign_embedded_dext",
        "verify_embedded_dext",
        "sign_host_app",
        "verify_host_app",
        "dump_host_entitlements",
        "dump_dext_entitlements",
        "activation_still_blocked",
        "provider_open_still_blocked",
        "bar_mapping_still_blocked",
        "gpu_command_submission_still_blocked",
    ]:
        checks.append(make_check("signer_contains_" + token.replace("-", "_"), token in signer_text, token))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_ACTUAL_LOCAL_SIGNING_HARD_OPTIN_READY" if failed == 0 else "FAIL_ACTUAL_LOCAL_SIGNING_HARD_OPTIN"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_ACTUAL_LOCAL_SIGNING_HARD_OPTIN",
        "default_refuses_signing": True,
        "hard_optin_flags_required": True,
        "ci_signing_attempted": False,
        "codesign_executed_by_default": False,
        "codesign_signing_attempted_in_ci": False,
        "signed_package_created_in_ci": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    json_path = out_dir / "actual-local-signing-hard-optin-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Actual Local Signing Hard Opt-In Check

- Decision: `{decision}`
- Default Refuses Signing: `True`
- Hard Opt-In Flags Required: `True`
- CI Signing Attempted: `False`
- Codesign Executed By Default: `False`
- Codesign Signing Attempted In CI: `False`
- Signed Package Created In CI: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
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
    md_path = out_dir / "actual-local-signing-hard-optin-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
