# System Extension User Approval & Rollback Flow

## Purpose

This Phase 19 contract defines the user approval and rollback flow for future H1mekaRTX DriverKit / System Extension activation.

This phase still does not activate DriverKit, does not activate a System Extension, does not load a dext, does not open a provider, does not map BAR memory, and does not submit GPU commands.

The real injection equivalent for this project is official DriverKit / System Extension activation through the SystemExtensions framework.

This project must never use kernel memory injection, process injection, SIP/AMFI bypass, private framework patching, fake Metal device spoofing, or direct Dock/WindowServer injection.

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

All Phase 19 outputs must be labeled only as:

- CLASSIFICATION_USER_APPROVAL_ROLLBACK_FLOW
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

- USER_APPROVAL_ROLLBACK_FLOW_ONLY: True
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
- NO_DIRECT_DOCK_INJECTION: True
- NO_WINDOWSERVER_PATCHING: True

## User Approval Flow

USER_APPROVAL_FLOW_REQUIREMENTS:

1. Host app must clearly explain what System Extension activation means.
2. User must know activation may require macOS Settings approval.
3. User must know deactivation may require restart.
4. Activation must be reversible.
5. Deactivation must be reversible.
6. Status must be captured before activation.
7. Status must be captured after activation.
8. Status must be captured after deactivation.
9. Failure path must tell user how to return to previous state.
10. No provider open, BAR mapping, BAR/MMIO mutation, GPU reset, firmware load, framebuffer init, display engine init, or GPU command submission is allowed in the first activation test.

## Rollback Flow

ROLLBACK_FLOW_REQUIREMENTS:

1. Snapshot or disposable test install must exist before real activation.
2. Current System Extension status must be captured.
3. Activation request logs must be captured.
4. User approval state must be captured.
5. Deactivation request must be available.
6. Restart-required state must be documented.
7. Safe Mode / Recovery rollback note must exist.
8. Repo must not claim UI/Metal acceleration from activation alone.

## Real Dock / Transparency / Blur Injection Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Dock, transparency, blur, window movement, Mission Control, Launchpad, and Stage Manager proof may start only after:

1. System Extension activation/deactivation is reversible.
2. Dext load is proven.
3. Provider matching is proven.
4. Provider open policy is reviewed separately.
5. BAR mapping policy is reviewed separately.
6. Real GPU command execution evidence exists.
7. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists.
8. UI compositor proof schema is satisfied.
9. Metal proof schema is satisfied.

Activation alone is not UI compositor acceleration.

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

- PHASE19_USER_APPROVAL_ROLLBACK_FLOW_READY: True
- USER_APPROVAL_ROLLBACK_FLOW_ONLY: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
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
