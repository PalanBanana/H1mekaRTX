# Runtime Probe Preflight & Read-Only Harness Contract

## Purpose

This contract defines the Phase 3 runtime probe preflight and read-only harness boundary for H1mekaRTX.

This phase exists to prepare future runtime diagnostics for RTX 5070 / NVIDIA RTX 5000-series macOS UI compositor acceleration research.

The long-term user-visible target remains:

- Smooth Dock animation
- Smooth Dock magnification
- Smooth Launchpad
- Smooth Mission Control
- Smooth Stage Manager
- Smooth window movement
- Smooth window resizing
- Working transparency
- Working blur
- Working shadows
- Smooth menu bar and Dock translucent effects

These goals relate to the WindowServer / Core Animation / QuartzCore / Metal compositor path.

## Classification

All Phase 3 preflight outputs must be labeled only as:

- CLASSIFICATION_STATIC_CONTRACT
- CLASSIFICATION_RUNTIME_PROBE_PREFLIGHT

This phase must not claim:

- real GPU command execution
- UI compositor proof
- Metal proof
- RTX 5070 workload attribution

## Safety Boundary

The Phase 3 preflight is non-invasive.

Required safety markers:

- READ_ONLY_PREFLIGHT_ONLY: True
- NO_BAR_MMIO_MUTATION: True
- NO_COMMAND_SUBMISSION: True
- NO_GSP_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_SYSTEM_MODIFICATION: True
- NO_DRIVER_ACTIVATION: True
- NO_KERNEL_OR_PROCESS_INJECTION: True
- NO_SIP_AMFI_BYPASS: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True

## DriverKit Prerequisites

DRIVERKIT_PREREQUISITES:

1. PCI matching manifest must exist before any driver activation attempt.
2. The target GPU must be identified as NVIDIA RTX 5070 / Blackwell.
3. Known static PCI identifiers:
   - vendor_id: 0x10de
   - device_id: 0x2f04
   - io_pci_match: 0x2f0410de
4. Apple DriverKit / PCIDriverKit entitlement requirements must be documented.
5. System Extension activation and deactivation must be reversible.
6. No DriverKit or System Extension activation is performed by this preflight.

## Future UI Compositor Evidence Checklist

FUTURE_UI_COMPOSITOR_EVIDENCE_CHECKLIST:

1. WindowServer must show evidence of compositor workload routing.
2. Core Animation frame delivery timing must be measurable.
3. QuartzCore rendering path must not be treated as proven GPU-backed without evidence.
4. Metal compositor fallback state must be distinguishable from real device-backed execution.
5. Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, and window animation behavior must be tied to evidence, not assumptions.
6. RTX 5070 workload attribution must remain UNPROVEN until real counters, logs, command execution, or verified compositor routing evidence exists.

## Current Contract State

- PREFLIGHT_STAGE_3_CONTRACT_READY: True
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
