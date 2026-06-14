#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.driverkit_local_toolchain_build_preflight_check.v1"

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

    manifest_path = root / "tools/driverkit-buildable-scaffold/driverkit-local-toolchain-build-preflight.json"
    local_report_path = root / "host-report-bundle/driverkit-toolchain-preflight/driverkit-local-toolchain-build-preflight.json"
    doc_path = root / "docs/driverkit/driverkit-local-toolchain-build-preflight.md"

    manifest = read_json(manifest_path)
    local_report = read_json(local_report_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("local_report_exists", local_report_path.exists(), str(local_report_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.driverkit_local_toolchain_build_preflight.v1"), "manifest schema"),
        make_check("local_report_schema", bool(local_report and local_report.get("schema") == "h1mekartx.driverkit_local_toolchain_build_preflight_report.v1"), "local report schema"),
    ]

    for obj_name, obj in [("manifest", manifest), ("local_report", local_report)]:
        for field in [
            "build_attempted",
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
    checks.append(make_check("scaffold_inputs_present", bool(derived.get("scaffold_inputs_present")), "scaffold inputs"))
    checks.append(make_check("toolchain_status_recorded", bool(local_report and local_report.get("toolchain_commands")), "toolchain commands recorded"))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_DRIVERKIT_LOCAL_TOOLCHAIN_BUILD_PREFLIGHT_READY" if failed == 0 else "FAIL_DRIVERKIT_LOCAL_TOOLCHAIN_BUILD_PREFLIGHT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_DRIVERKIT_LOCAL_TOOLCHAIN_BUILD_PREFLIGHT",
        "local_preflight_only": True,
        "host_report_bundle_local_only": True,
        "build_attempted": False,
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

    json_path = out_dir / "driverkit-local-toolchain-build-preflight-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    derived_text = json.dumps(derived, indent=2, sort_keys=True)

    md = f"""# DriverKit Local Toolchain Build Preflight Check

- Decision: `{decision}`
- Local Preflight Only: `True`
- Host Report Bundle Local Only: `True`
- Build Attempted: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Toolchain Status

{derived_text}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    md_path = out_dir / "driverkit-local-toolchain-build-preflight-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
