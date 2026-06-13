# Static Build / Signing / Entitlement Audit Gate

## Purpose

This Phase 10 contract defines a static build, signing, and entitlement audit gate for H1mekaRTX.

This phase checks whether the non-activating DriverKit host app + dext skeleton has the required static identity, signing, entitlement, and safety metadata before any future build or activation work.

This phase does not build, sign, install, activate, load, open, map, reset, or submit commands to any device.

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

All Phase 10 outputs must be labeled only as:

- CLASSIFICATION_STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- build success
- signing success
- install success
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

- STATIC_AUDIT_ONLY: True
- NO_BUILD_ATTEMPTED: True
- NO_SIGNING_ATTEMPTED: True
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

## Static Audit Inputs

STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT_INPUTS:

- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist

## Bundle Identity Contract

BUNDLE_IDENTITY_CONTRACT:

- host_bundle_id: dev.h1meka.H1mekaRTXHost
- dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- team_id_placeholder: TEAMID_PLACEHOLDER
- dext_extension_point: com.apple.driverkit
- expected_system_extension_entitlement: com.apple.developer.system-extension.install
- expected_driverkit_entitlement: com.apple.developer.driverkit
- expected_pci_transport_entitlement: com.apple.developer.driverkit.transport.pci
- build_state_in_this_phase: NOT_ATTEMPTED
- signing_state_in_this_phase: NOT_ATTEMPTED
- install_state_in_this_phase: NOT_ATTEMPTED
- activation_state_in_this_phase: NOT_ATTEMPTED

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

## Entitlement Audit Checklist

STATIC_ENTITLEMENT_AUDIT_CHECKLIST:

1. Host entitlement template must include com.apple.developer.system-extension.install.
2. Dext entitlement template must include com.apple.developer.driverkit.
3. Dext entitlement template must include com.apple.developer.driverkit.transport.pci.
4. PCI entitlement candidate must reference vendor_id 0x10de.
5. PCI entitlement candidate must reference device_id 0x2f04.
6. PCI entitlement candidate must reference io_pci_match 0x2f0410de.
7. Entitlement templates are placeholders and must not be treated as approved Apple entitlements.
8. Signing identity is not used in this phase.
9. Build system is not invoked in this phase.
10. System Extension activation is not invoked in this phase.
11. Dext load is not invoked in this phase.
12. No UI compositor acceleration claim is allowed in this phase.

## Future Promotion Gate

This static audit may promote only after later phases provide:

1. approved Apple Developer Team ID
2. approved DriverKit entitlement evidence
3. approved PCI transport entitlement evidence
4. valid signing identity evidence
5. Xcode project or deterministic build system
6. signed host app + dext artifact on disposable test install only
7. reversible activation/deactivation implementation
8. explicit user approval flow
9. rollback plan
10. no provider open policy
11. no BAR/MMIO mutation policy
12. no command submission policy

## Current Contract State

- PHASE10_STATIC_BUILD_SIGNING_ENTITLEMENT_AUDIT_READY: True
- STATIC_AUDIT_ONLY: True
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
