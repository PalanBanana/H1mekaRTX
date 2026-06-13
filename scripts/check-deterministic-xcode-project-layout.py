#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.deterministic_xcode_project_layout_check.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "PROJECT_LAYOUT_CONTRACT_ONLY: True",
    "NO_XCODEPROJ_GENERATION: True",
    "NO_BUILD_ATTEMPTED: True",
    "NO_SIGNING_ATTEMPTED: True",
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
    "DETERMINISTIC_XCODE_PROJECT_LAYOUT_INPUTS",
    "PROJECT_IDENTITY_CONTRACT",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "DETERMINISTIC_XCODE_LAYOUT_CHECKLIST",
    "H1mekaRTXDriverKit",
    "H1mekaRTXHost",
    "H1mekaRTXDriver",
    "dev.h1meka.H1mekaRTXHost",
    "dev.h1meka.H1mekaRTXDriver",
    "com.apple.driverkit",
    "com.apple.developer.driverkit",
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
    "XCODEPROJ_GENERATION_ATTEMPTED: False",
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

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check deterministic Xcode/project layout contract.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "deterministic-xcode-project-layout-contract.md"
    layout_path = root / "tools" / "driverkit-xcode-layout" / "project-layout.json"
    layout_readme_path = root / "tools" / "driverkit-xcode-layout" / "README.md"
    host_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.app.template" / "Info.plist"
    dext_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.dext.template" / "Info.plist"
    host_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.entitlements.template.plist"
    dext_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.entitlements.template.plist"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("layout_json_exists", layout_path.exists(), str(layout_path)),
        make_check("layout_readme_exists", layout_readme_path.exists(), str(layout_readme_path)),
        make_check("host_info_plist_exists", host_info_path.exists(), str(host_info_path)),
        make_check("dext_info_plist_exists", dext_info_path.exists(), str(dext_info_path)),
        make_check("host_entitlements_template_exists", host_entitlements_path.exists(), str(host_entitlements_path)),
        make_check("dext_entitlements_template_exists", dext_entitlements_path.exists(), str(dext_entitlements_path)),
    ]

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    layout = read_json(layout_path)
    host_info = read_plist(host_info_path)
    dext_info = read_plist(dext_info_path)
    host_entitlements = read_plist(host_entitlements_path)
    dext_entitlements = read_plist(dext_entitlements_path)

    checks.append(make_check(
        "layout_schema_matches",
        bool(layout and layout.get("schema") == "h1mekartx.deterministic_xcode_project_layout.v1"),
        "h1mekartx.deterministic_xcode_project_layout.v1",
    ))
    checks.append(make_check(
        "layout_contract_only_true",
        bool(layout and layout.get("project_layout_contract_only") is True),
        "project_layout_contract_only=true",
    ))
    checks.append(make_check(
        "layout_no_xcodeproj_generation",
        bool(layout and layout.get("xcodeproj_generation_attempted") is False),
        "xcodeproj_generation_attempted=false",
    ))
    checks.append(make_check(
        "layout_no_build_sign_install_activation",
        bool(layout and layout.get("build_attempted") is False and layout.get("signing_attempted") is False and layout.get("install_attempted") is False and layout.get("driverkit_activation_attempted") is False),
        "no build/sign/install/activation",
    ))
    checks.append(make_check(
        "host_bundle_id_consistent",
        bool(layout and host_info and layout["targets"]["host"]["bundle_id"] == host_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost"),
        "dev.h1meka.H1mekaRTXHost",
    ))
    checks.append(make_check(
        "dext_bundle_id_consistent",
        bool(layout and dext_info and layout["targets"]["dext"]["bundle_id"] == dext_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver"),
        "dev.h1meka.H1mekaRTXDriver",
    ))
    checks.append(make_check(
        "dext_extension_point_consistent",
        bool(layout and dext_info and layout["targets"]["dext"]["extension_point"] == dext_info.get("NSExtension", {}).get("NSExtensionPointIdentifier") == "com.apple.driverkit"),
        "com.apple.driverkit",
    ))
    checks.append(make_check(
        "host_system_extension_entitlement_template_present",
        bool(host_entitlements and host_entitlements.get("com.apple.developer.system-extension.install") is True),
        "com.apple.developer.system-extension.install",
    ))
    checks.append(make_check(
        "dext_driverkit_entitlement_template_present",
        bool(dext_entitlements and dext_entitlements.get("com.apple.developer.driverkit") is True),
        "com.apple.developer.driverkit",
    ))
    pci_entries = dext_entitlements.get("com.apple.developer.driverkit.transport.pci", []) if dext_entitlements else []
    pci_text = json.dumps(pci_entries, sort_keys=True)
    checks.append(make_check("dext_pci_transport_vendor_id_present", "0x10de" in pci_text, "0x10de"))
    checks.append(make_check("dext_pci_transport_device_id_present", "0x2f04" in pci_text, "0x2f04"))
    checks.append(make_check("dext_pci_transport_iopcimatch_present", "0x2f0410de" in pci_text, "0x2f0410de"))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_DETERMINISTIC_XCODE_PROJECT_LAYOUT_READY" if failed_count == 0 else "FAIL_DETERMINISTIC_XCODE_PROJECT_LAYOUT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
        "secondary_classification": "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 11 deterministic Xcode/project layout contract",
        "project_layout_contract_only": True,
        "xcodeproj_generation_attempted": False,
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
        "project_identity_contract": {
            "project_name": "H1mekaRTXDriverKit",
            "host_target_name": "H1mekaRTXHost",
            "dext_target_name": "H1mekaRTXDriver",
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

    json_path = out_dir / "deterministic-xcode-project-layout-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md_content = f"""# Deterministic Xcode / Project Layout Report

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Project Layout Contract Only: `{report['project_layout_contract_only']}`
- Xcodeproj Generation Attempted: `{report['xcodeproj_generation_attempted']}`
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

## Project Identity Contract

| Field | Value |
| --- | --- |
| project_name | H1mekaRTXDriverKit |
| host_target_name | H1mekaRTXHost |
| dext_target_name | H1mekaRTXDriver |
| host_bundle_id | dev.h1meka.H1mekaRTXHost |
| dext_bundle_id | dev.h1meka.H1mekaRTXDriver |
| dext_extension_point | com.apple.driverkit |
| io_pci_match | 0x2f0410de |
| provider_class | IOPCIDevice |

## Target User-Visible UI Goal

This layout preserves the Hackintosh RTX 5070 macOS UI compositor target:

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

This phase creates deterministic project layout metadata only. It does not generate an Xcode project, build, sign, install, activate, load, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.

## Next Phase Recommendation

Next safe step: add a non-building deterministic project generator dry-run that writes placeholder pbxproj metadata only, with no build/sign/activation.
"""

    md_path = out_dir / "deterministic-xcode-project-layout-check.md"
    md_path.write_text(md_content, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
