# Local Read-Only UI Baseline Collector

## Purpose

This Phase 36 contract defines a local read-only UI baseline collector for H1mekaRTX.

This phase collects local host baseline information for WindowServer, display, Dock, Core Animation, QuartzCore, and Metal-adjacent observability.

This phase is baseline-collection-only.

This phase stores local machine-specific output in host-report-bundle.

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

## Safe Local Read-Only Commands

LOCAL_READONLY_UI_BASELINE_COMMANDS:

- sw_vers
- uname -a
- system_profiler SPDisplaysDataType -json
- system_profiler SPHardwareDataType -json
- ioreg -r -c IODisplayConnect -l -w0
- ioreg -r -c IOFramebuffer -l -w0
- ps -axo pid,ppid,comm,args
- log show --last 5m --style compact --predicate process == "WindowServer"
- log show --last 5m --style compact --predicate process == "Dock"

These commands are read-only/status-only.

The log command is used only for local baseline observation.

## Local Output Policy

LOCAL_OUTPUTS_IGNORED_BY_GIT:

- host-report-bundle/ui-baseline/local-readonly-ui-baseline.json
- host-report-bundle/ui-baseline/local-readonly-ui-baseline.md

The host-report-bundle output is intentionally local-only and must not be force-added to git.

COMMITTED_CHECK_OUTPUTS:

- release-readiness/local-readonly-ui-baseline-check.json
- release-readiness/local-readonly-ui-baseline-check.md

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

All Phase 36 outputs must be labeled only as:

- CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR
- CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA
- CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- LOCAL_READONLY_UI_BASELINE_COLLECTOR_ONLY: True
- LOCAL_BASELINE_ONLY: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- MEASUREMENT_NOT_ACCELERATION_PROOF: True
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

## Baseline Buckets

LOCAL_READONLY_UI_BASELINE_BUCKETS:

1. OS version
2. kernel version
3. hardware model
4. display inventory
5. framebuffer inventory
6. WindowServer process visibility
7. Dock process visibility
8. recent WindowServer unified log visibility
9. recent Dock unified log visibility
10. local baseline artifact references

## Current Proof States

- LOCAL_READONLY_UI_BASELINE_STATE: COLLECTED_OR_UNAVAILABLE
- UI_FRAME_PACING_LATENCY_METRIC_SCHEMA_STATE: SCHEMA_ONLY
- UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED
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
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- RTX5070_WORKLOAD_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED

## Current Contract State

- PHASE36_LOCAL_READONLY_UI_BASELINE_COLLECTOR_READY: True
- LOCAL_READONLY_UI_BASELINE_COLLECTOR_ONLY: True
- LOCAL_BASELINE_ONLY: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- MEASUREMENT_NOT_ACCELERATION_PROOF: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- LOCAL_READONLY_UI_BASELINE_STATE: COLLECTED_OR_UNAVAILABLE
- UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED
- WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
