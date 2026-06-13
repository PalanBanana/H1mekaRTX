#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.no_build_project_generation_preflight.v1"

REQUIRED_CONTRACT_TOKENS = [
    "CLASSIFICATION_NO_BUILD_PROJECT_GENERATION_PREFLIGHT",
    "CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE",
    "CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT",
    "CLASSIFICATION_STATIC_CONTRACT",
    "NO_BUILD_PROJECT_GENERATION_PREFLIGHT_ONLY: True",
    "PROJECT_GENERATION_NOT_ATTEMPTED: True",
    "NO_REAL_XCODEPROJ_GENERATION: True",
    "NO_REAL_PBXPROJ_GENERATION: True",
    "NO_XCODE_INVOCATION: True",
    "NO_XCODEBUILD_INVOCATION: True",
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
    "NO_BUILD_PROJECT_GENERATION_PREFLIGHT_INPUTS",
    "NO_BUILD_PROJECT_GENERATION_PREFLIGHT_OUTPUTS",
    "NO_BUILD_PROJECT_GENERATION_PREFLIGHT_REQUIREMENTS",
    "REAL_DRIVERKIT_ACTIVATION_GATE_REQUIREMENTS",
    "TARGET_PCI_PROVIDER_MATCHING_MANIFEST",
    "NVIDIA RTX 5070",
    "0x10de",
    "0x2f04",
    "0x2f0410de",
    "IOPCIDevice",
    "PCIDriverKit",
    "com.apple.developer.driverkit.transport.pci",
    "WindowServer",
    "Core Animation",
    "QuartzCore",
    "Metal compositor",
    "Dock",
    "transparency",
    "blur",
    "PROJECT_GENERATION_ATTEMPTED: False",
    "REAL_XCODEPROJ_GENERATION_ATTEMPTED: False",
    "REAL_PBXPROJ_GENERATION_ATTEMPTED: False",
    "XCODE_INVOCATION_ATTEMPTED: False",
    "XCODEBUILD_INVOCATION_ATTEMPTED: False",
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

FORBIDDEN_PATHS = [
    "tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj",
    "tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj",
    "H1mekaRTXDriverKit.xcodeproj",
    "H1mekaRTXDriverKit.xcodeproj/project.pbxproj",
]

def make_check(name: str, passed: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(passed), "detail": detail}

def read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def read_plist(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("rb") as f:
        return plistlib.load(f)

def main() -> int:
    parser = argparse.ArgumentParser(description="Check no-build project generation preflight gate.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="release-readiness", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contract_path = root / "docs" / "driverkit" / "no-build-project-generation-preflight.md"
    layout_path = root / "tools" / "driverkit-xcode-layout" / "project-layout.json"
    manifest_path = root / "tools" / "driverkit-xcode-layout" / "project-generator-dryrun" / "project-generator-dryrun-manifest.json"
    allowlist_path = root / "tools" / "driverkit-xcode-layout" / "project-generator-dryrun" / "project-generator-output-allowlist.json"
    host_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.app.template" / "Info.plist"
    dext_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.dext.template" / "Info.plist"
    host_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.entitlements.template.plist"
    dext_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.entitlements.template.plist"

    checks = [
        make_check("contract_file_exists", contract_path.exists(), str(contract_path)),
        make_check("project_layout_exists", layout_path.exists(), str(layout_path)),
        make_check("generator_manifest_exists", manifest_path.exists(), str(manifest_path)),
        make_check("output_allowlist_exists", allowlist_path.exists(), str(allowlist_path)),
        make_check("host_info_exists", host_info_path.exists(), str(host_info_path)),
        make_check("dext_info_exists", dext_info_path.exists(), str(dext_info_path)),
        make_check("host_entitlements_exists", host_entitlements_path.exists(), str(host_entitlements_path)),
        make_check("dext_entitlements_exists", dext_entitlements_path.exists(), str(dext_entitlements_path)),
    ]

    for path in FORBIDDEN_PATHS:
        checks.append(make_check("forbidden_path_absent_" + path.replace("/", "_").replace(".", "_"), not (root / path).exists(), path))

    text = contract_path.read_text(encoding="utf-8", errors="replace") if contract_path.exists() else ""
    for token in REQUIRED_CONTRACT_TOKENS:
        check_name = "requires_token_" + token.replace(" ", "_").replace(":", "").replace("/", "_").lower()
        checks.append(make_check(check_name, token in text, token))

    layout = read_json(layout_path)
    manifest = read_json(manifest_path)
    allowlist = read_json(allowlist_path)
    host_info = read_plist(host_info_path)
    dext_info = read_plist(dext_info_path)
    host_entitlements = read_plist(host_entitlements_path)
    dext_entitlements = read_plist(dext_entitlements_path)

    checks.append(make_check("layout_schema_matches", bool(layout and layout.get("schema") == "h1mekartx.deterministic_xcode_project_layout.v1"), "layout schema"))
    checks.append(make_check("manifest_schema_matches", bool(manifest and manifest.get("schema") == "h1mekartx.nonbuilding_project_generator_dryrun.v1"), "generator manifest schema"))
    checks.append(make_check("allowlist_schema_matches", bool(allowlist and allowlist.get("schema") == "h1mekartx.project_generator_output_allowlist.v1"), "allowlist schema"))

    checks.append(make_check("host_bundle_id_matches", bool(host_info and host_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXHost"), "dev.h1meka.H1mekaRTXHost"))
    checks.append(make_check("dext_bundle_id_matches", bool(dext_info and dext_info.get("CFBundleIdentifier") == "dev.h1meka.H1mekaRTXDriver"), "dev.h1meka.H1mekaRTXDriver"))
    checks.append(make_check("host_system_extension_entitlement_present", bool(host_entitlements and host_entitlements.get("com.apple.developer.system-extension.install") is True), "system extension entitlement template"))
    checks.append(make_check("dext_driverkit_entitlement_present", bool(dext_entitlements and dext_entitlements.get("com.apple.developer.driverkit") is True), "driverkit entitlement template"))

    for obj_name, obj in [("manifest", manifest), ("allowlist", allowlist)]:
        for field in [
            "real_xcodeproj_generation_attempted",
            "real_pbxproj_generation_attempted",
            "xcode_invocation_attempted",
            "xcodebuild_invocation_attempted",
            "build_attempted",
            "signing_attempted",
            "install_attempted",
            "driverkit_activation_attempted",
            "system_extension_activation_attempted",
            "dext_load_attempted",
            "device_ownership_request_attempted",
            "provider_open_attempted",
            "bar_mapping_attempted",
            "bar_mmio_mutation_attempted",
            "real_gpu_command_execution_attempted",
            "ui_compositor_proof_claimed",
            "metal_proof_claimed",
        ]:
            checks.append(make_check(
                f"{obj_name}_{field}_false",
                bool(obj and obj.get(field) is False),
                f"{obj_name}.{field}=false",
            ))

    passed_count = sum(1 for check in checks if check["passed"])
    failed_count = len(checks) - passed_count
    decision = "PASS_NO_BUILD_PROJECT_GENERATION_PREFLIGHT_READY" if failed_count == 0 else "FAIL_NO_BUILD_PROJECT_GENERATION_PREFLIGHT"

    report = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "classification": "CLASSIFICATION_NO_BUILD_PROJECT_GENERATION_PREFLIGHT",
        "secondary_classification": "CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "scope": "Phase 16 no-build project generation preflight",
        "no_build_project_generation_preflight_only": True,
        "project_generation_attempted": False,
        "real_xcodeproj_generation_attempted": False,
        "real_pbxproj_generation_attempted": False,
        "xcode_invocation_attempted": False,
        "xcodebuild_invocation_attempted": False,
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
        "real_driverkit_activation_gate": {
            "starts_after": [
                "approved Apple Developer Team ID",
                "approved DriverKit entitlement",
                "approved PCI transport entitlement",
                "valid signing identity",
                "buildable host app and dext project",
                "signed artifacts",
                "disposable rollback-capable test install",
                "reversible activation/deactivation implementation",
            ],
            "current_state": "BLOCKED_NOT_ATTEMPTED",
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

    json_path = out_dir / "no-build-project-generation-preflight-check.json"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rows = "\n".join(
        f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {check['detail']} |"
        for check in checks
    )

    md = f"""# No-Build Project Generation Preflight Check

- Generated At UTC: `{report['generated_at_utc']}`
- Decision: `{report['decision']}`
- Classification: `{report['classification']}`
- Secondary Classification: `{report['secondary_classification']}`
- Scope: `{report['scope']}`
- Project Generation Attempted: `{report['project_generation_attempted']}`
- Real Xcodeproj Generation Attempted: `{report['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{report['real_pbxproj_generation_attempted']}`
- Xcode Invocation Attempted: `{report['xcode_invocation_attempted']}`
- Xcodebuild Invocation Attempted: `{report['xcodebuild_invocation_attempted']}`
- Build Attempted: `{report['build_attempted']}`
- Signing Attempted: `{report['signing_attempted']}`
- Install Attempted: `{report['install_attempted']}`
- DriverKit Activation Attempted: `{report['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{report['system_extension_activation_attempted']}`
- Dext Load Attempted: `{report['dext_load_attempted']}`
- Provider Open Attempted: `{report['provider_open_attempted']}`
- BAR Mapping Attempted: `{report['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{report['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{report['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{report['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{report['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{report['metal_proof_claimed']}`

## When Real DriverKit Activation Starts

Real DriverKit/System Extension activation starts only after:

- approved Apple Developer Team ID
- approved DriverKit entitlement
- approved PCI transport entitlement
- valid signing identity
- buildable host app and dext project
- signed artifacts
- disposable rollback-capable test install
- reversible activation/deactivation implementation

Current state: `BLOCKED_NOT_ATTEMPTED`

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
{rows}

## Conclusion

This phase is a no-build preflight only. It does not create a real `.xcodeproj`, real `project.pbxproj`, invoke Xcode/xcodebuild, build, sign, install, activate, load, open a provider, map BAR memory, submit GPU commands, or claim RTX 5070 UI compositor acceleration.
"""
    md_path = out_dir / "no-build-project-generation-preflight-check.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print(f"Decision: {decision}")
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
