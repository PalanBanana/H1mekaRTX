# Read-Only PCI Provider Matching Gate

## Purpose

This Phase 7 contract defines a read-only PCI provider matching gate for H1mekaRTX.

This phase checks whether the RTX 5070 target identity can be represented as a safe DriverKit / PCIDriverKit provider matching candidate.

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

All Phase 7 outputs must be labeled only as:

- CLASSIFICATION_READONLY_PCI_PROVIDER_MATCHING_GATE
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
- device ownership success
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

- READ_ONLY_PROVIDER_MATCHING_ONLY: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
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

## Target PCI Provider Matching Manifest

TARGET_PCI_PROVIDER_MATCHING_MANIFEST:

- target_gpu: NVIDIA RTX 5070
- architecture_family: NVIDIA Blackwell
- vendor_id: 0x10de
- device_id: 0x2f04
- io_pci_match: 0x2f0410de
- expected_provider_class: IOPCIDevice
- expected_driver_family: PCIDriverKit
- expected_entitlement: com.apple.developer.driverkit.transport.pci
- activation_state_in_this_phase: NOT_ATTEMPTED
- provider_open_state_in_this_phase: NOT_ATTEMPTED
- bar_mapping_state_in_this_phase: NOT_ATTEMPTED

## Read-Only Matching Requirements

READONLY_PCI_PROVIDER_MATCHING_REQUIREMENTS:

1. Target vendor ID must remain 0x10de.
2. Target device ID must remain 0x2f04.
3. Target io_pci_match must remain 0x2f0410de.
4. Provider class must be IOPCIDevice.
5. Driver family must remain PCIDriverKit.
6. PCI entitlement key must be documented but not used for activation in this phase.
7. Local Hackintosh observation may search IORegistry text for candidate PCI identities.
8. Local observation must not open the provider.
9. Local observation must not map BAR memory.
10. Local observation must not write PCI config, BAR, MMIO, firmware, framebuffer, or display engine state.
11. Local observation must not claim RTX 5070 UI compositor acceleration.

## Future Promotion Gate

This gate may promote only after later phases provide:

1. explicit reversible DriverKit/System Extension activation plan
2. entitlement/signing evidence
3. read-only provider open policy
4. BAR mapping safety plan
5. runtime probe policy
6. workload attribution plan
7. UI compositor proof plan
8. Metal proof plan

## Current Contract State

- PHASE7_READONLY_PCI_PROVIDER_MATCHING_GATE_READY: True
- READ_ONLY_PROVIDER_MATCHING_ONLY: True
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
