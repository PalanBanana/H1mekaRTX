# Hackintosh UI Compositor Observability Baseline Contract

## Purpose

This Phase 5 contract defines a safe Hackintosh UI compositor observability baseline.

This is the first phase that explicitly targets the user-visible Hackintosh desktop behavior:

- Dock smoothness
- Dock magnification
- transparency
- blur
- shadows
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager
- menu bar / Dock translucent effects

The technical observation path is:

- WindowServer
- Core Animation
- QuartzCore
- Metal compositor
- IOGraphics
- IOAccelerator
- IODisplay
- Metal device visibility

## Important Boundary

This phase observes the current Hackintosh graphics/UI state.

This phase does not claim:

- RTX 5070 workload attribution
- real GPU command execution
- UI compositor proof
- Metal proof
- Dock acceleration proof
- transparency acceleration proof
- blur acceleration proof

## Classification

All outputs must be labeled only as:

- CLASSIFICATION_HACKINTOSH_UI_OBSERVABILITY_BASELINE
- CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS
- CLASSIFICATION_STATIC_CONTRACT

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
- OBSERVATION_ONLY: True

## Hackintosh UI Baseline Evidence Checklist

HACKINTOSH_UI_BASELINE_EVIDENCE_CHECKLIST:

1. Capture macOS version, kernel version, architecture, and SIP state.
2. Capture display/graphics state using system_profiler when available.
3. Capture WindowServer process visibility.
4. Capture IOGraphics / IODisplay / IOAccelerator / Metal-related IORegistry hints when available.
5. Capture Metal device visibility if a safe local command or sample tool exists.
6. Capture current UI compositor target checklist:
   - Dock
   - transparency
   - blur
   - window movement
   - window resizing
   - Mission Control
   - Launchpad
   - Stage Manager
7. Preserve the conclusion that attribution remains UNPROVEN until later evidence gates.

## Future Promotion Gate

This baseline may promote to UI compositor proof only after later phases provide evidence for:

1. real GPU command execution
2. device/workload attribution
3. WindowServer/Core Animation/QuartzCore/Metal compositor routing
4. frame timing or GPU-backed workload evidence
5. no fake Metal device spoofing

## Current Contract State

- PHASE5_HACKINTOSH_UI_OBSERVABILITY_BASELINE_READY: True
- HACKINTOSH_UI_BASELINE_OBSERVATION_ONLY: True
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
