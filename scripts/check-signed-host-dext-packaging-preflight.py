#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.signed_host_dext_packaging_preflight_check.v1"

REQUIRED_LAYOUT = [
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist",
    "H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver"
]

REQUIRED_SIGNING = [
    "Apple Developer Team ID",
    "com.apple.developer.system-extension.install",
    "com.apple.developer.driverkit",
    "com.apple.developer.driverkit.transport.pci",
    "bundle ID dev.h1meka.H1mekaRTXHost",
    "bundle ID dev.h1meka.H1mekaRTXDriver"
]

REQUIRED_PRE_ACTIVATION = [
    "codesign verification passes for host app",
    "codesign verification passes for dext",
    "entitlements are dumped and checked",
    "dext nested under Contents/Library/SystemExtensions",
    "systemextensionsctl status captured before activation",
    "rollback/deactivation command available",
    "user approval is expected and allowed",
    "provider open remains disabled",
    "BAR mapping remains disabled",
    "GPU command submission remains disabled"
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

    manifest_path = root / "tools/driverkit-buildable-scaffold/signed-host-dext-packaging-preflight.json"
    doc_path = root / "docs/driverkit/signed-host-dext-packaging-preflight.md"
    phase47_path = root / "tools/driverkit-buildable-scaffold/manual-activation-approval-readiness-gate.json"
    phase46_path = root / "tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json"

    manifest = read_json(manifest_path)
    phase47 = read_json(phase47_path)
    phase46 = read_json(phase46_path)

    checks = [
        make_check("manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("doc_exists", doc_path.exists(), str(doc_path)),
        make_check("phase47_manifest_exists", phase47_path.exists(), str(phase47_path)),
        make_check("phase46_manifest_exists", phase46_path.exists(), str(phase46_path)),
        make_check("manifest_schema", bool(manifest and manifest.get("schema") == "h1mekartx.signed_host_dext_packaging_preflight.v1"), "manifest schema"),
        make_check("phase47_user_approval_allowed", bool(phase47 and phase47.get("manual_approval_allowed_for_future_local_test") is True), "phase47 user approval"),
        make_check("phase46_activation_code_exists", bool(phase46 and phase46.get("activation_capable_code_added") is True), "phase46 activation path"),
    ]

    for field in [
        "packaging_preflight_only",
        "signed_host_dext_packaging_preflight_ready",
    ]:
        checks.append(make_check(f"manifest_{field}_true", bool(manifest and manifest.get(field) is True), field))

    for field in [
        "signed_package_created",
        "codesign_attempted",
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

    layout = "\n".join(manifest.get("future_packaging_layout", []) if manifest else [])
    for item in REQUIRED_LAYOUT:
        checks.append(make_check("layout_contains_" + item.replace("/", "_"), item in layout, item))

    signing = "\n".join(manifest.get("required_future_signing_inputs", []) if manifest else [])
    for item in REQUIRED_SIGNING:
        checks.append(make_check("signing_contains_" + item.replace(" ", "_").replace(".", "_"), item in signing, item))

    pre_activation = "\n".join(manifest.get("required_future_pre_activation_checks", []) if manifest else [])
    for item in REQUIRED_PRE_ACTIVATION:
        checks.append(make_check("pre_activation_contains_" + item.replace(" ", "_").replace("/", "_"), item in pre_activation, item))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT_READY" if failed == 0 else "FAIL_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT",
        "packaging_preflight_only": True,
        "signed_package_created": False,
        "codesign_attempted": False,
        "install_attempted": False,
        "submit_activation_allowed_now": False,
        "submit_deactivation_allowed_now": False,
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

    json_path = out_dir / "signed-host-dext-packaging-preflight-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    md = f"""# Signed Host + Dext Packaging Preflight Check

- Decision: `{decision}`
- Packaging Preflight Only: `True`
- Signed Package Created: `False`
- Codesign Attempted: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- Submit Deactivation Allowed Now: `False`
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
    md_path = out_dir / "signed-host-dext-packaging-preflight-check.md"
    md_path.write_text(md, encoding="utf-8")

    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
