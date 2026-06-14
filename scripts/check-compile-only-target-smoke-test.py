#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.compile_only_target_smoke_test_check.v1"

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

    manifest_path = root / "tools/driverkit-buildable-scaffold/compile-only-target-smoke-test.json"
    local_report_path = root / "host-report-bundle/compile-only-smoke/compile-only-target-smoke-test.json"
    doc_path = root / "docs/driverkit/compile-only-target-smoke-test.md"

    manifest = read_json(manifest_path)
    local_report = read_json(local_report_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_report_exists", local_report_path.exists(), str(local_report_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.compile_only_target_smoke_test.v1"), "manifest schema"),
        make_check("local_report_schema", bool(local_report and local_report.get("schema") == "h1mekartx.compile_only_target_smoke_test_report.v1"), "local report schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("local_report", local_report)]:
        for field in [
            "build_artifact_created",
            "signing_attempted",
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
            checks.append(make_check(f"{obj_name}_{field}_false", bool(obj and obj.get(field) is False), field))

    derived = local_report.get("derived", {}) if local_report else {}
    commands = local_report.get("commands", {}) if local_report else {}
    plist_results = local_report.get("plist_results", {}) if local_report else {}

    checks.append(make_check("compile_only_attempts_recorded", bool(derived.get("compile_only_attempts_recorded")), "compile-only attempts recorded"))
    checks.append(make_check("commands_recorded", bool(commands), "commands recorded"))
    checks.append(make_check("plist_results_recorded", bool(plist_results), "plist results recorded"))
    checks.append(make_check("plist_parse_all_ok", bool(derived.get("plist_parse_all_ok")), "plist parse all ok"))
    checks.append(make_check("compile_failures_allowed_at_preflight_stage", bool(derived.get("compile_failures_allowed_at_preflight_stage")), "failures recorded only"))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_COMPILE_ONLY_TARGET_SMOKE_TEST_READY" if failed == 0 else "FAIL_COMPILE_ONLY_TARGET_SMOKE_TEST"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_COMPILE_ONLY_TARGET_SMOKE_TEST",
        "compile_only_evidence_only": True,
        "host_report_bundle_local_only": True,
        "build_artifact_created": False,
        "signing_attempted": False,
        "install_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "derived": derived,
        "checks": checks,
    }

    json_path = out_dir / "compile-only-target-smoke-test-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    derived_text = json.dumps(derived, indent=2, sort_keys=True)

    md = f"""# Compile-Only Target Smoke Test Check

- Decision: `{decision}`
- Compile Only Evidence Only: `True`
- Host Report Bundle Local Only: `True`
- Build Artifact Created: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Status

{derived_text}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "compile-only-target-smoke-test-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
