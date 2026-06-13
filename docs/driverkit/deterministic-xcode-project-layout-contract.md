# Deterministic Xcode / DriverKit Project Layout Contract

## Purpose

This Phase 11 contract defines a deterministic Xcode/project-layout plan for H1mekaRTX.

This phase creates static project layout metadata only.

It does not generate a real Xcode project, does not build, does not sign, does not install, does not activate, does not load a dext, does not open a provider, does not map BAR memory, and does not submit GPU commands.

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

All Phase 11 outputs must be labeled only as:

- CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- Xcode build success
- signing success
- install success
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

- PROJECT_LAYOUT_CONTRACT_ONLY: True
- NO_XCODEPROJ_GENERATION: True
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

## Deterministic Layout Inputs

DETERMINISTIC_XCODE_PROJECT_LAYOUT_INPUTS:

- tools/driverkit-xcode-layout/project-layout.json
- tools/driverkit-xcode-layout/README.md
- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist

## Project Identity Contract

PROJECT_IDENTITY_CONTRACT:

- project_name: H1mekaRTXDriverKit
- host_target_name: H1mekaRTXHost
- dext_target_name: H1mekaRTXDriver
- host_bundle_id: dev.h1meka.H1mekaRTXHost
- dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- team_id_placeholder: TEAMID_PLACEHOLDER
- dext_extension_point: com.apple.driverkit
- expected_system_extension_entitlement: com.apple.developer.system-extension.install
- expected_driverkit_entitlement: com.apple.developer.driverkit
- expected_pci_transport_entitlement: com.apple.developer.driverkit.transport.pci
- project_generation_state_in_this_phase: NOT_ATTEMPTED
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

## Xcode Layout Checklist

DETERMINISTIC_XCODE_LAYOUT_CHECKLIST:

1. Host target identity must be deterministic.
2. Dext target identity must be deterministic.
3. Host Info.plist source must be deterministic.
4. Dext Info.plist source must be deterministic.
5. Host entitlement template source must be deterministic.
6. Dext entitlement template source must be deterministic.
7. Build configuration names must be deterministic.
8. Signing must remain disabled / not attempted in this phase.
9. Xcode project generation must remain not attempted in this phase.
10. DriverKit activation must remain not attempted in this phase.
11. System Extension activation must remain not attempted in this phase.
12. No UI compositor acceleration claim is allowed in this phase.

## Future Promotion Gate

This layout contract may promote only after later phases provide:

1. deterministic project generator
2. non-signing project generation only
3. static pbxproj audit
4. no-build verification gate
5. approved Apple Developer Team ID
6. approved DriverKit entitlement evidence
7. approved PCI transport entitlement evidence
8. valid signing identity evidence
9. disposable test install plan
10. reversible activation/deactivation implementation
11. explicit user approval flow
12. rollback plan
13. no provider open policy
14. no BAR/MMIO mutation policy
15. no command submission policy

## Current Contract State

- PHASE11_DETERMINISTIC_XCODE_PROJECT_LAYOUT_READY: True
- PROJECT_LAYOUT_CONTRACT_ONLY: True
- XCODEPROJ_GENERATION_ATTEMPTED: False
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
