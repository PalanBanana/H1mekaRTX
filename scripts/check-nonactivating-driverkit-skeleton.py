#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.nonactivating_driverkit_skeleton.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_NONACTIVATING_DRIVERKIT_SKELETON_LAYOUT",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "NONACTIVATING_SKELETON_ONLY: True",
    "NO_BUILD_REQUIRED: True",
    "NO_SIGNING_REQUIRED: True",
    "NO_INSTALL_ATTEMPTED: True",
    "NO_DRIVER_ACTIVATION: True",
    "NO_SYSTEM_EXTENSION_ACTIVATION: True",
    "NO_DEXT_LOAD: True",
    "NO_DEVICE_OWNERSHIP_REQUEST: True",
    "NO_PROVIDER_OPEN: True",
    "NO_BAR_MAPPING: True",
    "NO_BAR_MMIO_MUTATION: True",
    "NO_COMMAND_SUBMISSION: True",
    "NO_GSP_FIRMWARE_LOAD: True",
    "NO_GPU_RESET: True",
    "NO_FRAMEBUFFER_INIT: True",
    "NO_DISPLAY_ENGINE_INIT: True",
    "NO_KERNEL_OR_PROCESS_INJECTION: True",
    "NO_SIP_AMFI_BYPASS: True",
    "NO_PRIVATE_FRAMEWORK_PATCHING: True",
    "NO_FAKE_METAL_DEVICE_SPOOFING: True",
    "NONACTIVATING_DRIVERKIT_SKELETON_LAYOUT",
    "BUNDLE_IDENTITY_CONTRACT",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "com.apple.driverkit",
    "com.apple.developer.driverkit.transport.pci",
    "com.apple.developer.system-extension.install",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "BUILD_ATTEMPTED: False",
    "SIGNING_ATTEMPTED: False",
    "INSTALL_ATTEMPTED: False",
    "DRIVERKIT_ACTIVATION_ATTEMPTED: False",
    "SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False",
    "DEXT_LOAD_ATTEMPTED: False",
    "DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False",
    "PROVIDER_OPEN_ATTEMPTED: False",
    "BAR_MAPPING_ATTEMPTED: False",
    "BAR_MMIO_MUTATION_ATTEMPTED: False",
    "REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False",
    "RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False",
    "REAL_GPU_ACCELERATION_CLAIMED: False",
    "UI_COMPOSITOR_PROOF_CLAIMED: False",
    "METAL_PROOF_CLAIMED: False",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_plist(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("rb") as f:
        return plistlib.load(f)

def main() -> int:
    parser = argparse.ArgumentParser(description="Check non-activating DriverKit host+dext skeleton layout.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "nonactivating-driverkit-host-dext-skeleton.md"
    readme_path = root / "tools" / "driverkit-skeleton" / "README.md"
    host_plist_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.app.template" / "Info.plist"
    dext_plist_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.dext.template" / "Info.plist"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("skeleton_readme_exists", readme_path.exists(), str(readme_path)),
        make_check("host_plist_exists", host_plist_path.exists(), str(host_plist_path)),
        make_check("dext_plist_exists", dext_plist_path.exists(), str(dext_plist_path)),
    ]

    text = ""
    if contract_path.exists():
        text = contract_path.read_text(encoding="utf-8", errors="replace")
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    host_plist = read_plist(host_plist_path)
    dext_plist = read_plist(dext_plist_path)

    checks.append(make_check(
        "host_bundle_id_static_template",
        bool(host_plist and host_plist.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost"),
        "dev.h1meka.H1mekaRTXHost",
    ))
    checks.append(make_check(
        "dext_bundle_id_static_template",
        bool(dext_plist and dext_plist.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver"),
        "dev.h1meka.H1mekaRTXDriver",
    ))

    extension_point = None
    if dext_plist:
        extension_point = dext_plist.get("NSExtension", {}).get("NSExtensionPointIdentifier")
    checks.append(make_check(
        "dext_extension_point_driverkit",
        extension_point == "com.apple.driverkit",
        "com.apple.driverkit",
    ))

    iokit_personalities = dext_plist.get("IOKitPersonalities", {}) if dext_plist else {}
    personality = iokit_personalities.get("H1mekaRTX5070StaticTemplate", {})
    checks.append(make_check(
        "dext_iopci_match_static_template",
        personality.get("IOPCIMatch") == "0x2f0410de",
        "0x2f0410de",
    ))
    checks.append(make_check(
        "dext_provider_class_iopci",
        personality.get("IOProviderClass") == "IOPCIDevice",
        "IOPCIDevice",
    ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_NONACTIVATING_DRIVERKIT_SKELETON_READY" if failed_count == 0 else "FAIL_NONACTIVATING_DRIVERKIT_SKELETON"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_NONACTIVATING_DRIVERKIT_SKELETON_LAYOUT",
        "secondary_classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 9 non-activating DriverKit host app + dext skeleton layout",
        "nonactivating_skeleton_only": True,
        "build_attempted": False,
        "signing_attempted": False,
        "install_attempted": False,
        "driverkit_activation_attempted": False,
        "system_extension_activation_attempted": False,
        "dext_load_attempted": False,
        "device_ownership_request_attempted": False,
        "provider_open_attempted": False,
        "bar_mapping_attempted": False,
        "bar_mmio_mutation_attempted": False,
        "real_gpu_command_execution_attempted": False,
        "rtx5070_workload_attribution_claimed": False,
        "real_gpu_acceleration_claimed": False,
        "ui_compositor_proof_claimed": False,
        "metal_proof_claimed": False,
        "bundle_identity_contract": {
            "host_bundle_id": "dev.h1meka.H1mekaRTXHost",
            "dext_bundle_id": "dev.h1meka.H1mekaRTXDriver",
            "dext_extension_point": "com.apple.driverkit",
            "io_pci_match": "0x2f0410de",
            "provider_class": "IOPCIDevice",
        },
        "target_user_visible_goal": [
            "smooth Dock animation",
            "working transparency",
            "working blur",
            "smooth window movement and resizing",
            "smooth Mission Control",
            "smooth Launchpad",
            "smooth Stage Manager",
        ],
        "checks": checks,
    }

    json_path = out_dir / "nonactivating-driverkit-skeleton-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# Non-Activating DriverKit Skeleton Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Non-Activating Skeleton Only: `{report['nonactivating_skeleton_only']}`
- Build Attempted: `{report['build_attempted']}`
- Signing Attempted: `{report['signing_attempted']}`
- Install Attempted: `{report['install_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Dext Load Attempted: `{report['dext_load_attempted']}`
- Device Ownership Request Attempted: `{report['device_ownership_request_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## Bundle Identity Contract

| Field | Value |
| --- | --- |
| host_bundle_id | dev.h1meka.H1mekaRTXHost |
| dext_bundle_id | dev.h1meka.H1mekaRTXDriver |
| dext_extension_point | com.apple.driverkit |
| io_pci_match | 0x2f0410de |
| provider_class | IOPCIDevice |

## Target User-Visible UI Goal

This skeleton preserves the Hackintosh RTX 5070 macOS UI compositor target:

- Dock animation
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager

No UI acceleration success is claimed in this phase.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase creates a static non-activating skeleton layout only. It does not build, sign, install, activate, load, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: add static build/signing/entitlement audit gates before any real DriverKit project generation.
"""

    md_path = out_dir / "nonactivating-driverkit-skeleton-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
