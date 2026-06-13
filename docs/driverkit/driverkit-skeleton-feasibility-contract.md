# DriverKit / PCIDriverKit Skeleton Feasibility Contract

## Purpose

This Phase 4 contract defines the feasibility boundary for a future DriverKit / PCIDriverKit skeleton.

This phase exists to prepare a reversible System Extension / DriverKit development path for H1mekaRTX without activating a driver, claiming acceleration, touching BAR/MMIO, or submitting GPU commands.

The long-term user-visible target remains macOS UI compositor acceleration research for:

- Dock smoothness
- Dock magnification
- transparency
- blur
- window movement and resizing
- Mission Control
- Launchpad
- Stage Manager
- WindowServer / Core Animation / QuartzCore / Metal compositor evidence

## Classification

All Phase 4 outputs must be labeled only as:

- CLASSIFICATION_STATIC_CONTRACT
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT

This phase must not claim:

- real GPU command execution
- UI compositor proof
- Metal proof
- RTX 5070 workload attribution
- DriverKit activation success
- System Extension activation success

## Safety Boundary

Required safety markers:

- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
- NO_DEVICE_OWNERSHIP_REQUEST: True
- NO_BAR_MMIO_MUTATION: True
- NO_COMMAND_SUBMISSION: True
- NO_GSP_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_FRAMEBUFFER_INIT: True
- NO_DISPLAY_ENGINE_INIT: True
- NO_KERNEL_OR_PROCESS_INJECTION: True
- NO_SIP_AMFI_BYPASS: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True

## Target PCI Matching Manifest

TARGET_PCI_MATCHING_MANIFEST:

- target_gpu: NVIDIA RTX 5070
- architecture_family: NVIDIA Blackwell
- vendor_id: 0x10de
- device_id: 0x2f04
- io_pci_match: 0x2f0410de
- expected_provider_family: PCIDriverKit
- expected_activation_model: System Extension / DriverKit dext
- activation_state_in_this_phase: NOT_ATTEMPTED

## DriverKit Skeleton Preconditions

DRIVERKIT_SKELETON_PRECONDITIONS:

1. Apple DriverKit / PCIDriverKit entitlement requirements must be documented.
2. Team ID / signing identity requirements must be documented.
3. System Extension install, activation, and deactivation path must be reversible.
4. Device matching must be static-manifest-only in this phase.
5. No provider open, MMIO mapping, BAR access, firmware load, GPU reset, framebuffer init, display engine init, or command submission is allowed.
6. All future runtime actions must remain gated by explicit evidence-level promotion.

## Future UI Compositor Evidence Path

FUTURE_UI_COMPOSITOR_EVIDENCE_PATH:

1. DriverKit skeleton feasibility
2. Reversible System Extension activation planning
3. Read-only PCI provider matching
4. Runtime probe with explicit no-write policy
5. Real GPU command execution proof
6. WindowServer / Core Animation / QuartzCore attribution research
7. UI compositor proof
8. Metal proof

## Current Contract State

- PHASE4_DRIVERKIT_SKELETON_FEASIBILITY_READY: True
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
