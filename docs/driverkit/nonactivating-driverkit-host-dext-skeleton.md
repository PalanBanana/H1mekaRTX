# Non-Activating DriverKit Host App + Dext Skeleton Layout

## Purpose

This Phase 9 contract defines a non-activating Host App + DriverKit dext skeleton layout for H1mekaRTX.

This phase creates static templates only.

It does not build, sign, install, activate, deactivate, load, attach, open, map, reset, or submit commands to any device.

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

All Phase 9 outputs must be labeled only as:

- CLASSIFICATION_NONACTIVATING_DRIVERKIT_SKELETON_LAYOUT
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
- dext load success
- device ownership success
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

- NONACTIVATING_SKELETON_ONLY: True
- NO_BUILD_REQUIRED: True
- NO_SIGNING_REQUIRED: True
- NO_INSTALL_ATTEMPTED: True
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

## Skeleton Layout

NONACTIVATING_DRIVERKIT_SKELETON_LAYOUT:

- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist
- tools/driverkit-skeleton/README.md

## Bundle Identity Contract

BUNDLE_IDENTITY_CONTRACT:

- host_bundle_id: dev.h1meka.H1mekaRTXHost
- dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- team_id_placeholder: TEAMID_PLACEHOLDER
- dext_extension_point: com.apple.driverkit
- expected_system_extension_entitlement: com.apple.developer.system-extension.install
- expected_pci_transport_entitlement: com.apple.developer.driverkit.transport.pci
- activation_state_in_this_phase: NOT_ATTEMPTED
- signing_state_in_this_phase: NOT_ATTEMPTED
- install_state_in_this_phase: NOT_ATTEMPTED

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
- expected_system_extension_entitlement: com.apple.developer.system-extension.install

## Future Promotion Gate

This static skeleton may promote only after later phases provide:

1. valid Apple Developer Team ID
2. approved DriverKit / PCI transport entitlement evidence
3. valid signing identity evidence
4. complete Xcode project or build system
5. static Info.plist validation
6. reversible activation/deactivation code
7. explicit user approval flow
8. disposable test install plan
9. no provider open policy
10. no BAR/MMIO mutation policy
11. no command submission policy
12. rollback plan

## Current Contract State

- PHASE9_NONACTIVATING_DRIVERKIT_SKELETON_READY: True
- NONACTIVATING_SKELETON_ONLY: True
- BUILD_ATTEMPTED: False
- SIGNING_ATTEMPTED: False
- INSTALL_ATTEMPTED: False
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
