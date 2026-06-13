# UI Compositor Scenario Matrix

## Purpose

This Phase 33 contract defines the UI compositor scenario matrix for H1mekaRTX.

This phase is matrix-only.

This phase does not prove UI compositor acceleration.

This phase does not claim Dock acceleration.

This phase does not claim transparency acceleration.

This phase does not claim blur acceleration.

This phase does not claim Mission Control acceleration.

This phase does not claim Launchpad acceleration.

This phase does not claim Stage Manager acceleration.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not write PCI configuration space.

This phase does not read or write MMIO.

This phase does not submit GPU commands.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not load a dext.

This phase does not execute activation or deactivation.

## Long-Term UI Goal

The long-term user-visible goal remains Hackintosh macOS UI compositor acceleration research:

- Dock smoothness
- Dock magnification
- transparency
- blur
- menu bar translucency
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager
- desktop space switching
- WindowServer / Core Animation / QuartzCore / Metal compositor evidence path

## Classification

All Phase 33 outputs must be labeled only as:

- CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX
- CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA
- CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- UI_COMPOSITOR_SCENARIO_MATRIX_ONLY: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
- SCENARIO_MATRIX_ONLY: True
- OBJECTIVE_METRICS_REQUIRED: True
- BEFORE_AFTER_BASELINE_REQUIRED: True
- WINDOWSERVER_ATTRIBUTION_REQUIRED: True
- CORE_ANIMATION_QUARTZCORE_EVIDENCE_REQUIRED: True
- METAL_COMPOSITOR_EVIDENCE_REQUIRED: True
- REAL_GPU_COMMAND_EVIDENCE_REQUIRED: True
- RTX5070_WORKLOAD_ATTRIBUTION_REQUIRED: True
- FIRMWARE_LOAD_FORBIDDEN: True
- GPU_RESET_FORBIDDEN: True
- FRAMEBUFFER_INIT_FORBIDDEN: True
- DISPLAY_ENGINE_INIT_FORBIDDEN: True
- GPU_COMMAND_SUBMISSION_FORBIDDEN: True
- CONFIGURATION_WRITES_FORBIDDEN: True
- BAR_MAPPING_FORBIDDEN: True
- BAR_MMIO_MUTATION_FORBIDDEN: True
- PROVIDER_OPEN_FORBIDDEN: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
- NO_SYSTEM_EXTENSION_DEACTIVATION: True
- NO_DEXT_LOAD: True
- NO_PROVIDER_OPEN: True
- NO_BAR_MAPPING: True
- NO_BAR_MMIO_MUTATION: True
- NO_CONFIGURATION_WRITES: True
- NO_COMMAND_SUBMISSION: True
- NO_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_FRAMEBUFFER_INIT: True
- NO_DISPLAY_ENGINE_INIT: True
- NO_DIRECT_DOCK_INJECTION: True
- NO_WINDOWSERVER_PATCHING: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True

## Scenario Matrix

UI_COMPOSITOR_SCENARIOS:

1. Dock magnification
2. Dock hide/show
3. transparency
4. blur
5. menu bar translucency
6. window movement
7. window resizing
8. Mission Control
9. Launchpad
10. Stage Manager
11. desktop space switching

## Per-Scenario Required Evidence

Each scenario requires:

- repeatable interaction procedure
- before baseline
- after candidate run
- objective frame pacing metric
- objective latency metric
- screen recording or trace artifact reference
- WindowServer attribution evidence
- Core Animation / QuartzCore evidence
- Metal compositor evidence
- real GPU command evidence
- RTX 5070 workload attribution evidence
- rollback evidence
- no spoofing / no patching evidence

## Current Proof States

- UI_COMPOSITOR_SCENARIO_MATRIX_STATE: MATRIX_ONLY
- UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- DOCK_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- TRANSPARENCY_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- BLUR_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- MISSION_CONTROL_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- LAUNCHPAD_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- STAGE_MANAGER_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- RTX5070_WORKLOAD_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED

## Dependency Chain

UI_COMPOSITOR_SCENARIO_MATRIX_DEPENDENCY_CHAIN:

1. activation prerequisites ledger READY
2. activation execution gate allows execute in a future reviewed phase
3. dext load proof PROVEN
4. provider match proof PROVEN
5. provider-open policy authorized
6. BAR mapping policy authorized
7. PCI configuration write policy authorized
8. firmware/reset/display-init policy authorized
9. real GPU command execution proof PROVEN
10. RTX 5070 workload attribution proof PROVEN
11. WindowServer attribution proof PROVEN
12. Core Animation / QuartzCore compositor proof PROVEN
13. Metal compositor proof PROVEN
14. before/after scenario matrix complete
15. UI compositor proof may be evaluated

## Current Contract State

- PHASE33_UI_COMPOSITOR_SCENARIO_MATRIX_READY: True
- UI_COMPOSITOR_SCENARIO_MATRIX_ONLY: True
- SCENARIO_MATRIX_ONLY: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
- UI_COMPOSITOR_SCENARIO_MATRIX_STATE: MATRIX_ONLY
- UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- DOCK_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- TRANSPARENCY_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- BLUR_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- MISSION_CONTROL_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- LAUNCHPAD_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- STAGE_MANAGER_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_STATE: ENFORCED
- GPU_COMMAND_SUBMISSION_PROHIBITION_STATE: ENFORCED
- CONFIG_WRITE_PROHIBITION_STATE: ENFORCED
- BAR_MAPPING_PROHIBITION_STATE: ENFORCED
- PROVIDER_OPEN_PROHIBITION_STATE: ENFORCED
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
