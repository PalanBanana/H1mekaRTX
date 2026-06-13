# System Extension Activation / Deactivation Dry-Run Skeleton

## Purpose

This Phase 20 contract introduces a System Extension activation/deactivation code skeleton for H1mekaRTX.

This phase adds source skeleton and static validation only.

Default behavior must be dry-run only.

Real DriverKit/System Extension activation must remain blocked unless a future explicit execution gate verifies that all activation prerequisites are READY.

The real injection equivalent for this project is official DriverKit / System Extension activation through the SystemExtensions framework.

This project must never use kernel memory injection, process injection, SIP/AMFI bypass, private framework patching, fake Metal device spoofing, direct Dock injection, or WindowServer patching.

## Long-Term UI Goal

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

All Phase 20 outputs must be labeled only as:

- CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON
- CLASSIFICATION_USER_APPROVAL_ROLLBACK_FLOW
- CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER
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

- ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_ONLY: True
- DEFAULT_MODE_DRY_RUN: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
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

## Skeleton Files

ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_FILES:

- tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift
- tools/driverkit-activation/activation-deactivation-dryrun-plan.json

## Execution Rule

REAL_EXECUTION_RULE:

Real `OSSystemExtensionRequest.activationRequest` or `OSSystemExtensionRequest.deactivationRequest` submit may be introduced only in a future phase after:

1. activation prerequisites ledger reports all required entries READY
2. Apple Developer Team ID is recorded
3. DriverKit entitlement approval evidence is recorded
4. PCI transport entitlement approval evidence is recorded
5. valid signing identity evidence is recorded
6. buildable host app and dext project exists
7. signed artifacts exist
8. disposable rollback-capable test install exists
9. user approval flow is documented
10. rollback/deactivation flow is implemented
11. first activation test keeps provider open disabled
12. first activation test keeps BAR mapping disabled
13. first activation test keeps GPU command submission disabled

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Activation/deactivation alone is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. real GPU command execution evidence exists
4. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
5. UI compositor proof schema is satisfied
6. Metal proof schema is satisfied

## Current Contract State

- PHASE20_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_READY: True
- ACTIVATION_DEACTIVATION_DRYRUN_SKELETON_ONLY: True
- DEFAULT_MODE_DRY_RUN: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- DRIVERKIT_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False
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
