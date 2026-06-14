#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.buildable_driverkit_host_dext_scaffold_check.v1"

REQUIRED = [
    "tools/driverkit-buildable-scaffold/buildable-driverkit-host-dext-scaffold.json",
    "tools/driverkit-buildable-scaffold/build-plan.json",
    "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist",
    "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift",
    "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements",
    "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist",
    "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements",
    "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Sources/H1mekaRTXDriver.cpp",
    "docs/driverkit/buildable-driverkit-host-dext-scaffold.md",
]

def make_check(name, passed, detail):
    return {"name": name, "passed": bool(passed), "detail": detail}

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def load_plist(path):
    try:
        with path.open("rb") as f:
            return plistlib.load(f)
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out-dir", default="release-readiness")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checks = []
    for rel in REQUIRED:
        checks.append(make_check("exists_" + rel.replace("/", "_"), (root / rel).exists(), rel))

    manifest = load_json(root / "tools/driverkit-buildable-scaffold/buildable-driverkit-host-dext-scaffold.json")
    plan = load_json(root / "tools/driverkit-buildable-scaffold/build-plan.json")
    host_info = load_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/Info.plist")
    dext_info = load_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Info.plist")
    host_ent = load_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.entitlements")
    dext_ent = load_plist(root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/H1mekaRTXDriver.entitlements")
    host_src = (root / "tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift").read_text(encoding="utf-8", errors="replace")
    dext_src = (root / "tools/driverkit-buildable-scaffold/H1mekaRTXDriver.dext/Sources/H1mekaRTXDriver.cpp").read_text(encoding="utf-8", errors="replace")

    checks += [
        make_check("manifest_schema", manifest and manifest.get("schema") == "h1mekartx.buildable_driverkit_host_dext_scaffold.v1", "manifest schema"),
        make_check("build_plan_schema", plan and plan.get("schema") == "h1mekartx.driverkit_build_plan.v1", "build plan schema"),
        make_check("host_bundle_id", host_info and host_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost", "host bundle id"),
        make_check("dext_bundle_id", dext_info and dext_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver", "dext bundle id"),
        make_check("iopcimatch_5070", "0x2f0410de" in json.dumps(dext_info), "0x2f0410de"),
        make_check("provider_class_iopci", "IOPCIDevice" in json.dumps(dext_info), "IOPCIDevice"),
        make_check("host_system_extension_entitlement", host_ent and host_ent.get("com.apple.developer.system-extension.install") is True, "host entitlement"),
        make_check("dext_driverkit_entitlement", dext_ent and dext_ent.get("com.apple.developer.driverkit") is True, "driverkit entitlement"),
        make_check("dext_pci_entitlement_present", "com.apple.developer.driverkit.transport.pci" in (dext_ent or {}), "pci entitlement"),
        make_check("host_dry_run_no_submit", "not submitting OSSystemExtensionRequest" in host_src, "dry run only"),
        make_check("dext_no_runtime_access_comment", "No provider open" in dext_src and "no BAR mapping" in dext_src, "runtime forbidden comment"),
    ]

    for field in [
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
        checks.append(make_check(f"manifest_{field}_false", manifest and manifest.get(field) is False, field))

    passed = sum(1 for c in checks if c["passed"])
    failed = len(checks) - passed
    decision = "PASS_BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD_READY" if failed == 0 else "FAIL_BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed,
        "failed_count": failed,
        "classification": "CLASSIFICATION_BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD",
        "real_development_build_scope_started": True,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "gpu_command_submission_attempted": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "checks": checks,
    }

    (out_dir / "buildable-driverkit-host-dext-scaffold-check.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rows = "\n".join(f"| `{c['name']}` | {'PASS' if c['passed'] else 'FAIL'} | {c['detail']} |" for c in checks)
    md = f"""# Buildable DriverKit Host + Dext Scaffold Check

- Decision: `{decision}`
- Real Development Build Scope Started: `True`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

| Check | Status | Detail |
| --- | --- | --- |
{rows}
"""
    (out_dir / "buildable-driverkit-host-dext-scaffold-check.md").write_text(md, encoding="utf-8")
    print("Decision:", decision)
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
