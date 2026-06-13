# PBXProj Dry-Run Diff Guard & Sanitizer Contract

## Purpose

This Phase 13 contract defines a dry-run diff guard and sanitizer for H1mekaRTX pbxproj metadata.

This phase validates that pbxproj dry-run metadata does not accidentally promote into a real Xcode project generation, build, signing, install, DriverKit activation, System Extension activation, dext load, provider open, BAR mapping, or GPU command submission step.

This phase may read:

- tools/driverkit-xcode-layout/pbxproj-metadata-dryrun.json
- tools/driverkit-xcode-layout/pbxproj-metadata-dryrun.md
- tools/driverkit-xcode-layout/project-layout.json

This phase may write sanitized JSON/Markdown reports only.

This phase must not create a real `.xcodeproj`, must not create a real `project.pbxproj`, must not invoke Xcode, must not build, must not sign, must not install, must not activate a System Extension, must not load a dext, must not open a provider, must not map BAR memory, and must not submit GPU commands.

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

All Phase 13 outputs must be labeled only as:

- CLASSIFICATION_PBXPROJ_DRYRUN_DIFF_GUARD
- CLASSIFICATION_PBXPROJ_METADATA_DRYRUN
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

- PBXPROJ_DRYRUN_DIFF_GUARD_ONLY: True
- SANITIZER_REPORT_ONLY: True
- NO_REAL_XCODEPROJ_GENERATION: True
- NO_REAL_PBXPROJ_GENERATION: True
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

## Guard Inputs

PBXPROJ_DRYRUN_DIFF_GUARD_INPUTS:

- tools/driverkit-xcode-layout/project-layout.json
- tools/driverkit-xcode-layout/pbxproj-metadata-dryrun.json
- tools/driverkit-xcode-layout/pbxproj-metadata-dryrun.md

## Guard Outputs

PBXPROJ_DRYRUN_DIFF_GUARD_OUTPUTS:

- release-readiness/pbxproj-dryrun-diff-guard-check.json
- release-readiness/pbxproj-dryrun-diff-guard-check.md
- tools/driverkit-xcode-layout/pbxproj-sanitized-metadata.json
- tools/driverkit-xcode-layout/pbxproj-sanitized-metadata.md

## Forbidden Promotion Markers

FORBIDDEN_PBXPROJ_PROMOTION_MARKERS:

- real_xcodeproj_generation_attempted: true
- real_pbxproj_generation_attempted: true
- xcodebuild_invocation_attempted: true
- build_attempted: true
- signing_attempted: true
- install_attempted: true
- driverkit_activation_attempted: true
- system_extension_activation_attempted: true
- dext_load_attempted: true
- provider_open_attempted: true
- bar_mapping_attempted: true
- bar_mmio_mutation_attempted: true
- real_gpu_command_execution_attempted: true
- rtx5070_workload_attribution_claimed: true
- real_gpu_acceleration_claimed: true
- ui_compositor_proof_claimed: true
- metal_proof_claimed: true

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

## Future Promotion Gate

This diff guard may promote only after later phases provide:

1. real project generator dry-run diff approval
2. deterministic pbxproj sanitizer
3. no-build verification gate
4. approved Apple Developer Team ID
5. approved DriverKit entitlement evidence
6. approved PCI transport entitlement evidence
7. valid signing identity evidence
8. disposable test install plan
9. reversible activation/deactivation implementation
10. explicit user approval flow
11. rollback plan
12. no provider open policy
13. no BAR/MMIO mutation policy
14. no command submission policy

## Current Contract State

- PHASE13_PBXPROJ_DRYRUN_DIFF_GUARD_READY: True
- PBXPROJ_DRYRUN_DIFF_GUARD_ONLY: True
- SANITIZER_REPORT_ONLY: True
- REAL_XCODEPROJ_GENERATION_ATTEMPTED: False
- REAL_PBXPROJ_GENERATION_ATTEMPTED: False
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
