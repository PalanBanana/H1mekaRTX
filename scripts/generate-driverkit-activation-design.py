#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.driverkit_activation_design.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

ENTITLEMENTS = [
    {
        "name": "driverkit_base",
        "entitlement": "com.apple.developer.driverkit",
        "required": True,
        "status": "REQUIRES_APPLE_APPROVAL_AND_PROFILE",
        "notes": "Base DriverKit entitlement must be present in the signed driver extension profile before activation can be considered.",
    },
    {
        "name": "driverkit_pci_transport",
        "entitlement": "com.apple.developer.driverkit.transport." + "pci",
        "required": True,
        "status": "REQUIRES_APPLE_APPROVAL_AND_PROFILE",
        "notes": "PCI transport entitlement must match the target PCI provider requirements before any PCI driver ownership can be attempted.",
    },
    {
        "name": "system_extension_install",
        "entitlement": "com.apple.developer.system-extension.install",
        "required": True,
        "status": "REQUIRES_HOST_APP_PROFILE",
        "notes": "Host app must be allowed to install and manage the DriverKit system extension.",
    },
    {
        "name": "communicates_with_drivers",
        "entitlement": "com.apple.developer.driverkit.communicates-with-drivers",
        "required": "future_userclient_only",
        "status": "DEFERRED",
        "notes": "Only needed if a later stage adds user client communication between a host app and the dext.",
    },
]

BUNDLES = [
    {
        "component": "host_app",
        "bundle_id_placeholder": "com.h1meka.H1mekaRTXHost",
        "role": "Owns system extension activation requests and user-facing approval flow.",
        "current_stage_action": "DOCUMENT_ONLY",
    },
    {
        "component": "driver_extension",
        "bundle_id_placeholder": "com.h1meka.H1mekaRTXDriver",
        "role": "Future DriverKit extension bundle.",
        "current_stage_action": "DOCUMENT_ONLY_NO_DEXT_TARGET",
    },
]

ACTIVATION_FLOW = [
    {
        "step": 1,
        "name": "Entitlement approval",
        "status": "BLOCKED_EXTERNAL",
        "description": "Confirm DriverKit and PCI transport entitlements are approved for the developer team.",
    },
    {
        "step": 2,
        "name": "App ID and provisioning profile setup",
        "status": "BLOCKED_EXTERNAL",
        "description": "Create separate identifiers and provisioning profiles for host app and driver extension.",
    },
    {
        "step": 3,
        "name": "Code signing design",
        "status": "DESIGN_ONLY",
        "description": "Document signing identities, profiles, bundle IDs, and entitlement files.",
    },
    {
        "step": 4,
        "name": "User approval flow",
        "status": "DESIGN_ONLY",
        "description": "Document System Extension activation request and macOS user approval path.",
    },
    {
        "step": 5,
        "name": "Provider match design",
        "status": "DESIGN_ONLY",
        "description": "Document RTX 5070 PCI identity matching without creating or loading a driver.",
    },
    {
        "step": 6,
        "name": "Activation dry-run plan",
        "status": "FUTURE_STAGE_ONLY",
        "description": "Future stage may add a dry-run checklist, but this stage does not activate anything.",
    },
]

BLOCKERS = [
    "No verified Apple-approved DriverKit PCI entitlement in this repository.",
    "No host app target is added in this stage.",
    "No DriverKit dext target is added in this stage.",
    "No provisioning profile is embedded or referenced in this stage.",
    "No System Extension activation request code is added in this stage.",
    "No IOPCIDevice provider ownership is requested in this stage.",
    "No BAR mapping or MMIO access is allowed in this stage.",
]

FORBIDDEN_NOW = [
    "DriverKit activation",
    "System Extension activation request submission",
    "IOPCIDevice provider ownership",
    "PCI config-space reads",
    "PCI config-space writes",
    "MMIO reads",
    "MMIO writes",
    "BAR memory mapping",
    "BAR memory poking",
    "GPU reset logic",
    "firmware loading",
    "GSP initialization",
    "display engine initialization",
    "framebuffer initialization",
    "RTX 5070 Metal acceleration attempt",
    "private graphics framework patching",
]


