# Dext Load / Provider Match Proof Schema

## Purpose

This Phase 24 contract defines the proof schema for future H1mekaRTX dext load and provider match evidence.

This phase does not load a dext.

This phase does not execute activation or deactivation.

This phase does not open a provider, map BAR memory, mutate BAR/MMIO, or submit GPU commands.

This phase defines what future evidence must exist before claiming:

- dext load proof
- System Extension registered/enabled proof
- provider match proof
- RTX 5070 PCI provider candidate proof

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

All Phase 24 outputs must be labeled only as:

- CLASSIFICATION_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA
- CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS
- CLASSIFICATION_ACTIVATION_EXECUTION_GATE
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
- System Extension deactivation success
- dext load success
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

- DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_ONLY: True
- PROOF_SCHEMA_ONLY: True
- READ_ONLY_STATUS_EVIDENCE_ONLY: True
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

## Future Required Evidence

FUTURE_DEXT_LOAD_EVIDENCE_REQUIREMENTS:

1. systemextensionsctl list shows expected extension identifier
2. systemextensionsctl list shows expected team identifier
3. systemextensionsctl list shows enabled/activated state
4. sysextd logs show registration result
5. host app bundle path contains Contents/Library/SystemExtensions
6. dext bundle identifier matches expected identifier
7. signing identity and entitlement evidence match the activated dext
8. activation/deactivation rollback remains available

FUTURE_PROVIDER_MATCH_EVIDENCE_REQUIREMENTS:

1. target vendor_id is 0x10de
2. target device_id is 0x2f04
3. target io_pci_match is 0x2f0410de
4. expected provider class is IOPCIDevice
5. expected driver family is PCIDriverKit
6. expected PCI transport entitlement is present
7. provider match is observed without provider open
8. provider match is observed without BAR mapping
9. provider match is observed without GPU command submission

## Proof States

VALID_PROOF_STATES:

- NOT_ATTEMPTED
- BLOCKED
- CANDIDATE_OBSERVED
- PROVEN

Current expected state:

- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED

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

## Schema Files

DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_FILES:

- tools/driverkit-activation/dext-load-provider-match-proof-schema.json
- scripts/check-dext-load-provider-match-proof-schema.py
- scripts/run-dext-load-provider-match-proof-schema.sh

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Dext load proof and provider match proof are still not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. real GPU command execution evidence exists
4. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
5. UI compositor proof schema is satisfied
6. Metal proof schema is satisfied

## Current Contract State

- PHASE24_DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_READY: True
- DEXT_LOAD_PROVIDER_MATCH_PROOF_SCHEMA_ONLY: True
- PROOF_SCHEMA_ONLY: True
- READ_ONLY_STATUS_EVIDENCE_ONLY: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
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
