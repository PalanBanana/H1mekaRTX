#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.free_account_driverkit_feasibility_matrix.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

MATRIX = [
    {
        "id": "FA-001",
        "topic": "Free Apple account app development",
        "official_status": "ALLOWED_FOR_TOOLS_AND_LOCAL_APP_WORK",
        "free_account_status": "GO_FOR_SWIFTUI_LOCAL_APP",
        "runtime_status": "NO_RUNTIME",
        "notes": "Use for SwiftUI host app, local JSON status UI, mocks, and documentation.",
    },
    {
        "id": "FA-002",
        "topic": "Official DriverKit entitlement request",
        "official_status": "APPLE_REVIEW_REQUIRED",
        "free_account_status": "NO_GO_FOR_GRANTED_ENTITLEMENT",
        "runtime_status": "BLOCKED",
        "notes": "DriverKit and device transport capabilities require Apple-granted entitlements.",
    },
    {
        "id": "FA-003",
        "topic": "Security-reduced local research environment",
        "official_status": "TEMPORARY_TESTING_ONLY",
        "free_account_status": "DOES_NOT_GRANT_ENTITLEMENTS",
        "runtime_status": "BLOCKED",
        "notes": "Security reduction is not a substitute for Apple-granted capabilities.",
    },
    {
        "id": "FA-004",
        "topic": "Ad-hoc signing",
        "official_status": "NOT_A_CAPABILITY_GRANT",
        "free_account_status": "NO_GO_FOR_DRIVERKIT_CAPABILITIES",
        "runtime_status": "BLOCKED",
        "notes": "Ad-hoc signing does not create Apple-granted DriverKit capabilities.",
    },
    {
        "id": "FA-005",
        "topic": "Provider matching and device ownership",
        "official_status": "REQUIRES_VALID_MATCH_AND_CAPABILITY",
        "free_account_status": "NO_GO",
        "runtime_status": "BLOCKED",
        "notes": "Must be gated behind evidence and official capability review.",
    },
    {
        "id": "FA-006",
        "topic": "Low-level hardware access",
        "official_status": "REQUIRES_DRIVER_STACK_AND_CAPABILITY",
        "free_account_status": "NO_GO",
        "runtime_status": "BLOCKED",
        "notes": "Not allowed in this repository until all implementation gates move to GO.",
    },
    {
        "id": "FA-007",
        "topic": "RTX 5070 Metal device exposure",
        "official_status": "UNSUPPORTED_BY_CURRENT_PROJECT_EVIDENCE",
        "free_account_status": "NO_GO",
        "runtime_status": "BLOCKED",
        "notes": "Requires a complete graphics driver architecture, not a mock service label.",
    },
]

BLOCKERS = [
    "Apple-granted DriverKit entitlement evidence missing",
    "Device transport entitlement evidence missing",
    "Bundle identity and signing evidence missing",
    "Provider matching transition remains not ready",
    "Device ownership transition remains not ready",
    "Low-level hardware access safety gate remains blocked",
    "RTX 5070 Metal runtime architecture remains unimplemented",
]


def build_matrix() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "FREE_ACCOUNT_DRIVERKIT_FEASIBILITY_RESEARCH_ONLY_NO_RUNTIME",
        "plain_answer": "Free-account work can continue for app UI, local reports, mocks, and validators. Official DriverKit runtime remains blocked without Apple-granted capabilities.",
        "free_account_path_available": True,
        "free_account_official_driverkit_runtime_allowed": False,
        "paid_program_or_apple_granted_capability_required": True,
        "apple_granted_driverkit_capability_required": True,
        "security_reduction_is_not_capability_grant": True,
        "ad_hoc_signing_is_not_capability_grant": True,
        "provider_attach_allowed": False,
        "device_ownership_allowed": False,
        "low_level_hardware_access_allowed": False,
        "rtx5070_metal_device_exposure_allowed": False,
        "rtx5070_metal_acceleration_runtime_allowed": False,
        "matrix": MATRIX,
        "blockers": BLOCKERS,
        "next_stage_recommendation": "Stage 55 should add a local-only status model loader for the SwiftUI host app, not a DriverKit runtime or hardware access implementation.",
        "safety_boundary": {
            "read_only": True,
            "documentation_only": True,
            "feasibility_matrix_only": True,
            "no_runtime": True,
            "no_security_bypass_instructions": True,
            "no_driver_installation": True,
            "no_driver_activation": True,
            "no_provider_attach": True,
            "no_device_ownership": True,
            "no_low_level_hardware_access": True,
            "no_metal_device_exposure": True,
            "no_rtx5070_metal_runtime": True,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    rows = [
        f"| `{item['id']}` | {item['topic']} | `{item['official_status']}` | `{item['free_account_status']}` | `{item['runtime_status']}` | {item['notes']} |"
        for item in data["matrix"]
    ]
    blockers = [f"- {item}" for item in data["blockers"]]

    return "\n".join(
        [
            "# Free-account DriverKit Feasibility Matrix",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"Plain answer: {data['plain_answer']}",
            "",
            f"Free-account path available: `{data['free_account_path_available']}`",
            "",
            f"Free-account official DriverKit runtime allowed: `{data['free_account_official_driverkit_runtime_allowed']}`",
            "",
            f"Paid program or Apple-granted capability required: `{data['paid_program_or_apple_granted_capability_required']}`",
            "",
            f"Apple-granted DriverKit capability required: `{data['apple_granted_driverkit_capability_required']}`",
            "",
            f"Security reduction is not capability grant: `{data['security_reduction_is_not_capability_grant']}`",
            "",
            f"Ad-hoc signing is not capability grant: `{data['ad_hoc_signing_is_not_capability_grant']}`",
            "",
            f"Provider attach allowed: `{data['provider_attach_allowed']}`",
            "",
            f"Device ownership allowed: `{data['device_ownership_allowed']}`",
            "",
            f"Low-level hardware access allowed: `{data['low_level_hardware_access_allowed']}`",
            "",
            f"RTX 5070 Metal device exposure allowed: `{data['rtx5070_metal_device_exposure_allowed']}`",
            "",
            f"RTX 5070 Metal acceleration runtime allowed: `{data['rtx5070_metal_acceleration_runtime_allowed']}`",
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
            "## Matrix",
            "",
            "| ID | Topic | Official Status | Free Account Status | Runtime Status | Notes |",
            "| --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Blockers",
            "",
            *blockers,
            "",
            "## Safety Boundary",
            "",
            "This stage is a feasibility matrix only. It adds no runtime, no driver installation, no driver activation, no provider transition, no device ownership transition, no low-level hardware access, and no RTX 5070 Metal runtime.",
            "",
            "## Next Stage",
            "",
            data["next_stage_recommendation"],
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate free-account DriverKit feasibility matrix.")
    parser.add_argument("--out-dir", default=".", help="Output directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_matrix()

    json_path = out_dir / "free-account-driverkit-feasibility-matrix.json"
    md_path = out_dir / "free-account-driverkit-feasibility-matrix.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
