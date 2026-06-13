# Activation Status Capture Harness

## Purpose

This Phase 23 contract defines a read-only activation status capture harness for H1mekaRTX.

This phase collects status only.

This phase does not execute activation or deactivation.

The harness may read:

- systemextensionsctl list
- log show status slices for system extension related processes/subsystems
- sw_vers
- uname -a
- activation execution gate JSON
- activation prerequisites ledger JSON

The real injection equivalent for this project remains official DriverKit / System Extension activation through the SystemExtensions framework in a later phase, after the activation prerequisites ledger is READY.

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

All Phase 23 outputs must be labeled only as:

- CLASSIFICATION_ACTIVATION_STATUS_CAPTURE_HARNESS
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

- ACTIVATION_STATUS_CAPTURE_HARNESS_ONLY: True
- READ_ONLY_STATUS_CAPTURE_ONLY: True
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

## Safe Status Commands

SAFE_ACTIVATION_STATUS_COMMANDS:

- systemextensionsctl list
- log show --style compact --last 10m --predicate 'process == "sysextd" OR subsystem CONTAINS "systemextensions"'
- sw_vers
- uname -a

These commands are status-only.

## Harness Files

ACTIVATION_STATUS_CAPTURE_HARNESS_FILES:

- tools/driverkit-activation/activation-status-capture-plan.json
- scripts/collect-activation-status-capture.py
- scripts/check-activation-status-capture-harness.py
- scripts/run-activation-status-capture-harness.sh

## Output Policy

LOCAL_STATUS_OUTPUTS_IGNORED:

- host-report-bundle/activation-status-capture/activation-status-capture.json
- host-report-bundle/activation-status-capture/activation-status-capture.md

The host-report-bundle output is intentionally local-only and should not be force-added to git.

COMMITTED_CHECK_OUTPUTS:

- release-readiness/activation-status-capture-harness-check.json
- release-readiness/activation-status-capture-harness-check.md

## Dock / Transparency / Blur Rule

REAL_UI_COMPOSITOR_ACCELERATION_RULE:

Activation status capture is not Dock, transparency, blur, Mission Control, Launchpad, Stage Manager, UI compositor, or Metal acceleration proof.

UI compositor proof remains blocked until:

1. dext load is proven
2. provider matching is proven
3. real GPU command execution evidence exists
4. WindowServer / Core Animation / QuartzCore / Metal compositor attribution evidence exists
5. UI compositor proof schema is satisfied
6. Metal proof schema is satisfied

## Current Contract State

- PHASE23_ACTIVATION_STATUS_CAPTURE_HARNESS_READY: True
- ACTIVATION_STATUS_CAPTURE_HARNESS_ONLY: True
- READ_ONLY_STATUS_CAPTURE_ONLY: True
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
