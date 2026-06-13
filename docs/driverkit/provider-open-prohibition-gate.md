# Provider Open Prohibition Gate

## Purpose

This Phase 27 contract defines a provider-open prohibition gate for H1mekaRTX.

This phase blocks provider open paths before any real DriverKit / PCIDriverKit provider interaction is allowed.

This phase does not open a provider.

This phase does not prove provider match.

This phase does not load a dext.

This phase does not execute activation or deactivation.

This phase does not map BAR memory, mutate BAR/MMIO, or submit GPU commands.

This phase audits runtime activation and provider-candidate artifacts for forbidden provider open and hardware access markers.

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

All Phase 27 outputs must be labeled only as:

- CLASSIFICATION_PROVIDER_OPEN_PROHIBITION_GATE
- CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_SUMMARY_GATE
- CLASSIFICATION_PROVIDER_MATCH_CANDIDATE_COLLECTOR
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

- PROVIDER_OPEN_PROHIBITION_GATE_ONLY: True
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
- NO_IOPCIDEVICE_OPEN: True
- NO_IOSERVICE_OPEN: True
- NO_BAR_MAPPING: True
- NO_BAR_MMIO_MUTATION: True
- NO_CONFIGURATION_WRITES: True
- NO_MEMORY_DESCRIPTOR_MAPPING: True
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

## Forbidden Provider Open Markers

FORBIDDEN_PROVIDER_OPEN_MARKERS:

- IOPCIDevice open API
- IOPCIDevice C++ open API
- IOPCIDevice open symbol
- provider open call
- provider open helper
- provider open invocation
- IOService open API
- IOConnect call method API
- IOConnect map memory API
- IOConnect notification-port API

## Forbidden Hardware Access Markers

FORBIDDEN_HARDWARE_ACCESS_MARKERS:

- map device memory API
- map device memory API
- create memory descriptor API
- configuration write 8-bit API
- configuration write 16-bit API
- configuration write 32-bit API
- memory write API
- write memory API
- submit commands API
- submit commands API
- command submission API
- GPU command API
- GSP firmware API
- GPU reset API
- framebuffer init API
- display engine init API

## Audit Scope

PROVIDER_OPEN_PROHIBITION_AUDIT_SCOPE:

Runtime activation and provider candidate artifacts only:

- tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift
- scripts/collect-provider-match-candidate.py
- tools/driverkit-activation/provider-match-candidate-collector-plan.json
- tools/driverkit-activation/provider-match-candidate-summary-gate.json
- tools/driverkit-activation/dext-load-provider-match-proof-schema.json
- tools/driverkit-activation/activation-execution-gate.json

Static checker scripts, docs, and generated reports are intentionally excluded from marker scanning because they may contain explanatory blocked provider-open wording without creating an executable provider-open path.

## Gate Rule

PROVIDER_OPEN_PROHIBITION_GATE_RULE:

1. Provider open remains forbidden.
2. IOPCIDevice open API remains forbidden.
3. IOService open API remains forbidden.
4. BAR mapping remains forbidden.
5. BAR/MMIO mutation remains forbidden.
6. Configuration writes remain forbidden.
7. GPU command submission remains forbidden.
8. Candidate observation is not provider match proof.
9. Provider match proof remains NOT_ATTEMPTED.
10. Dext load proof remains NOT_ATTEMPTED.

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

## Proof State

Current expected state:

- PROVIDER_OPEN_PROHIBITION_STATE: ENFORCED
- PROVIDER_MATCH_CANDIDATE_SUMMARY_STATE: SUMMARY_ONLY
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Provider-open prohibition is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. provider open is separately reviewed and authorized in a future phase
4. BAR mapping policy is separately reviewed and authorized in a future phase
5. real GPU command execution evidence exists
6. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
7. UI compositor proof schema is satisfied
8. Metal proof schema is satisfied

## Current Contract State

- PHASE27_PROVIDER_OPEN_PROHIBITION_GATE_READY: True
- PROVIDER_OPEN_PROHIBITION_GATE_ONLY: True
- PROVIDER_OPEN_FORBIDDEN: True
- PROVIDER_MATCH_PROOF_NOT_CLAIMED: True
- CANDIDATE_SUMMARY_ONLY: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE
- PROVIDER_OPEN_PROHIBITION_STATE: ENFORCED
- PROVIDER_MATCH_CANDIDATE_SUMMARY_STATE: SUMMARY_ONLY
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
- IOPCIDEVICE_OPEN_ATTEMPTED: False
- IOSERVICE_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- MEMORY_DESCRIPTOR_MAPPING_ATTEMPTED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
