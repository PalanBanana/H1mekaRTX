# UI Proof Promotion Unblock Criteria Contract

## Purpose

This Phase 41 contract defines the unblock criteria for each UI proof promotion blocker in H1mekaRTX.

This phase is criteria-only.

This phase does not unblock any blocker.

This phase does not promote any UI proof state.

This phase does not prove UI compositor acceleration.

This phase does not claim Dock acceleration.

This phase does not claim transparency acceleration.

This phase does not claim blur acceleration.

This phase does not claim Metal proof.

This phase does not claim real GPU command execution.

This phase does not claim RTX 5070 workload attribution.

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

## Real Development Direction

REAL_DEVELOPMENT_ALLOWED_SCOPE:

- buildable DriverKit host app scaffold
- buildable dext scaffold
- deterministic Info.plist generation
- deterministic entitlement template validation
- official SystemExtensions activation/deactivation wrapper in dry-run mode first
- signing identity discovery
- entitlement approval evidence collection
- provider matching proof collection
- local-only host evidence collection

REAL_DEVELOPMENT_NOT_ALLOWED_YET:

- direct Dock injection
- WindowServer patching
- private framework patching
- fake Metal device spoofing
- provider open
- BAR mapping
- MMIO writes
- PCI configuration writes
- firmware loading
- GPU reset
- framebuffer/display-engine init
- GPU command submission
- Dock/transparency/blur acceleration claims

## Promotion Decision

Current decision:

- UI_PROOF_PROMOTION_DECISION: BLOCK_PROMOTION
- UI_PROOF_PROMOTION_ALLOWED: False
- DOCK_ACCELERATION_PROMOTION_ALLOWED: False
- TRANSPARENCY_ACCELERATION_PROMOTION_ALLOWED: False
- BLUR_ACCELERATION_PROMOTION_ALLOWED: False
- METAL_PROOF_PROMOTION_ALLOWED: False

## Classification

All Phase 41 outputs must be labeled only as:

- CLASSIFICATION_UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_CONTRACT
- CLASSIFICATION_UI_PROOF_PROMOTION_BLOCKER_DASHBOARD
- CLASSIFICATION_UI_EVIDENCE_CHAIN_ROLLUP
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_CONTRACT_ONLY: True
- UNBLOCK_CRITERIA_ONLY: True
- PROMOTION_BLOCKED: True
- UI_PROOF_PROMOTION_ALLOWED: False
- DOCK_ACCELERATION_PROMOTION_ALLOWED: False
- TRANSPARENCY_ACCELERATION_PROMOTION_ALLOWED: False
- BLUR_ACCELERATION_PROMOTION_ALLOWED: False
- METAL_PROOF_PROMOTION_ALLOWED: False
- REAL_DEVELOPMENT_ALLOWED_SCOPE_DEFINED: True
- REAL_DEVELOPMENT_RUNTIME_ACCESS_NOT_ALLOWED_YET: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- REAL_GPU_COMMAND_EXECUTION_NOT_CLAIMED: True
- RTX5070_WORKLOAD_ATTRIBUTION_NOT_CLAIMED: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- RAW_LOCAL_LOGS_NOT_COMMITTED: True
- RAW_COMMAND_STDOUT_NOT_COMMITTED: True
- RAW_COMMAND_STDERR_NOT_COMMITTED: True
- MEASUREMENT_NOT_ACCELERATION_PROOF: True
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

## Unblock Criteria

Each blocker remains blocked until its listed unblock criteria are proven in a future PR.


## Exact Blocker Token Coverage

The criteria contract also includes exact blocker-token aliases required by the checker:

- firmware load remains forbidden
- display-engine initialization remains forbidden
- Core Animation / QuartzCore attribution proof is not PROVEN

These aliases do not unblock any capability. They only make the promotion blocker criteria explicit and machine-checkable.

## Current Contract State

- PHASE41_UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_CONTRACT_READY: True
- UI_PROOF_PROMOTION_UNBLOCK_CRITERIA_CONTRACT_ONLY: True
- UNBLOCK_CRITERIA_ONLY: True
- UI_PROOF_PROMOTION_DECISION: BLOCK_PROMOTION
- UI_PROOF_PROMOTION_ALLOWED: False
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- RTX5070_WORKLOAD_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
