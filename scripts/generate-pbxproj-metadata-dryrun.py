#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "h1mekartx.pbxproj_metadata_dryrun.v1"

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def read_plist(path: Path) -> dict:
    with path.open("rb") as f:
        return plistlib.load(f)

def main() -> int:
    parser = argparse.ArgumentParser(description="Generate non-building pbxproj metadata dry-run outputs.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--out-dir", default="tools/driverkit-xcode-layout", help="Output directory")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = (root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    layout_path = root / "tools" / "driverkit-xcode-layout" / "project-layout.json"
    host_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.app.template" / "Info.plist"
    dext_info_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.dext.template" / "Info.plist"
    host_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXHost.entitlements.template.plist"
    dext_entitlements_path = root / "tools" / "driverkit-skeleton" / "H1mekaRTXDriver.entitlements.template.plist"

    layout = read_json(layout_path)
    host_info = read_plist(host_info_path)
    dext_info = read_plist(dext_info_path)
    host_entitlements = read_plist(host_entitlements_path)
    dext_entitlements = read_plist(dext_entitlements_path)

    metadata = {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "CLASSIFICATION_PBXPROJ_METADATA_DRYRUN",
        "secondary_classification": "CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT",
        "tertiary_classification": "CLASSIFICATION_STATIC_CONTRACT",
        "pbxproj_metadata_dryrun_only": True,
        "real_xcodeproj_generation_attempted": False,
        "real_pbxproj_generation_attempted": False,
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
        "future_project_graph": {
            "project_name": layout["project"]["project_name"],
            "host_target_name": layout["project"]["host_target_name"],
            "dext_target_name": layout["project"]["dext_target_name"],
            "host_bundle_id": host_info["CFBundleIdentifier"],
            "dext_bundle_id": dext_info["CFBundleIdentifier"],
            "dext_extension_point": dext_info["NSExtension"]["NSExtensionPointIdentifier"],
            "host_entitlements": sorted(k for k in host_entitlements.keys() if k.startswith("com.apple.")),
            "dext_entitlements": sorted(k for k in dext_entitlements.keys() if k.startswith("com.apple.")),
            "source_files": [
                "tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist",
                "tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist",
                "tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist",
                "tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist",
            ],
            "would_generate": [
                "H1mekaRTXDriverKit.xcodeproj/project.pbxproj"
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

    json_path = out_dir / "pbxproj-metadata-dryrun.json"
    json_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    md = f"""# PBXProj Metadata Dry-Run

- Generated At UTC: `{metadata['generated_at_utc']}`
- Classification: `{metadata['classification']}`
- PBXProj Metadata Dry-Run Only: `{metadata['pbxproj_metadata_dryrun_only']}`
- Real Xcodeproj Generation Attempted: `{metadata['real_xcodeproj_generation_attempted']}`
- Real PBXProj Generation Attempted: `{metadata['real_pbxproj_generation_attempted']}`
- Xcodebuild Invocation Attempted: `{metadata['xcodebuild_invocation_attempted']}`
- Build Attempted: `{metadata['build_attempted']}`
- Signing Attempted: `{metadata['signing_attempted']}`
- Install Attempted: `{metadata['install_attempted']}`
- DriverKit Activation Attempted: `{metadata['driverkit_activation_attempted']}`
- System Extension Activation Attempted: `{metadata['system_extension_activation_attempted']}`
- Dext Load Attempted: `{metadata['dext_load_attempted']}`
- Provider Open Attempted: `{metadata['provider_open_attempted']}`
- BAR Mapping Attempted: `{metadata['bar_mapping_attempted']}`
- BAR/MMIO Mutation Attempted: `{metadata['bar_mmio_mutation_attempted']}`
- Real GPU Command Execution Attempted: `{metadata['real_gpu_command_execution_attempted']}`
- RTX 5070 Workload Attribution Claimed: `{metadata['rtx5070_workload_attribution_claimed']}`
- UI Compositor Proof Claimed: `{metadata['ui_compositor_proof_claimed']}`
- Metal Proof Claimed: `{metadata['metal_proof_claimed']}`

## Future Project Graph

| Field | Value |
| --- | --- |
| project_name | {metadata['future_project_graph']['project_name']} |
| host_target_name | {metadata['future_project_graph']['host_target_name']} |
| dext_target_name | {metadata['future_project_graph']['dext_target_name']} |
| host_bundle_id | {metadata['future_project_graph']['host_bundle_id']} |
| dext_bundle_id | {metadata['future_project_graph']['dext_bundle_id']} |
| dext_extension_point | {metadata['future_project_graph']['dext_extension_point']} |
| would_generate | H1mekaRTXDriverKit.xcodeproj/project.pbxproj |
| actually_generated | none |

## Target User-Visible UI Goal

This metadata dry-run preserves the Hackintosh RTX 5070 macOS UI compositor target:

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

This is metadata only. No `.xcodeproj`, real `project.pbxproj`, build, signing, install, DriverKit activation, System Extension activation, provider open, BAR mapping, command submission, UI compositor proof, or Metal proof is attempted.
"""
    md_path = out_dir / "pbxproj-metadata-dryrun.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"Wrote JSON: {json_path}")
    print(f"Wrote Markdown: {md_path}")
    print("Decision: PASS_PBXPROJ_METADATA_DRYRUN_GENERATED")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
