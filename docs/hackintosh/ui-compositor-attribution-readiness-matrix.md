# UI Compositor Attribution Readiness Matrix

## Purpose

This Phase 6 contract defines the evidence matrix required before H1mekaRTX may claim that RTX 5070 is contributing to macOS UI compositor acceleration.

The target user-visible behavior remains:

- Smooth Dock animation
- Smooth Dock magnification
- Working transparency
- Working blur
- Smooth window movement
- Smooth window resizing
- Smooth Mission Control
- Smooth Launchpad
- Smooth Stage Manager
- Smooth menu bar and Dock translucent effects

The target graphics path remains:

- WindowServer
- Core Animation
- QuartzCore
- Metal compositor
- IOGraphics
- IOAccelerator
- IODisplay
- RTX 5070 workload attribution

## Classification

All Phase 6 outputs must be labeled only as:

- CLASSIFICATION_UI_COMPOSITOR_ATTRIBUTION_READINESS
- CLASSIFICATION_GRAPHICS_STACK_DIAGNOSTICS
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- real RTX 5070 UI acceleration
- real Metal proof
- real GPU command execution
- workload attribution success
- Dock acceleration success
- transparency acceleration success
- blur acceleration success

## Safety Boundary

Required safety markers:

- OBSERVATION_ONLY: True
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

## Attribution Readiness Requirements

UI_COMPOSITOR_ATTRIBUTION_REQUIREMENTS:

1. WindowServer visibility must be captured.
2. Core Animation / QuartzCore path evidence must be represented.
3. Metal compositor or Metal device visibility must be represented.
4. IOGraphics / IOAccelerator / IODisplay hints must be represented.
5. RTX 5070 PCI identity must be known from earlier host diagnostics.
6. Real GPU command execution must remain NOT_ATTEMPTED in this phase.
7. Workload attribution must remain UNPROVEN in this phase.
8. UI compositor proof must remain UNPROVEN in this phase.
9. Metal proof must remain UNPROVEN in this phase.
10. Future promotion requires frame timing, compositor routing, workload attribution, and command execution evidence.

## Required Matrix Rows

UI_COMPOSITOR_ATTRIBUTION_MATRIX_ROWS:

- WindowServer process visibility
- Core Animation / QuartzCore evidence path
- Metal compositor visibility
- IOGraphics / IOAccelerator / IODisplay hints
- RTX 5070 PCI identity
- Dock smoothness target
- transparency target
- blur target
- window movement target
- Mission Control target
- Launchpad target
- Stage Manager target
- workload attribution blocker
- real GPU command execution blocker
- UI compositor proof blocker
- Metal proof blocker

## Current Contract State

- PHASE6_UI_COMPOSITOR_ATTRIBUTION_READINESS_READY: True
- ATTRIBUTION_READINESS_MATRIX_ONLY: True
- OBSERVATION_ONLY: True
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
