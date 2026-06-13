# No-Build Project Generation Preflight Gate

## Purpose

This Phase 16 contract defines a no-build project generation preflight for H1mekaRTX.

This phase validates whether the project generator is allowed to proceed toward a future real project generation phase.

This phase still must not create a real `.xcodeproj`, must not create a real `project.pbxproj`, must not invoke Xcode, must not invoke xcodebuild, must not build, must not sign, must not install, must not activate a System Extension, must not load a dext, must not open a provider, must not map BAR memory, and must not submit GPU commands.

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

All Phase 16 outputs must be labeled only as:

- CLASSIFICATION_NO_BUILD_PROJECT_GENERATION_PREFLIGHT
- CLASSIFICATION_PROJECT_GENERATOR_OUTPUT_ALLOWLIST_GATE
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

- NO_BUILD_PROJECT_GENERATION_PREFLIGHT_ONLY: True
- PROJECT_GENERATION_NOT_ATTEMPTED: True
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

## Preflight Inputs

NO_BUILD_PROJECT_GENERATION_PREFLIGHT_INPUTS:

- tools/driverkit-xcode-layout/project-layout.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-dryrun-manifest.json
- tools/driverkit-xcode-layout/project-generator-dryrun/project-generator-output-allowlist.json
- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist

## Preflight Outputs

NO_BUILD_PROJECT_GENERATION_PREFLIGHT_OUTPUTS:

- release-readiness/no-build-project-generation-preflight-check.json
- release-readiness/no-build-project-generation-preflight-check.md

## Required Preflight Conditions

NO_BUILD_PROJECT_GENERATION_PREFLIGHT_REQUIREMENTS:

1. project layout metadata must exist
2. non-building project generator dry-run manifest must exist
3. output allowlist must exist
4. forbidden real project output paths must be absent
5. host app Info.plist template must exist
6. dext Info.plist template must exist
7. host entitlement template must exist
8. dext entitlement template must exist
9. bundle IDs must remain deterministic
10. PCI match metadata must remain deterministic
11. no build/sign/install/activation state may be true
12. no UI compositor acceleration claim may be true
13. no Metal proof claim may be true

## Future Real Injection Gate

REAL_DRIVERKIT_ACTIVATION_GATE_REQUIREMENTS:

1. approved Apple Developer Team ID
2. approved DriverKit entitlement
3. approved PCI transport entitlement
4. valid signing identity
5. buildable host app and dext project
6. signed artifacts
7. disposable test install or snapshot rollback environment
8. explicit user approval path
9. reversible activation implementation
10. reversible deactivation implementation
11. no provider open policy for first activation test
12. no BAR mapping policy for first activation test
13. no BAR/MMIO mutation policy
14. no GPU command submission policy
15. no UI compositor acceleration claim before proof gate
16. no Metal proof claim before real GPU-backed workload evidence

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

- PHASE16_NO_BUILD_PROJECT_GENERATION_PREFLIGHT_READY: True
- NO_BUILD_PROJECT_GENERATION_PREFLIGHT_ONLY: True
- PROJECT_GENERATION_ATTEMPTED: False
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
