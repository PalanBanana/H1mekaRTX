# Buildable DriverKit Host + Dext Scaffold

## Purpose

Phase 42 starts real development inside the approved build/scaffold/evidence scope.

This phase adds a deterministic buildable-source scaffold for:

- H1mekaRTXHost
- H1mekaRTXDriver.dext
- Info.plist templates
- entitlement templates
- source placeholders
- build plan metadata

This phase does not activate a System Extension.

This phase does not deactivate a System Extension.

This phase does not load a dext.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Target

- GPU: NVIDIA GeForce RTX 5070 / GB205
- Vendor ID: 0x10de
- Device ID: 0x2f04
- IOPCIMatch: 0x2f0410de
- Provider class target: IOPCIDevice
- Driver family direction: PCIDriverKit / DriverKit

## Allowed Real Development Scope

- deterministic source scaffold
- deterministic Info.plist scaffold
- deterministic entitlement template scaffold
- build plan metadata
- signing/entitlement evidence preparation
- SystemExtensions wrapper planning
- no runtime activation

## Forbidden Runtime Scope

- no System Extension activation
- no System Extension deactivation
- no dext load
- no provider open
- no BAR mapping
- no MMIO mutation
- no PCI config writes
- no firmware load
- no GPU reset
- no display init
- no GPU command submission
- no WindowServer patching
- no private framework patching
- no fake Metal spoofing

## Classification

- CLASSIFICATION_BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD
- CLASSIFICATION_REAL_DEVELOPMENT_BUILD_SCOPE
- CLASSIFICATION_NO_RUNTIME_ACTIVATION
- CLASSIFICATION_STATIC_CONTRACT

## Current State

- BUILDABLE_DRIVERKIT_HOST_DEXT_SCAFFOLD_READY: True
- REAL_DEVELOPMENT_BUILD_SCOPE_STARTED: True
- SYSTEM_EXTENSION_ACTIVATION_ATTEMPTED: False
- SYSTEM_EXTENSION_DEACTIVATION_ATTEMPTED: False
- DEXT_LOAD_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
