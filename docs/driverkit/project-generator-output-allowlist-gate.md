# Project Generator Output Allowlist & Promotion Gate

## Purpose

This Phase 15 contract defines an explicit output allowlist and promotion gate for the H1mekaRTX non-building project generator.

This phase validates which paths a future project generator may write during dry-run and which paths remain forbidden until a later explicit promotion.

This phase must not create a real `.xcodeproj`, must not create a real `project.pbxproj`, must not invoke Xcode, must not invoke xcodebuild, must not build, must not sign, must not install, must not activate a System Extension, must not load a dext, must not open a provider, must not map BAR memory, and must not submit GPU commands.

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

All Phase 15 outputs must be labeled only as:

- CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE
- CLASSIFICATION_NONBUILDING_PROJECT_GENERATOR_DRYRUN
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
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

- PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE_ONLY: True
- OUTPUT_ALLOWLIST_REPORT_ONLY: True
- PROMOTION_GATE_ONLY: True
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

## Allowlist Inputs

PROJECT_GENERATOR_OUTPUT_ALLOWLIST_INPUTS:

- tools/driverkit-xcode-layout/project-layout.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.md

## Allowlist Outputs

PROJECT_GENERATOR_OUTPUT_ALLOWLIST_OUTPUTS:

- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.md
- release-readiness/project-generator-output-allowlist-gate-check.json
- release-readiness/project-generator-output-allowlist-gate-check.md

## Allowed Dry-Run Output Paths

ALLOWED_DRYRUN_OUTPUT_PATHS:

- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.md
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.md
- release-readiness/nonbuilding-project-generator-dryrun-check.json
- release-readiness/nonbuilding-project-generator-dryrun-check.md
- release-readiness/project-generator-output-allowlist-gate-check.json
- release-readiness/project-generator-output-allowlist-gate-check.md

## Forbidden Real Project Output Paths

FORBIDDEN_REAL_PROJECT_OUTPUT_PATHS:

- tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj
- tools/driverkit-xcode-layout/H1mekaRTXDriverKit.xcodeproj/project.pbxproj
- H1mekaRTXDriverKit.xcodeproj
- H1mekaRTXDriverKit.xcodeproj/project.pbxproj

## Promotion Requirements

PROJECT_GENERATOR_PROMOTION_REQUIREMENTS:

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
16. no UI compositor acceleration claim before proof gate
17. no Metal proof claim before real GPU-backed workload evidence

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

## Current Contract State

- PHASE15_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE_READY: True
- PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE_ONLY: True
- OUTPUT_ALLOWLIST_REPORT_ONLY: True
- PROMOTION_GATE_ONLY: True
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
