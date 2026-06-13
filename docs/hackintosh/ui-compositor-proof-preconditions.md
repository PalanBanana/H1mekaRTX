# UI Compositor Proof Precondition Schema

## Purpose

This Phase 32 contract defines the proof preconditions required before H1mekaRTX may claim macOS UI compositor acceleration for RTX 5070.

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

The real injection equivalent for this project remains official DriverKit / System Extension activation through the SystemExtensions framework in a later phase, after the activation prerequisites ledger is READY.

This project must never use kernel memory injection, process injection, SIP/AMFI bypass, private framework patching, fake Metal device spoofing, direct Dock injection, or WindowServer patching.

## Long-Term UI Goal

The long-term user-visible goal remains Hackintosh macOS UI compositor acceleration research:

- Dock smoothness
- Dock magnification
- transparency
- blur
- window movement
- window resizing
- Mission Control
- Launchpad
- Stage Manager
- WindowServer / Core Animation / QuartzCore / Metal compositor evidence path

## Classification

All Phase 32 outputs must be labeled only as:

- CLASSIFICATION_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA
- CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE
- CLASSIFICATION_GPU_COMMAND_SUBMISSION_PROHIBITION_GATE
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
- System Extension deactivation success
- dext load success
- provider match proof
- provider open success
- BAR mapping success
- MMIO access success
- PCI configuration write success
- firmware load success
- GPU reset success
- framebuffer init success
- display-engine init success
- real GPU command execution
- RTX 5070 workload attribution
- UI compositor proof
- Metal proof
- Dock acceleration success
- transparency acceleration success
- blur acceleration success

## Safety Boundary

Required safety markers:

- UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA_ONLY: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
- FIRMWARE_LOAD_FORBIDDEN: True
- GPU_RESET_FORBIDDEN: True
- FRAMEBUFFER_INIT_FORBIDDEN: True
- DISPLAY_ENGINE_INIT_FORBIDDEN: True
- GPU_COMMAND_SUBMISSION_FORBIDDEN: True
- CONFIGURATION_WRITES_FORBIDDEN: True
- BAR_MAPPING_FORBIDDEN: True
- BAR_MMIO_MUTATION_FORBIDDEN: True
- MEMORY_DESCRIPTOR_MAPPING_FORBIDDEN: True
- PROVIDER_OPEN_FORBIDDEN: True
- PROVIDER_MATCH_PROOF_NOT_CLAIMED: True
- CANDIDATE_SUMMARY_ONLY: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
- NO_SYSTEM_EXTENSION_DEACTIVATION: True
- NO_DEXT_LOAD: True
- NO_DEVICE_OWNERSHIP_REQUEST: True
- NO_PROVIDER_OPEN: True
- NO_BAR_MAPPING: True
- NO_BAR_MMIO_MUTATION: True
- NO_CONFIGURATION_WRITES: True
- NO_MEMORY_DESCRIPTOR_MAPPING: True
- NO_COMMAND_SUBMISSION: True
- NO_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_FRAMEBUFFER_INIT: True
- NO_DISPLAY_ENGINE_INIT: True
- NO_MODESET: True
- NO_SCANOUT_INIT: True
- NO_METAL_COMMAND_QUEUE: True
- NO_METAL_COMMAND_BUFFER: True
- NO_METAL_COMMAND_ENCODER: True
- NO_METAL_COMMAND_COMMIT: True
- NO_KERNEL_OR_PROCESS_INJECTION: True
- NO_SIP_AMFI_BYPASS: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True
- NO_DIRECT_DOCK_INJECTION: True
- NO_WINDOWSERVER_PATCHING: True

## Required Proof Preconditions

UI_COMPOSITOR_PROOF_REQUIRED_PRECONDITIONS:

1. dext load proof is PROVEN
2. provider match proof is PROVEN
3. provider-open policy is separately reviewed and authorized
4. BAR mapping policy is separately reviewed and authorized
5. PCI configuration write policy is separately reviewed and authorized
6. firmware/reset/display-init policy is separately reviewed and authorized
7. real GPU command execution proof is PROVEN
8. RTX 5070 workload attribution proof is PROVEN
9. WindowServer attribution evidence is present
10. Core Animation / QuartzCore compositor evidence is present
11. Metal compositor evidence is present
12. before/after baseline comparison is present
13. repeatable UI interaction scenario is present
14. objective frame pacing or latency metric is present
15. rollback evidence is present
16. no fake Metal device spoofing evidence is present
17. no private framework patching evidence is present
18. no WindowServer patching evidence is present

## Required UI Scenarios

UI_COMPOSITOR_REQUIRED_SCENARIOS:

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
- expose-style animation
- desktop space switching

## Required Evidence Buckets

UI_COMPOSITOR_REQUIRED_EVIDENCE_BUCKETS:

- system extension activation state
- dext load proof
- provider match proof
- GPU command execution proof
- RTX 5070 workload attribution
- WindowServer process attribution
- Core Animation / QuartzCore compositor path
- Metal command execution path
- display/compositor frame pacing
- before/after baseline
- rollback/deactivation evidence

## Valid Proof States

VALID_UI_COMPOSITOR_PROOF_STATES:

- NOT_ATTEMPTED
- BLOCKED
- PRECONDITIONS_INCOMPLETE
- CANDIDATE_OBSERVED
- PROVEN

Current expected state:

- UI_COMPOSITOR_PROOF_PRECONDITION_STATE: PRECONDITIONS_INCOMPLETE
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- DOCK_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- TRANSPARENCY_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- BLUR_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- MISSION_CONTROL_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- LAUNCHPAD_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED
- STAGE_MANAGER_ACCELERATION_PROOF_STATE: NOT_ATTEMPTED

## Gate Dependency Chain

UI_COMPOSITOR_PROOF_DEPENDENCY_CHAIN:

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
11. compositor attribution proof PROVEN
12. UI compositor proof PROVEN
13. Metal proof PROVEN
14. Dock/transparency/blur proof may be evaluated

## Target PCI Provider Matching Manifest

TARGET_PCI_PROVIDER_MATCHING_MANIFEST:

- target_gpu: NVIDIA RTX 5070
- architecture_family: NVIDIA Blackwell
- vendor_id: 0x10de
- device_id: 0x2f04
- io_pci_match: 0x2f0410de
- expected_provider_class: IOPCIDevice
- expected_driver_family: PCIDriverKit
- expected_pci_transport_entitlement: com.apple.developer.driverkit.transport.pci
- expected_system_extension_entitlement: com.apple.developer.system-extension.install
- expected_dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- expected_host_bundle_id: dev.h1meka.H1mekaRTXHost

## Current Contract State

- PHASE32_UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA_READY: True
- UI_COMPOSITOR_PROOF_PRECONDITION_SCHEMA_ONLY: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True
- LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True
- STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True
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
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False
- DEXT_LOAD_ATTEMPTED: False
- DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- MEMORY_DESCRIPTOR_MAPPING_ATTEMPTED: False
- GPU_COMMAND_QUEUE_ATTEMPTED: False
- GPU_COMMAND_BUFFER_ATTEMPTED: False
- GPU_COMMAND_ENCODER_ATTEMPTED: False
- GPU_COMMAND_COMMIT_ATTEMPTED: False
- FIRMWARE_LOAD_ATTEMPTED: False
- GPU_RESET_ATTEMPTED: False
- FRAMEBUFFER_INIT_ATTEMPTED: False
- DISPLAY_ENGINE_INIT_ATTEMPTED: False
- MODESET_ATTEMPTED: False
- SCANOUT_INIT_ATTEMPTED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
