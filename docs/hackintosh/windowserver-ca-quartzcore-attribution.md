# WindowServer / Core Animation / QuartzCore Attribution Schema

## Purpose

This Phase 34 contract defines the WindowServer, Core Animation, QuartzCore, and Metal compositor attribution schema for H1mekaRTX.

This phase is schema-only.

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

All Phase 34 outputs must be labeled only as:

- CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA
- CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX
- CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA_ONLY: True
- ATTRIBUTION_SCHEMA_ONLY: True
- WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
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

## Attribution Buckets

WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_BUCKETS:

1. WindowServer process observation
2. WindowServer compositor workload attribution
3. Core Animation transaction evidence
4. QuartzCore layer/compositor evidence
5. Metal drawable/compositor path evidence, including CAMetalLayer evidence
6. Metal command queue/buffer evidence
7. RTX 5070 workload attribution evidence
8. frame pacing evidence
9. latency evidence
10. before/after scenario evidence
11. rollback evidence
12. no spoofing/patching evidence

## Required Attribution Fields

WINDOWSERVER_ATTRIBUTION_REQUIRED_FIELDS:

- process_name
- process_identifier
- sample_or_trace_reference
- before_baseline_reference
- after_candidate_reference
- compositor_activity_observed
- rtx5070_workload_attribution_state
- real_gpu_command_execution_state
- ui_scenario_name
- frame_pacing_metric
- latency_metric
- rollback_reference
- spoofing_or_patching_absent

CORE_ANIMATION_QUARTZCORE_REQUIRED_FIELDS:

- ca_transaction_observed
- quartzcore_layer_activity_observed
- layer_tree_or_compositor_reference
- metal_layer_or_drawable_reference
- blended/transparency/blur evidence reference
- before_after_delta
- objective_metric_reference

METAL_COMPOSITOR_REQUIRED_FIELDS:

- metal_device_identity
- command_queue_reference
- command_buffer_reference
- command_execution_reference
- drawable_reference
- rtx5070_attribution_reference
- no_fake_metal_device_spoofing

## Valid Attribution States

VALID_ATTRIBUTION_STATES:

- NOT_ATTEMPTED
- BLOCKED
- PRECONDITIONS_INCOMPLETE
- CANDIDATE_OBSERVED
- ATTRIBUTED
- PROVEN

## Current Proof States

- WINDOWSERVER_ATTRIBUTION_SCHEMA_STATE: SCHEMA_ONLY
- WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- CORE_ANIMATION_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- QUARTZCORE_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
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

WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_DEPENDENCY_CHAIN:

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
12. Core Animation / QuartzCore attribution proof PROVEN
13. Metal compositor attribution proof PROVEN
14. before/after scenario matrix complete
15. UI compositor proof may be evaluated

## Current Contract State

- PHASE34_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA_READY: True
- WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA_ONLY: True
- ATTRIBUTION_SCHEMA_ONLY: True
- WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- WINDOWSERVER_ATTRIBUTION_SCHEMA_STATE: SCHEMA_ONLY
- WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- CORE_ANIMATION_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- QUARTZCORE_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_SCENARIO_MATRIX_STATE: MATRIX_ONLY
- UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
