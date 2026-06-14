#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.codesign_dryrun_command_plan_check.v1"

REQUIRED_COMMANDS = [
    "sign_embedded_dext",
    "verify_embedded_dext",
    "sign_host_app",
    "verify_host_app",
    "dump_host_entitlements",
    "dump_dext_entitlements",
    "capture_systemextensionsctl_status_before_activation",
]

REQUIRED_ORDER = [
    "sign_embedded_dext",
    "verify_embedded_dext",
    "sign_host_app",
    "verify_host_app",
    "dump_host_entitlements",
    "dump_dext_entitlements",
    "capture_systemextensionsctl_status_before_activation",
]

FORBIDDEN_NOW_TRUE = [
    "codesign_executed",
    "codesign_signing_attempted",
    "signed_package_created",
    "install_attempted",
    "submit_activation_allowed_now",
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
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def command_names(plan: dict | None) -> list[str]:
    if not plan:
        return []
    return [cmd.get("name", "") for cmd in plan.get("planned_commands", [])]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = root / "tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json"
    generated_json_path = root / "release-readiness/codesign-dryrun-command-plan.json"
    generated_md_path = root / "release-readiness/codesign-dryrun-command-plan.md"
    doc_path = root / "docs/driverkit/codesign-dryrun-command-plan.md"
    phase51_path = root / "tools/driverkit-buildable-scaffold/local-unsigned-bundle-manifest-lock.json"
    phase50_path = root / "tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json"

    manifest = read_json(manifest_path)
    generated = read_json(generated_json_path)
    phase51 = read_json(phase51_path)
    phase50 = read_json(phase50_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("generated_json_exists", generated_json_path.exists(), str(generated_json_path)),
        make_check("generated_md_exists", generated_md_path.exists(), str(generated_md_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase51_manifest_exists", phase51_path.exists(), str(phase51_path)),
        make_check("phase50_manifest_exists", phase50_path.exists(), str(phase50_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.codesign_dryrun_command_plan.v1"), "manifest schema"),
        make_check("generated_schema", bool(generated and generated.get("schema") == "h1mekartx.codesign_dryrun_command_plan_generated.v1"), "generated schema"),
        make_check("phase51_schema", bool(phase51 and phase51.get("schema") == "h1mekartx.local_unsigned_bundle_manifest_lock.v1"), "phase51 schema"),
        make_check("phase50_schema", bool(phase50 and phase50.get("schema") == "h1mekartx.codesign_identity_entitlement_dryrun_evidence.v1"), "phase50 schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("generated", generated)]:
        checks.append(make_check(f"{obj_name}_command_plan_only_true", bool(obj and obj.get("command_plan_only") is True), "command_plan_only"))
        for field in FORBIDDEN_NOW_TRUE:
            checks.append(make_check(f"{obj_name}_{field}_false", bool(obj and obj.get(field) is False), field))

    names = command_names(generated)
    for required in REQUIRED_COMMANDS:
        checks.append(make_check(f"contains_command_{required}", required in names, required))

    checks.append(make_check("planned_order_exact", bool(generated and generated.get("planned_order") == REQUIRED_ORDER), "planned order"))

    for cmd in generated.get("planned_commands", []) if generated else []:
        name = cmd.get("name", "unknown")
        checks.append(make_check(f"{name}_execute_now_false", cmd.get("execute_now") is False, name))
        checks.append(make_check(f"{name}_command_nonempty", bool(cmd.get("command")), name))

    derived = generated.get("derived", {}) if generated else {}
    for field in [
        "all_commands_marked_execute_now_false",
        "contains_sign_embedded_dext",
        "contains_verify_embedded_dext",
        "contains_sign_host_app",
        "contains_verify_host_app",
        "contains_entitlement_dump",
        "contains_systemextensionsctl_status_capture",
    ]:
        checks.append(make_check(f"derived_{field}_true", bool(derived.get(field)), field))

    text = generated_md_path.read_text(encoding="utf-8", errors="replace") if generated_md_path.exists() else ""
    checks.append(make_check("no_real_identity_in_md", "Developer ID Application:" not in text and "Apple Development:" not in text, "no real identity"))
    checks.append(make_check("placeholder_identity_used", "SIGNING_IDENTITY_PLACEHOLDER" in json.dumps(generated), "placeholder identity"))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_CODESIGN_DRYRUN_COMMAND_PLAN_READY" if failed == 0 else "FAIL_CODESIGN_DRYRUN_COMMAND_PLAN"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_CODESIGN_DRYRUN_COMMAND_PLAN",
        "command_plan_only": True,
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

    json_path = out_dir / "codesign-dryrun-command-plan-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)

    md = f"""# Codesign Dry-Run Command Plan Check

- Decision: `{decision}`
- Command Plan Only: `True`
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
    md_path = out_dir / "codesign-dryrun-command-plan-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
