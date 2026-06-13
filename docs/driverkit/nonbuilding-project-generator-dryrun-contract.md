# Non-Building Project Generator Dry-Run Skeleton Contract

## Purpose

This Phase 14 contract defines a non-building project generator dry-run skeleton for H1mekaRTX.

This phase introduces a generator skeleton that emits dry-run project metadata only.

It must not create a real `.xcodeproj`, must not create a real `project.pbxproj`, must not invoke Xcode, must not invoke xcodebuild, must not build, must not sign, must not install, must not activate a System Extension, must not load a dext, must not open a provider, must not map BAR memory, and must not submit GPU commands.

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

All Phase 14 outputs must be labeled only as:

- CLASSIFICATION_NONBUILDING_PROJECT_GENERATOR_DRYRUN
- CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD
- CLASSIFICATION_DETERMINISTIC_XCODE_PROJECT_LAYOUT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- `.xcodeproj` generation success
- `project.pbxproj` generation success
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

- NONBUILDING_PROJECT_GENERATOR_DRYRUN_ONLY: True
- GENERATOR_EMITS_METADATA_ONLY: True
- NO_REAL_XCODEPROJ_GENERATION: True
- NO_REAL_PBXPROJ_GENERATION: True
- NO_XCODE_INVOCATION: True
- NO_XCODEBUILD_INVOCATION: True
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

## Dry-Run Inputs

NONBUILDING_PROJECT_GENERATOR_DRYRUN_INPUTS:

- tools/driverkit-xcode-layout/project-layout.json
- tools/driverkit-xcode-layout/pbxproj-metadata-dryrun.json
- tools/driverkit-xcode-layout/pbxproj-sanitized-metadata.json
- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist

## Dry-Run Outputs

NONBUILDING_PROJECT_GENERATOR_DRYRUN_OUTPUTS:

- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.md
- release-readiness/nonbuilding-project-generator-dryrun-check.json
- release-readiness/nonbuilding-project-generator-dryrun-check.md

## Future Project Generator Contract

FUTURE_PROJECT_GENERATOR_CONTRACT:

- project_name: H1mekaRTXDriverKit
- host_target_name: H1mekaRTXHost
- dext_target_name: H1mekaRTXDriver
- host_bundle_id: dev.h1meka.H1mekaRTXHost
- dext_bundle_id: dev.h1meka.H1mekaRTXDriver
- dext_extension_point: com.apple.driverkit
- expected_system_extension_entitlement: com.apple.developer.system-extension.install
- expected_driverkit_entitlement: com.apple.developer.driverkit
- expected_pci_transport_entitlement: com.apple.developer.driverkit.transport.pci
- project_generator_state_in_this_phase: DRYRUN_METADATA_ONLY
- xcodeproj_generation_state_in_this_phase: NOT_ATTEMPTED
- pbxproj_generation_state_in_this_phase: NOT_ATTEMPTED
- xcode_invocation_state_in_this_phase: NOT_ATTEMPTED
- xcodebuild_invocation_state_in_this_phase: NOT_ATTEMPTED
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

## Forbidden Output Paths

FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS:

- tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj
- tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj
- H1mekaRTXDriverKit.xcodeproj
- H1mekaRTXDriverKit.xcodeproj/project.pbxproj

## Future Promotion Gate

This dry-run generator may promote only after later phases provide:

1. deterministic project generator implementation with explicit output allowlist
2. dry-run diff approval
3. pbxproj sanitizer approval
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

- PHASE14_NONBUILDING_PROJECT_GENERATOR_DRYRUN_READY: True
- NONBUILDING_PROJECT_GENERATOR_DRYRUN_ONLY: True
- GENERATOR_EMITS_METADATA_ONLY: True
- REAL_XCODEPROJ_GENERATION_ATTEMPTED: False
- REAL_PBXPROJ_GENERATION_ATTEMPTED: False
- XCODE_INVOCATION_ATTEMPTED: False
- XCODEBUILD_INVOCATION_ATTEMPTED: False
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
