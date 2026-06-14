#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.unsigned_local_app_bundle_layout_check.v1"

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

    manifest_path = root / "tools/driverkit-buildable-scaffold/unsigned-local-app-bundle-layout-generator.json"
    local_report_path = root / "host-report-bundle/unsigned-app-bundle/unsigned-local-app-bundle-layout.json"
    doc_path = root / "docs/driverkit/unsigned-local-app-bundle-layout-generator.md"
    phase48_path = root / "tools/driverkit-buildable-scaffold/signed-host-dext-packaging-preflight.json"

    manifest = read_json(manifest_path)
    local_report = read_json(local_report_path)
    phase48 = read_json(phase48_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_report_exists", local_report_path.exists(), str(local_report_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase48_manifest_exists", phase48_path.exists(), str(phase48_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.unsigned_local_app_bundle_layout_generator.v1"), "manifest schema"),
        make_check("local_report_schema", bool(local_report and local_report.get("schema") == "h1mekartx.unsigned_local_app_bundle_layout_report.v1"), "local report schema"),
        make_check("phase48_schema", bool(phase48 and phase48.get("schema") == "h1mekartx.signed_host_dext_packaging_preflight.v1"), "phase48 schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("local_report", local_report)]:
        for field in [
            "signed_package_created",
            "codesign_attempted",
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
        ]:
            checks.append(make_check(f"{obj_name}_{field}_false", bool(obj and obj.get(field) is False), field))

    derived = local_report.get("derived", {}) if local_report else {}
    checks.append(make_check("layout_created", bool(derived.get("layout_created")), "layout created"))
    checks.append(make_check("all_plists_parse_ok", bool(derived.get("all_plists_parse_ok")), "plists parse"))
    checks.append(make_check("contains_systemextensions_dir", bool(derived.get("contains_systemextensions_dir")), "SystemExtensions dir"))
    checks.append(make_check("contains_dext_under_systemextensions", bool(derived.get("contains_dext_under_systemextensions")), "dext under SystemExtensions"))
    checks.append(make_check("unsigned_placeholders_only", bool(derived.get("unsigned_placeholders_only")), "unsigned placeholders only"))

    paths = local_report.get("paths", {}) if local_report else {}
    for key in [
        "app_root",
        "host_info",
        "host_placeholder",
        "systemextensions_dir",
        "dext_root",
        "dext_info",
        "dext_placeholder",
    ]:
        checks.append(make_check(f"path_{key}_present", bool(paths.get(key)), key))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_READY" if failed == 0 else "FAIL_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_GENERATOR",
        "local_output_only": True,
        "host_report_bundle_local_only": True,
        "signed_package_created": False,
        "codesign_attempted": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "system_extension_activation_attempted": False,
        "system_extension_deactivation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "derived": derived,
        "checks": checks,
    }

    json_path = out_dir / "unsigned-local-app-bundle-layout-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    derived_text = json.dumps(derived, indent=2, sort_keys=True)

    md = f"""# Unsigned Local App Bundle Layout Check

- Decision: `{decision}`
- Local Output Only: `True`
- Host Report Bundle Local Only: `True`
- Signed Package Created: `False`
- Codesign Attempted: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- System Extension Deactivation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived

{derived_text}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "unsigned-local-app-bundle-layout-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
