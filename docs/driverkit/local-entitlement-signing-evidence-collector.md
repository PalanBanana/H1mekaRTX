# Local Entitlement / Signing Evidence Collector Contract

## Purpose

This Phase 18 contract defines a local read-only entitlement and signing evidence collector for H1mekaRTX.

This phase collects local status evidence that may later help update the Phase 17 activation prerequisites ledger.

This phase is read-only and status-only.

It must not build, sign, install, activate a System Extension, load a dext, request device ownership, open a provider, map BAR memory, mutate BAR/MMIO, or submit GPU commands.

The real injection equivalent for this project remains official DriverKit / System Extension activation only after all prerequisites are READY.

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

All Phase 18 outputs must be labeled only as:

- CLASSIFICATION_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE
- CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- Apple entitlement approval
- valid signing readiness
- build success
- signing success
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

- LOCAL_EVIDENCE_COLLECTOR_ONLY: True
- READ_ONLY_STATUS_COLLECTION_ONLY: True
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

## Collector Inputs

LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_INPUTS:

- tools/driverkit-activation/activation-prerequisites-ledger.json
- tools/driverkit-skeleton/H1mekaRTXHost.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.entitlements.template.plist
- tools/driverkit-skeleton/H1mekaRTXHost.app.template/Info.plist
- tools/driverkit-skeleton/H1mekaRTXDriver.dext.template/Info.plist

## Collector Outputs

LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_OUTPUTS:

- host-report-bundle/local-entitlement-signing-evidence/local-entitlement-signing-evidence.json
- host-report-bundle/local-entitlement-signing-evidence/local-entitlement-signing-evidence.md
- release-readiness/local-entitlement-signing-evidence-check.json
- release-readiness/local-entitlement-signing-evidence-check.md

## Safe Local Commands

SAFE_LOCAL_STATUS_COMMANDS:

- xcode-select -p
- xcodebuild -version
- security find-identity -v -p codesigning
- systemextensionsctl list
- sw_vers
- uname -a

These commands are status-only.

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

- PHASE18_LOCAL_ENTITLEMENT_SIGNING_EVIDENCE_READY: True
- LOCAL_EVIDENCE_COLLECTOR_ONLY: True
- READ_ONLY_STATUS_COLLECTION_ONLY: True
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
