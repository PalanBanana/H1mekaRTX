#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "h1mekartx.ui_compositor_proof_schema.v1"

TARGET = {
    "gpu": "NVIDIA RTX 5070",
    "vendor_id": "0x10de",
    "device_id": "0x2f04",
    "iopcimatch": "0x2f0410de",
    "subsystem_vendor_id": "0x1458",
    "subsystem_id": "0x417e",
}

PROOF_LEVELS = [
    {
        "level": "static_contract",
        "claim_allowed": False,
        "description": "Source-level schema, manifest, or generated report only.",
    },
    {
        "level": "host_diagnostics",
        "claim_allowed": False,
        "description": "PCIe identity, BAR-like inventory, IORegistry visibility, and host OS state.",
    },
    {
        "level": "graphics_stack_diagnostics",
        "claim_allowed": False,
        "description": "IODisplay, IOGraphics, IOAccelerator, Metal device list, WindowServer, Dock, Core Animation, QuartzCore hints.",
    },
    {
        "level": "runtime_probe",
        "claim_allowed": False,
        "description": "Read-only access attempts and logs without GPU command execution proof.",
    },
    {
        "level": "real_gpu_command_execution",
        "claim_allowed": False,
        "description": "Command submission, memory movement, shader/compute execution, timing, and correctness proof.",
    },
    {
        "level": "ui_compositor_proof",
        "claim_allowed": True,
        "description": "Evidence that macOS UI compositor paths are actually GPU-backed by RTX 5070.",
    },
    {
        "level": "metal_proof",
        "claim_allowed": True,
        "description": "Evidence that macOS Metal API or a verified Metal-facing layer executes RTX 5070 GPU-backed workloads.",
    },
]

