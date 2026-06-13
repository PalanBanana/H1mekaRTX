# Reversible DriverKit / System Extension Activation Dry-Run Plan

## Purpose

This Phase 8 contract defines a reversible DriverKit / System Extension activation dry-run plan for H1mekaRTX.

This is still not a real activation step.

The purpose is to define the exact safety, signing, entitlement, approval, rollback, and evidence requirements that must exist before any future DriverKit / PCIDriverKit dext activation is attempted.

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

All Phase 8 outputs must be labeled only as:

- CLASSIFICATION_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN_PLAN
- CLASSIFICATION_DRIVERKIT_FEASIBILITY_PREFLIGHT
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
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

- DRY_RUN_PLAN_ONLY: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
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

## Future Activation Prerequisites

REVERSIBLE_DRIVERKIT_ACTIVATION_PREREQUISITES:

1. Apple Developer Team ID must be documented.
2. DriverKit entitlement request status must be documented.
3. PCI transport entitlement requirement must be documented.
4. System Extension entitlement requirement must be documented.
5. Dext bundle identifier must be documented.
6. Host app bundle identifier must be documented.
7. Reversible activation flow must be documented.
8. Deactivation / rollback flow must be documented.
9. User approval requirement must be documented.
10. System extension status inspection command must be documented.
11. No provider open, BAR mapping, MMIO mutation, GPU reset, firmware loading, framebuffer initialization, display engine initialization, or command submission is allowed in this phase.
12. No UI compositor acceleration claim is allowed in this phase.

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
- activation_state_in_this_phase: NOT_ATTEMPTED
- rollback_state_in_this_phase: PLAN_ONLY
- provider_open_state_in_this_phase: NOT_ATTEMPTED
- bar_mapping_state_in_this_phase: NOT_ATTEMPTED

## Reversible Activation Dry-Run Checklist

REVERSIBLE_ACTIVATION_DRYRUN_CHECKLIST:

1. Define host app bundle.
2. Define dext bundle.
3. Define dext bundle identifier.
4. Define DriverKit entitlement requirements.
5. Define PCI transport entitlement requirements.
6. Define System Extension install entitlement requirements.
7. Define user approval requirement.
8. Define activation request API requirement.
9. Define systemextensionsctl status inspection path.
10. Define deactivation request API requirement.
11. Define rollback plan.
12. Define logs to collect from sysextd and system extension status.
13. Define safety preconditions that block activation.
14. Preserve RTX 5070 UI compositor goal as future proof target only.

## Future Promotion Gate

This dry-run plan may promote only after later phases provide:

1. approved DriverKit / PCI entitlement evidence
2. valid signing identity evidence
3. host app + dext bundle skeleton
4. dext Info.plist static validation
5. reversible activation/deactivation implementation
6. no hardware access policy
7. no BAR/MMIO mutation policy
8. no provider open policy
9. explicit user approval and rollback instructions
10. real activation test on disposable test install only

## Current Contract State

- PHASE8_REVERSIBLE_DRIVERKIT_ACTIVATION_DRYRUN_READY: True
- DRY_RUN_PLAN_ONLY: True
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- DEVICE_OWNERSHIP_REQUEST_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
