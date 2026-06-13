# Provider Match Candidate Collector

## Purpose

This Phase 25 contract defines a read-only provider match candidate collector for H1mekaRTX.

This phase does not open a provider.

This phase does not load a dext.

This phase does not execute activation or deactivation.

This phase does not map BAR memory, mutate BAR/MMIO, or submit GPU commands.

This phase may read local I/O Registry PCI device information and compare it to the expected RTX 5070 provider matching manifest.

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

All Phase 25 outputs must be labeled only as:

- CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_COLLECTOR
- CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA
- CLASSIFICATION_ACTIVATION_EXECUTION_GATE
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
- real GPU command execution
- RTX 5070 workload attribution
- UI compositor proof
- Metal proof
- Dock acceleration success
- transparency acceleration success
- blur acceleration success

## Safety Boundary

Required safety markers:

- PROVIDER_MATCH_CANDIDATE_COLLECTOR_ONLY: True
- READ_ONLY_PROVIDER_CANDIDATE_COLLECTION_ONLY: True
- CANDIDATE_REPORT_ONLY: True
- PROVIDER_MATCH_PROOF_NOT_CLAIMED: True
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
- NO_COMMAND_SUBMISSION: True
- NO_GSP_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_FRAMEBUFFER_INIT: True
- NO_DISPLAY_ENGINE_INIT: True
- NO_KERNEL_OR_PROCESS_INJECTION: True
- NO_SIP_AMFI_BYPASS: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True
- NO_DIRECT_DOCK_INJECTION: True
- NO_WINDOWSERVER_PATCHING: True

## Safe Read-Only Commands

SAFE_PROVIDER_MATCH_CANDIDATE_COMMANDS:

- ioreg -r -c IOPCIDevice -l
- ioreg -r -c IOPCIDevice -l -w0
- system_profiler SPPCIDataType
- sw_vers
- uname -a

These commands are status-only.

## Candidate Matching Rules

PROVIDER_MATCH_CANDIDATE_RULES:

1. target vendor_id is 0x10de
2. target device_id is 0x2f04
3. target io_pci_match is 0x2f0410de
4. expected provider class is IOPCIDevice
5. expected driver family is PCIDriverKit
6. candidate observation is not proof
7. provider open remains forbidden
8. BAR mapping remains forbidden
9. GPU command submission remains forbidden

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

## Output Policy

LOCAL_PROVIDER_CANDIDATE_OUTPUTS_IGNORED:

- host-report-bundle/provider-match-candidate/provider-match-candidate-report.json
- host-report-bundle/provider-match-candidate/provider-match-candidate-report.md

The host-report-bundle output is intentionally local-only and should not be force-added to git.

COMMITTED_CHECK_OUTPUTS:

- release-readiness/provider-match-candidate-collector-check.json
- release-readiness/provider-match-candidate-collector-check.md

## Proof State

Current expected state:

- PROVIDER_MATCH_CANDIDATE_STATE: CANDIDATE_COLLECTION_ONLY
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Provider candidate observation is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. real GPU command execution evidence exists
4. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
5. UI compositor proof schema is satisfied
6. Metal proof schema is satisfied

## Current Contract State

- PHASE25_PROVIDER_MATCH_CANDIDATE_COLLECTOR_READY: True
- PROVIDER_MATCH_CANDIDATE_COLLECTOR_ONLY: True
- READ_ONLY_PROVIDER_CANDIDATE_COLLECTION_ONLY: True
- CANDIDATE_REPORT_ONLY: True
- PROVIDER_MATCH_PROOF_NOT_CLAIMED: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE
- PROVIDER_MATCH_CANDIDATE_STATE: CANDIDATE_COLLECTION_ONLY
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
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
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
