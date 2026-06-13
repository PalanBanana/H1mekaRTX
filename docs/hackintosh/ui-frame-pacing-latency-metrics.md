# UI Frame Pacing / Latency Metric Schema

## Purpose

This Phase 35 contract defines the before/after frame pacing and latency metric schema for H1mekaRTX UI compositor research.

This phase is metric-schema-only.

This phase does not measure real acceleration.

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

All Phase 35 outputs must be labeled only as:

- CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA
- CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA
- CLASSIFICATION_UI_COMPOSITOR_SCENARIO_MATRIX
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_ONLY: True
- METRIC_SCHEMA_ONLY: True
- MEASUREMENT_NOT_COLLECTED: True
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

## Metric Buckets

UI_FRAME_PACING_LATENCY_METRIC_BUCKETS:

1. scenario identity
2. before baseline metric set
3. after candidate metric set
4. frame interval metric
5. average frame time metric
6. p50 frame time metric
7. p95 frame time metric
8. p99 frame time metric
9. dropped frame count
10. hitch count
11. latency metric
12. jitter metric
13. sample duration
14. sample source
15. screen refresh rate
16. WindowServer attribution reference
17. Core Animation / QuartzCore attribution reference
18. Metal compositor attribution reference
19. real GPU command evidence reference
20. RTX 5070 workload attribution reference
21. rollback reference

## Required Metric Fields

UI_FRAME_PACING_LATENCY_REQUIRED_FIELDS:

- scenario_name
- measurement_state
- baseline_reference
- candidate_reference
- sample_duration_seconds
- display_refresh_hz
- frame_interval_ms_average
- frame_interval_ms_p50
- frame_interval_ms_p95
- frame_interval_ms_p99
- frame_time_ms_average
- frame_time_ms_p50
- frame_time_ms_p95
- frame_time_ms_p99
- dropped_frame_count
- hitch_count
- latency_ms_average
- latency_ms_p95
- jitter_ms
- baseline_candidate_delta_percent
- trace_or_recording_reference
- WindowServer_attribution_reference
- Core_Animation_QuartzCore_attribution_reference
- Metal_compositor_attribution_reference
- real_GPU_command_evidence_reference
- RTX5070_workload_attribution_reference
- rollback_reference
- spoofing_or_patching_absent

## Required UI Scenarios

UI_FRAME_PACING_LATENCY_SCENARIOS:

- Dock magnification
- Dock hide/show
- transparency
- blur
- menu bar translucency
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager
- desktop space switching

## Valid Metric States

VALID_UI_FRAME_PACING_LATENCY_METRIC_STATES:

- NOT_ATTEMPTED
- BLOCKED
- SCHEMA_ONLY
- BASELINE_PENDING
- CANDIDATE_PENDING
- MEASURED
- ATTRIBUTED
- PROVEN

## Current Proof States

- UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_STATE: SCHEMA_ONLY
- UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED
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

UI_FRAME_PACING_LATENCY_DEPENDENCY_CHAIN:

1. UI compositor scenario matrix complete
2. WindowServer / Core Animation / QuartzCore attribution schema complete
3. baseline measurement procedure defined
4. candidate measurement procedure defined
5. objective metric fields complete
6. dext load proof PROVEN
7. provider match proof PROVEN
8. provider-open policy authorized
9. BAR mapping policy authorized
10. PCI configuration write policy authorized
11. firmware/reset/display-init policy authorized
12. real GPU command execution proof PROVEN
13. RTX 5070 workload attribution proof PROVEN
14. WindowServer attribution proof PROVEN
15. Core Animation / QuartzCore attribution proof PROVEN
16. Metal compositor attribution proof PROVEN
17. before/after metric delta may be evaluated

## Current Contract State

- PHASE35_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_READY: True
- UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_ONLY: True
- METRIC_SCHEMA_ONLY: True
- MEASUREMENT_NOT_COLLECTED: True
- UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_STATE: SCHEMA_ONLY
- UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
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
