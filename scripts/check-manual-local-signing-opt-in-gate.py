#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.manual_local_signing_opt_in_gate_check.v1"

REQUIRED_BEFORE = [
    "codesign dry-run command plan exists",
    "unsigned bundle manifest lock exists",
    "codesign identity evidence exists",
    "host entitlement parse proof exists",
    "dext entitlement parse proof exists",
    "host bundle ID matches",
    "dext bundle ID matches",
    "user passes an explicit future signing flag",
    "signing identity is selected explicitly",
    "signing output remains local-only",
    "signed artifact manifest is generated",
    "activation remains blocked after signing until verify gates pass"
]

REQUIRED_ORDER = [
    "confirm user opt-in flag",
    "choose signing identity explicitly",
    "sign embedded dext first",
    "verify embedded dext",
    "sign host app second",
    "verify host app",
    "dump host entitlements",
    "dump dext entitlements",
    "create signed artifact manifest",
    "keep activation blocked until separate activation gate"
]

REQUIRED_FLAGS = [
    "--i-understand-local-signing",
    "--signing-identity",
    "--output-under-host-report-bundle"
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

    manifest_path = root / "tools/driverkit-buildable-scaffold/manual-local-signing-opt-in-gate.json"
    doc_path = root / "docs/driverkit/manual-local-signing-opt-in-gate.md"
    phase52_path = root / "tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json"
    phase51_path = root / "tools/driverkit-buildable-scaffold/local-unsigned-bundle-manifest-lock.json"
    phase50_path = root / "tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json"

    manifest = read_json(manifest_path)
    phase52 = read_json(phase52_path)
    phase51 = read_json(phase51_path)
    phase50 = read_json(phase50_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase52_manifest_exists", phase52_path.exists(), str(phase52_path)),
        make_check("phase51_manifest_exists", phase51_path.exists(), str(phase51_path)),
        make_check("phase50_manifest_exists", phase50_path.exists(), str(phase50_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.manual_local_signing_opt_in_gate.v1"), "manifest schema"),
        make_check("phase52_schema", bool(phase52 and phase52.get("schema") == "h1mekartx.codesign_dryrun_command_plan.v1"), "phase52 schema"),
        make_check("phase51_schema", bool(phase51 and phase51.get("schema") == "h1mekartx.local_unsigned_bundle_manifest_lock.v1"), "phase51 schema"),
        make_check("phase50_schema", bool(phase50 and phase50.get("schema") == "h1mekartx.codesign_identity_entitlement_dryrun_evidence.v1"), "phase50 schema"),
    ]

    for field in [
        "manual_local_signing_opt_in_gate_ready",
        "user_may_opt_in_to_local_signing",
        "local_signing_requires_explicit_flag",
        "command_gate_only"
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    for field in [
        "local_signing_allowed_now",
        "codesign_executed",
        "codesign_signing_attempted",
        "signed_package_created",
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

    before = "\n".join(manifest.get("required_before_actual_signing", []) if manifest else [])
    for item in REQUIRED_BEFORE:
        checks.append(make_check("required_before_contains_" + item.replace(" ", "_").replace("-", "_"), item in before, item))

    order = manifest.get("future_signing_safety_order", []) if manifest else []
    checks.append(make_check("future_signing_order_exact", order == REQUIRED_ORDER, "future signing order"))

    flags = "\n".join(manifest.get("explicit_future_flags", []) if manifest else [])
    for flag in REQUIRED_FLAGS:
        checks.append(make_check("future_flag_contains_" + flag.replace("-", "_"), flag in flags, flag))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_MANUAL_LOCAL_SIGNING_OPT_IN_GATE_READY" if failed == 0 else "FAIL_MANUAL_LOCAL_SIGNING_OPT_IN_GATE"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_MANUAL_LOCAL_SIGNING_OPT_IN_GATE",
        "user_may_opt_in_to_local_signing": True,
        "local_signing_requires_explicit_flag": True,
        "local_signing_allowed_now": False,
        "command_gate_only": True,
        "codesign_executed": False,
        "codesign_signing_attempted": False,
        "signed_package_created": False,
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

    json_path = out_dir / "manual-local-signing-opt-in-gate-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Manual Local Signing Opt-In Gate Check

- Decision: `{decision}`
- User May Opt In To Local Signing: `True`
- Local Signing Requires Explicit Flag: `True`
- Local Signing Allowed Now: `False`
- Command Gate Only: `True`
- Codesign Executed: `False`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
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
    md_path = out_dir / "manual-local-signing-opt-in-gate-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
