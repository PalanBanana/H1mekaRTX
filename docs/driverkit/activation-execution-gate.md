# System Extension Activation Execution Gate

## Purpose

This Phase 21 contract defines the execution gate for future H1mekaRTX DriverKit / System Extension activation and deactivation.

This phase does not execute activation or deactivation.

This phase creates a strict gate that blocks any future execute mode unless every required activation prerequisite is READY.

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

All Phase 21 outputs must be labeled only as:

- CLASSIFICATION_ACTIVATION_EXECUTION_GATE
- CLASSIFICATION_ACTIVATION_DEACTIVATION_DRYRUN_SKELETON
- CLASSIFICATION_ACTIVATION_PREREQUISITES_LEDGER
- CLASSIFICATION_STATIC_CONTRACT

This phase must not claim:

- DriverKit activation success
- System Extension activation success
- System Extension deactivation success
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

- ACTIVATION_EXECUTION_GATE_ONLY: True
- EXECUTE_MODE_BLOCKED_BY_DEFAULT: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
- NO_SYSTEM_EXTENSION_DEACTIVATION: True
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

## Execution Gate Rule

ACTIVATION_EXECUTION_GATE_RULE:

Future execute mode may be permitted only if all of these are true:

1. activation prerequisites ledger exists
2. every required ledger item has status READY
3. Apple Developer Team ID evidence exists
4. approved DriverKit entitlement evidence exists
5. approved PCI transport entitlement evidence exists
6. valid signing identity evidence exists
7. buildable host app and dext project exists
8. signed host app and dext artifacts exist
9. disposable rollback-capable test install exists
10. user approval flow exists
11. rollback/deactivation flow exists
12. no provider open policy is active
13. no BAR mapping policy is active
14. no BAR/MMIO mutation policy is active
15. no GPU command submission policy is active

Current expected decision is BLOCK_EXECUTE because the ledger is not fully READY.

## Skeleton Files

ACTIVATION_EXECUTION_GATE_FILES:

- tools/driverkit-activation/activation-execution-gate.json
- scripts/check-activation-execution-gate.py
- scripts/run-activation-execution-gate.sh

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Activation execution is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. real GPU command execution evidence exists
4. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
5. UI compositor proof schema is satisfied
6. Metal proof schema is satisfied

## Current Contract State

- PHASE21_ACTIVATION_EXECUTION_GATE_READY: True
- ACTIVATION_EXECUTION_GATE_ONLY: True
- EXECUTE_MODE_BLOCKED_BY_DEFAULT: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- ACTIVATION_EXECUTION_GATE_DECISION: BLOCK_EXECUTE
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