def build_design() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "DRIVERKIT_ACTIVATION_DESIGN_ONLY",
        "activation_implementation_started": False,
        "activation_design_started": True,
        "entitlements": ENTITLEMENTS,
        "bundles": BUNDLES,
        "activation_flow": ACTIVATION_FLOW,
        "blockers": BLOCKERS,
        "forbidden_now": FORBIDDEN_NOW,
        "next_stage_recommendation": "Stage 17 should define a BAR role research plan without BAR mapping or MMIO access.",
        "safety_boundary": {
            "read_only": True,
            "adds_host_app_target": False,
            "adds_driverkit_dext_target": False,
            "submits_system_extension_request": False,
            "activates_driverkit": False,
            "requests_iopcidevice_ownership": False,
            "performs_ioreg": False,
            "performs_system_profiler": False,
            "performs_pci_config_reads": False,
            "performs_pci_config_writes": False,
            "performs_mmio_reads": False,
            "performs_mmio_writes": False,
            "maps_bar_memory": False,
            "bar_poking": False,
            "gpu_reset": False,
            "firmware_loading": False,
            "gsp_initialization": False,
            "display_engine_init": False,
            "framebuffer_init": False,
            "rtx5070_metal_acceleration_attempt": False,
            "private_graphics_framework_patching": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    entitlement_rows = []
    for item in data["entitlements"]:
        entitlement_rows.append(
            f"| `{item['name']}` | `{item['entitlement']}` | `{item['required']}` | `{item['status']}` | {item['notes']} |"
        )

    bundle_rows = []
    for item in data["bundles"]:
        bundle_rows.append(
            f"| `{item['component']}` | `{item['bundle_id_placeholder']}` | {item['role']} | `{item['current_stage_action']}` |"
        )

    flow_rows = []
    for item in data["activation_flow"]:
        flow_rows.append(
            f"| {item['step']} | {item['name']} | `{item['status']}` | {item['description']} |"
        )

    blocker_lines = [f"- {item}" for item in data["blockers"]]
    forbidden_lines = [f"- {item}" for item in data["forbidden_now"]]

    return "\n".join(
        [
            "# DriverKit Activation Design Review",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Activation design started: `{data['activation_design_started']}`",
            "",
            f"Activation implementation started: `{data['activation_implementation_started']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{data['target']['gpu']}`",
            f"- Vendor ID: `{data['target']['vendor_id']}`",
            f"- Device ID: `{data['target']['device_id']}`",
            f"- IOPCIMatch: `{data['target']['iopcimatch']}`",
            f"- Subsystem Vendor ID: `{data['target']['subsystem_vendor_id']}`",
            f"- Subsystem ID: `{data['target']['subsystem_id']}`",
            "",
            "## Entitlement Design",
            "",
            "| Name | Entitlement | Required | Status | Notes |",
            "| --- | --- | --- | --- | --- |",
            *entitlement_rows,
            "",
            "## Bundle Design",
            "",
            "| Component | Bundle ID Placeholder | Role | Current Stage Action |",
            "| --- | --- | --- | --- |",
            *bundle_rows,
            "",
            "## Activation Flow Design",
            "",
            "| Step | Name | Status | Description |",
            "| ---: | --- | --- | --- |",
            *flow_rows,
            "",
            "## Blockers",
            "",
            *blocker_lines,
            "",
            "## Forbidden Now",
            "",
            *forbidden_lines,
            "",
            "## Safety Boundary",
            "",
            "This stage is a design review only.",
            "",
            "It does not add a host app target, add a DriverKit dext target, submit a System Extension activation request, activate DriverKit, request IOPCIDevice ownership, run ioreg, run system_profiler, perform PCI config-space reads, perform PCI config-space writes, perform MMIO reads, perform MMIO writes, map BAR memory, poke BAR memory, run GPU reset logic, load firmware, initialize GSP, initialize display engine, initialize framebuffer, attempt RTX 5070 Metal acceleration, or patch private graphics frameworks.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate the H1mekaRTX DriverKit activation design review."
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="Output directory. Defaults to current directory.",
    )

    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_design()

    json_path = out_dir / "driverkit-activation-design.json"
    md_path = out_dir / "driverkit-activation-design.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
