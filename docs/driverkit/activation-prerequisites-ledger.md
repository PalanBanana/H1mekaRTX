# DriverKit / System Extension Activation Prerequisites Ledger

## Purpose

This Phase 17 contract defines the activation prerequisites ledger for H1mekaRTX.

This phase answers when real DriverKit / System Extension activation may start.

Real activation is still not attempted in this phase.

The real injection equivalent for this project is DriverKit / System Extension activation through the official SystemExtensions framework path, not kernel memory injection, process injection, SIP/AMFI bypass, private framework patching, or fake Metal device spoofing.

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

All Phase 17 outputs must be labeled only as:

- CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
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

- ACTIVATION_PREREQUISITES_LEDGER_ONLY: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
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

## Real Activation Start Rule

REAL_DRIVERKIT_ACTIVATION_START_RULE:

Real DriverKit/System Extension activation may start only after all required ledger entries are READY:

1. Apple Developer Team ID
2. approved DriverKit entitlement
3. approved PCI transport entitlement
4. valid signing identity
5. buildable host app and dext project
6. signed host app and dext artifacts
7. disposable rollback-capable test install
8. reversible activation implementation
9. reversible deactivation implementation
10. explicit user approval flow
11. logs/status capture plan
12. no provider open policy for first activation test
13. no BAR mapping policy for first activation test
14. no BAR/MMIO mutation policy
15. no GPU command submission policy
16. UI compositor proof remains blocked until attribution evidence exists
17. Metal proof remains blocked until real GPU-backed workload evidence exists

## Activation Prerequisites Ledger Schema

ACTIVATION_PREREQUISITES_LEDGER_SCHEMA:

Each ledger item has:

- key
- description
- status
- required_for_activation
- evidence_path
- blocker_reason

Valid status values:

- READY
- MISSING
- BLOCKED
- NOT_APPLICABLE

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

## Current Contract State

- PHASE17_ACTIVATION_PREREQUISITES_LEDGER_READY: True
- ACTIVATION_PREREQUISITES_LEDGER_ONLY: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- ACTIVATION_GATE_STATE: BLOCKED_MISSING_PREREQUISITES
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
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