UI_SURFACES = [
    {
        "surface": "Dock movement",
        "required_evidence": [
            "WindowServer or Dock trace around movement interval",
            "frame timing sample",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Dock magnification",
        "required_evidence": [
            "Dock magnification enabled state",
            "animation timing sample",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Window move",
        "required_evidence": [
            "WindowServer trace during drag",
            "frame pacing or dropped-frame evidence",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Window resize",
        "required_evidence": [
            "WindowServer trace during resize",
            "Core Animation transaction or frame timing evidence",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Mission Control",
        "required_evidence": [
            "transition timing evidence",
            "WindowServer or Dock transition trace",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Launchpad",
        "required_evidence": [
            "transition timing evidence",
            "Dock or WindowServer transition trace",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Transparency and blur",
        "required_evidence": [
            "reduce-transparency state",
            "visual effect or backdrop trace",
            "GPU-backed compositor attribution",
        ],
    },
    {
        "surface": "Menu bar and sidebar translucency",
        "required_evidence": [
            "display/UI state sample",
            "visual effect trace",
            "GPU-backed compositor attribution",
        ],
    },
]

EVIDENCE_REQUIREMENTS = [
    {
        "id": "target_identity",
        "level": "host_diagnostics",
        "required_for_ui_compositor_claim": True,
        "description": "RTX 5070 vendor ID, device ID, subsystem ID, class code, and IORegistry path are captured.",
    },
    {
        "id": "bar_inventory",
        "level": "host_diagnostics",
        "required_for_ui_compositor_claim": True,
        "description": "BAR-like assigned-addresses/reg/system_profiler/ioreg inventory is captured.",
    },
    {
        "id": "graphics_stack_visibility",
        "level": "graphics_stack_diagnostics",
        "required_for_ui_compositor_claim": True,
        "description": "IODisplay, IOGraphics, IOAccelerator, display, and Metal-facing visibility are captured.",
    },
    {
        "id": "current_ui_gpu_attribution",
        "level": "graphics_stack_diagnostics",
        "required_for_ui_compositor_claim": True,
        "description": "Current UI rendering path can be attributed to a concrete GPU or compositor backend.",
    },
    {
        "id": "windowserver_coreanimation_timing",
        "level": "graphics_stack_diagnostics",
        "required_for_ui_compositor_claim": True,
        "description": "WindowServer/Core Animation timing evidence exists for Dock/window/Mission Control/Launchpad interactions.",
    },
    {
        "id": "rtx5070_gpu_workload_attribution",
        "level": "real_gpu_command_execution",
        "required_for_ui_compositor_claim": True,
        "description": "RTX 5070 work attribution exists during the UI compositor sample window.",
    },
    {
        "id": "ui_surface_correlation",
        "level": "ui_compositor_proof",
        "required_for_ui_compositor_claim": True,
        "description": "UI action interval, compositor timing, and RTX 5070 GPU-backed work are correlated.",
    },
]

FORBIDDEN_SHORTCUTS = [
    "Treating PCIe visibility as UI acceleration proof.",
    "Treating BAR inventory as Metal proof.",
    "Treating IOAccelerator keyword hits as RTX 5070 compositor proof.",
    "Treating a Metal device list alone as RTX 5070 Metal proof.",
    "Spoofing a Metal device.",
    "Patching private frameworks.",
    "Bypassing SIP or AMFI.",
    "Injecting into WindowServer or Dock.",
]


def build_schema() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "target": TARGET,
        "decision": "UI_COMPOSITOR_PROOF_SCHEMA_READY",
        "ui_compositor_acceleration_claim_allowed_now": False,
        "metal_acceleration_claim_allowed_now": False,
        "proof_levels": PROOF_LEVELS,
        "ui_surfaces": UI_SURFACES,
        "evidence_requirements": EVIDENCE_REQUIREMENTS,
        "forbidden_shortcuts": FORBIDDEN_SHORTCUTS,
        "minimum_claim_rule": "UI compositor acceleration may be claimed only after target identity, graphics stack visibility, UI GPU attribution, timing evidence, RTX 5070 workload attribution, and UI surface correlation are all present.",
        "safety_boundary": {
            "schema_only": True,
            "static_contract": True,
            "runs_live_diagnostics": False,
            "driverkit_activation": False,
            "system_extension_activation": False,
            "device_ownership_request": False,
            "pci_config_writes": False,
            "mmio_reads": False,
            "mmio_writes": False,
            "bar_mapping": False,
            "bar_poking": False,
            "gpu_command_submission": False,
            "windowserver_injection": False,
            "dock_injection": False,
            "private_framework_patching": False,
            "sip_bypass": False,
            "amfi_bypass": False,
            "fake_metal_device_spoofing": False,
            "ui_compositor_proof_claim": False,
            "metal_proof_claim": False,
        },
    }


def markdown_report(data: dict[str, Any]) -> str:
    proof_rows = [
        f"| `{item['level']}` | `{item['claim_allowed']}` | {item['description']} |"
        for item in data["proof_levels"]
    ]
    surface_rows = [
        f"| `{item['surface']}` | {', '.join(f'`{x}`' for x in item['required_evidence'])} |"
        for item in data["ui_surfaces"]
    ]
    evidence_rows = [
        f"| `{item['id']}` | `{item['level']}` | `{item['required_for_ui_compositor_claim']}` | {item['description']} |"
        for item in data["evidence_requirements"]
    ]
    shortcut_lines = [f"- {item}" for item in data["forbidden_shortcuts"]]

    return "\n".join(
        [
            "# UI Compositor Proof Schema",
            "",
            f"Generated UTC: `{data['generated_at_utc']}`",
            "",
            f"Decision: `{data['decision']}`",
            "",
            f"UI compositor acceleration claim allowed now: `{data['ui_compositor_acceleration_claim_allowed_now']}`",
            "",
            f"Metal acceleration claim allowed now: `{data['metal_acceleration_claim_allowed_now']}`",
            "",
            "## Target",
            "",
            f"- GPU: `{data['target']['gpu']}`",
            f"- Vendor ID: `{data['target']['vendor_id']}`",
            f"- Device ID: `{data['target']['device_id']}`",
            f"- IOPCIMatch: `{data['target']['iopcimatch']}`",
            "",
            "## Proof Levels",
            "",
            "| Level | Claim Allowed | Description |",
            "| --- | --- | --- |",
            *proof_rows,
            "",
            "## UI Surfaces",
            "",
            "| Surface | Required Evidence |",
            "| --- | --- |",
            *surface_rows,
            "",
            "## Evidence Requirements",
            "",
            "| ID | Level | Required For UI Claim | Description |",
            "| --- | --- | --- | --- |",
            *evidence_rows,
            "",
            "## Forbidden Shortcuts",
            "",
            *shortcut_lines,
            "",
            "## Minimum Claim Rule",
            "",
            data["minimum_claim_rule"],
            "",
            "## Safety Boundary",
            "",
            "This schema is a static contract only. It does not run live diagnostics, activate DriverKit or System Extensions, request device ownership, write PCI config space, access MMIO, map BAR memory, submit GPU commands, inject into WindowServer or Dock, patch private frameworks, bypass SIP/AMFI, spoof Metal devices, or claim RTX 5070 UI compositor or Metal acceleration.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate H1mekaRTX UI compositor proof schema.")
    parser.add_argument("--out-dir", default=".", help="Output directory. Defaults to current directory.")
    args = parser.parse_args()

    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    data = build_schema()
    json_path = out_dir / "ui-compositor-proof-schema.json"
    md_path = out_dir / "ui-compositor-proof-schema.md"

    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    md_path.write_text(markdown_report(data) + "\n")

    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Decision: {data['decision']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
