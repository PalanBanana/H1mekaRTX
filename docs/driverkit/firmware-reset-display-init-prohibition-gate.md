# Firmware / Reset / Display Init Prohibition Gate

## Purpose

This Phase 31 contract defines a firmware, reset, framebuffer, and display-engine initialization prohibition gate for H1mekaRTX.

This phase blocks firmware loading, GPU reset, framebuffer initialization, display-engine initialization, modeset, scanout, and display pipeline initialization paths before any real GPU bring-up work is allowed.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not write PCI configuration space.

This phase does not read or write MMIO.

This phase does not submit GPU commands.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize a framebuffer.

This phase does not initialize a display engine.

This phase does not load a dext.

This phase does not execute activation or deactivation.

This phase audits runtime activation and provider-candidate artifacts for forbidden firmware, reset, framebuffer, display pipeline, modeset, and scanout marker families.

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

All Phase 31 outputs must be labeled only as:

- CLASSIFICATION_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE
- CLASSIFICATION_GPU_COMMAND_SUBMISSION_PROHIBITION_GATE
- CLASSIFICATION_CONFIG_WRITE_PROHIBITION_GATE
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

- FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_ONLY: True
- FIRMWARE_LOAD_FORBIDDEN: True
- GPU_RESET_FORBIDDEN: True
- FRAMEBUFFER_INIT_FORBIDDEN: True
- DISPLAY_ENGINE_INIT_FORBIDDEN: True
- MODESET_FORBIDDEN: True
- SCANOUT_INIT_FORBIDDEN: True
- GPU_COMMAND_SUBMISSION_FORBIDDEN: True
- GPU_QUEUE_CREATION_FORBIDDEN: True
- GPU_COMMAND_BUFFER_CREATION_FORBIDDEN: True
- GPU_ENCODER_CREATION_FORBIDDEN: True
- GPU_COMMAND_COMMIT_FORBIDDEN: True
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

## Forbidden Marker Policy

The checker constructs forbidden runtime marker strings from smaller parts at runtime.

Exact unsafe runtime marker strings must not be committed directly in this contract, JSON manifests, checker scripts, or generated release-readiness reports.

Existing safe schema field names that describe false/blocked safety state are not treated as executable firmware/reset/display-init paths unless they appear in runtime activation/provider access artifacts.

## Audit Scope

FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_AUDIT_SCOPE:

Runtime activation and provider candidate artifacts only:

- tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift
- scripts/collect-provider-match-candidate.py
- tools/driverkit-activation/provider-open-prohibition-gate.json
- tools/driverkit-activation/bar-mapping-prohibition-gate.json
- tools/driverkit-activation/config-write-prohibition-gate.json
- tools/driverkit-activation/gpu-command-submission-prohibition-gate.json
- tools/driverkit-activation/provider-match-candidate-collector-plan.json
- tools/driverkit-activation/provider-match-candidate-summary-gate.json
- tools/driverkit-activation/dext-load-provider-match-proof-schema.json
- tools/driverkit-activation/activation-execution-gate.json

Static checker scripts, docs, generated reports, and historical schema files are intentionally excluded from marker scanning because they may contain explanatory safety-field wording without creating an executable firmware/reset/display-init path.

## Gate Rule

FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_RULE:

1. Firmware load remains forbidden.
2. GPU reset remains forbidden.
3. Framebuffer initialization remains forbidden.
4. Display-engine initialization remains forbidden.
5. Modeset remains forbidden.
6. Scanout initialization remains forbidden.
7. GPU command submission remains forbidden.
8. Provider open remains forbidden.
9. BAR mapping remains forbidden.
10. PCI configuration writes remain forbidden.
11. Candidate observation is not provider match proof.
12. Provider match proof remains NOT_ATTEMPTED.
13. Dext load proof remains NOT_ATTEMPTED.
14. Real GPU command execution proof remains NOT_ATTEMPTED.

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

- FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_STATE: ENFORCED
- GPU_COMMAND_SUBMISSION_PROHIBITION_STATE: ENFORCED
- CONFIG_WRITE_PROHIBITION_STATE: ENFORCED
- BAR_MAPPING_PROHIBITION_STATE: ENFORCED
- PROVIDER_OPEN_PROHIBITION_STATE: ENFORCED
- PROVIDER_MATCH_CANDIDATE_SUMMARY_STATE: SUMMARY_ONLY
- PROVIDER_MATCH_PROOF_STATE: NOT_ATTEMPTED
- DEXT_LOAD_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Firmware/reset/display-init prohibition is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. provider open is separately reviewed and authorized in a future phase
4. BAR mapping policy is separately reviewed and authorized in a future phase
5. PCI configuration write policy is separately reviewed and authorized in a future phase
6. firmware/reset/display-init policy is separately reviewed and authorized in a future phase
7. real GPU command execution evidence exists
8. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
9. UI compositor proof schema is satisfied
10. Metal proof schema is satisfied

## Current Contract State

- PHASE31_FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_READY: True
- FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_GATE_ONLY: True
- FIRMWARE_LOAD_FORBIDDEN: True
- GPU_RESET_FORBIDDEN: True
- FRAMEBUFFER_INIT_FORBIDDEN: True
- DISPLAY_ENGINE_INIT_FORBIDDEN: True
- MODESET_FORBIDDEN: True
- SCANOUT_INIT_FORBIDDEN: True
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
- ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE
- FIRMWARE_RESET_DISPLAY_INIT_PROHIBITION_STATE: ENFORCED
- GPU_COMMAND_SUBMISSION_PROHIBITION_STATE: ENFORCED
- CONFIG_WRITE_PROHIBITION_STATE: ENFORCED
- BAR_MAPPING_PROHIBITION_STATE: ENFORCED
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
