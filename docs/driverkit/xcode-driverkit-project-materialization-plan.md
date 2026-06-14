# Xcode DriverKit Project Materialization Plan

## Purpose

Phase 60M materializes the source, plist, entitlement, and project-layout inputs required to create a real Xcode DriverKit project.

Phase 60L showed that no real Xcode DriverKit project exists at:

- apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj

Therefore the local real DriverKit dext build gate cannot run yet.

This phase does not create a provider-open path.

This phase does not call IOServiceOpen.

This phase does not map BAR memory.

This phase does not mutate BAR/MMIO.

This phase does not write PCI configuration space.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not submit GPU commands.

This phase does not claim Metal proof.

This phase does not claim Dock/transparency/blur acceleration.

## Materialized Inputs

This phase adds:

- DriverKit host app Swift source
- DriverKit dext C++ source
- host Info.plist template
- dext Info.plist template
- host entitlements template
- dext entitlements template
- Xcode project materialization manifest
- local project existence/materialization checker

## Manual Xcode Project Creation

The intended Xcode project should be created as:

- Project path: apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj
- Host target: H1mekaRTXHost
- DriverKit target: H1mekaRTXDriver
- Host bundle ID: dev.h1meka.H1mekaRTXHost
- Dext bundle ID: dev.h1meka.H1mekaRTXDriver
- Dext extension ID: dev.h1meka.H1mekaRTXDriver
- Driver provider class: IOPCIDevice
- IOPCIMatch: 0x2f0410de

## Runtime Boundary

Even after the project exists:

- Phase 60L must prove a real Xcode-built DriverKit dext binary
- signing/preflight must be rerun
- /Applications activation remediation must be rerun
- provider open remains blocked
- IOServiceOpen remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked
- Metal proof remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_XCODE_DRIVERKIT_PROJECT_MATERIALIZATION_PLAN
- CLASSIFICATION_REAL_DRIVERKIT_DEXT_BUILD_GATE
- CLASSIFICATION_PROJECT_INPUTS_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
