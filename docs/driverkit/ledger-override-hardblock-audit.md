# Ledger Override Hard-Block Audit

## Purpose

This Phase 22 contract defines a hard-block audit that prevents bypassing the H1mekaRTX DriverKit / System Extension activation execution gate.

This phase does not execute activation or deactivation.

This phase audits that no override, force, bypass, or runtime submit path is present in runtime activation tooling before the activation prerequisites ledger becomes fully READY.

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

All Phase 22 outputs must be labeled only as:

- CLASSIFICATION_LEDGER_OVERRIDE_HARDBLOCK_AUDIT
- CLASSIFICATION_ACTIVATION_EXECUTION_GATE
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

- LEDGER_OVERRIDE_HARDBLOCK_AUDIT_ONLY: True
- OVERRIDE_PATHS_FORBIDDEN: True
- FORCE_EXECUTE_FORBIDDEN: True
- EXECUTE_MODE_STILL_BLOCKED: True
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

## Forbidden Override Markers

FORBIDDEN_LEDGER_OVERRIDE_MARKERS:

- --execute
- --force
- --force-activate
- --force-deactivate
- --allow-unsafe
- --bypass-ledger
- --override-ledger
- H1MEKARTX_FORCE_EXECUTE
- H1MEKARTX_ALLOW_UNSAFE
- H1MEKARTX_BYPASS_LEDGER
- H1MEKARTX_OVERRIDE_LEDGER
- FORCE_ACTIVATION
- FORCE_DEACTIVATION
- BYPASS_ACTIVATION_GATE
- OVERRIDE_ACTIVATION_GATE

## Forbidden Runtime Submit Markers

FORBIDDEN_RUNTIME_SUBMIT_MARKERS:

- OSSystemExtensionManager.shared.submitRequest
- submitRequest(
- submitRequest:
- activationRequest(forExtensionWithIdentifier
- deactivationRequest(forExtensionWithIdentifier
- provider.open
- IOServiceOpen
- mapDeviceMemory
- mapMemory
- writeMemory
- commandSubmission
- submitCommands

## Audit Scope

LEDGER_OVERRIDE_HARDBLOCK_AUDIT_SCOPE:

Runtime activation artifacts only:

- tools/driverkit-activation/H1mekaRTXSystemExtensionActivationDryRun.swift
- tools/driverkit-activation/activation-deactivation-dryrun-plan.json
- tools/driverkit-activation/activation-execution-gate.json

Static checker scripts and generated reports are intentionally excluded from runtime-marker scanning because they may contain explanatory text such as blocked `execute` wording without creating an executable activation path.

## Execution Gate Rule

ACTIVATION_EXECUTION_GATE_RULE:

Future execute mode may be permitted only if all required activation prerequisites ledger entries are READY.

Current expected decision remains BLOCK_EXECUTE.

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

- PHASE22_LEDGER_OVERRIDE_HARDBLOCK_AUDIT_READY: True
- LEDGER_OVERRIDE_HARDBLOCK_AUDIT_ONLY: True
- OVERRIDE_PATHS_FORBIDDEN: True
- FORCE_EXECUTE_FORBIDDEN: True
- EXECUTE_MODE_STILL_BLOCKED: True
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
