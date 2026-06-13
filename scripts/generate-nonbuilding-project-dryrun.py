#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.nonbuilding_project_generator_dryrun.v1"

FORBIDDEN_PATH_SUFFIXES = [
    "H1mekaRTXDriverKit.xcodeproj",
    "H1mekaRTXDriverKit.xcodeproj/project.pbxproj",
]

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def read_plist(path: Path) -> dict:
    with path.open("rb") as f:
        return plistlib.load(f)

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate non-building project generator dry-run manifest.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="tools/driverkit-xcode-layout/project-generator-dryrun", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    layout = read_json(root / "tools" / "driverkit-xcode-layout" / "project-layout.json")
    metadata = read_json(root / "tools" / "driverkit-xcode-layout" / "pbxproj-metadata-dryrun.json")
    sanitized = read_json(root / "tools" / "driverkit-xcode-layout" / "pbxproj-sanitized-metadata.json")
    host_info = read_plist(root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.app.template" / "Info.plist")
    dext_info = read_plist(root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.dext.template" / "Info.plist")

    forbidden_existing = []
    for suffix in FORBIDDEN_PATH_SUFFIXES:
        candidate = root / "tools" / "driverkit-xcode-layout" / suffix
        if candidate.exists():
            forbidden_existing.append(str(candidate.relative_to(root)))

    manifest = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_NONBUILDING_PROJECT_GENERATOR_DRYRUN",
        "secondary_classification": "CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "nonbuilding_project_generator_dryrun_only": True,
        "generator_emits_metadata_only": True,
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
        "forbidden_real_project_outputs_existing": forbidden_existing,
        "future_project_generator_contract": {
            "project_name": layout["project"]["project_name"],
            "host_target_name": layout["project"]["host_target_name"],
            "dext_target_name": layout["project"]["dext_target_name"],
            "host_bundle_id": host_info["CFBundleIdentifier"],
            "dext_bundle_id": dext_info["CFBundleIdentifier"],
            "dext_extension_point": dext_info["NSExtension"]["NSExtensionPointIdentifier"],
            "source_metadata_schema": metadata["schema"],
            "source_sanitized_schema": sanitized["schema"],
            "would_generate_if_promoted": [
                "tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj"
            ],
            "actually_generated": [],
        },
        "target_pci_provider_matching_manifest": {
            "target_gpu": "NVIDIA RTX 5070",
            "architecture_family": "NVIDIA Blackwell",
            "vendor_id": "0x10de",
            "device_id": "0x2f04",
            "io_pci_match": "0x2f0410de",
            "expected_provider_class": "IOPCIDevice",
            "expected_driver_family": "PCIDriverKit",
            "expected_pci_transport_entitlement": "com.apple.developer.driverkit.transport.pci",
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
    }

    json_path = out_dir / "project-generator-dryrun-manifest.json"
    json_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = f"""# Non-Building Project Generator Dry-Run Manifest

- Generated At UTC: `{manifest['generated_at_utc']}`
- Classification: `{manifest['classification']}`
- Non-Building Project Generator Dry-Run Only: `{manifest['nonbuilding_project_generator_dryrun_only']}`
- Generator Emits Metadata Only: `{manifest['generator_emits_metadata_only']}`
- Real Xcodeproj Generation Attempted: `{manifest['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{manifest['real_pbxproj_generation_attempted']}`
- Xcode Invocation Attempted: `{manifest['xcode_invocation_attempted']}`
- Xcodebuild Invocation Attempted: `{manifest['xcodebuild_invocation_attempted']}`
- Build Attempted: `{manifest['build_attempted']}`
- Signing Attempted: `{manifest['signing_attempted']}`
- Install Attempted: `{manifest['install_attempted']}`
- DriverKit Activation Attempted: `{manifest['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{manifest['system_extension_activation_attempted']}`
- Dext Load Attempted: `{manifest['dext_load_attempted']}`
- Provider Open Attempted: `{manifest['provider_open_attempted']}`
- BAR Mapping Attempted: `{manifest['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{manifest['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{manifest['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{manifest['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{manifest['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{manifest['metal_proof_claimed']}`

## Future Generator Contract

| Field | Value |
| --- | --- |
| project_name | {manifest['future_project_generator_contract']['project_name']} |
| host_target_name | {manifest['future_project_generator_contract']['host_target_name']} |
| dext_target_name | {manifest['future_project_generator_contract']['dext_target_name']} |
| host_bundle_id | {manifest['future_project_generator_contract']['host_bundle_id']} |
| dext_bundle_id | {manifest['future_project_generator_contract']['dext_bundle_id']} |
| dext_extension_point | {manifest['future_project_generator_contract']['dext_extension_point']} |
| would_generate_if_promoted | tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj |
| actually_generated | none |

## Target User-Visible UI Goal

This dry-run preserves the Hackintosh RTX 5070 macOS UI compositor target:

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

## Conclusion

This generator skeleton emits metadata only. It does not create a real `.xcodeproj`, real `project.pbxproj`, build, signing, install, activation, provider open, BAR mapping, command submission, UI compositor proof, or Metal proof.
"""
    md_path = out_dir / "project-generator-dryrun-manifest.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_NONBUILDING_PROJECT_GENERATOR_DRYRUN_GENERATED")
    return 0 if not forbidden_existing else 1

if __name__ == "__main__":
    raise SystemExit(main())
