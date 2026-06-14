# Signed Host + Dext Packaging Preflight

## Purpose

Phase 48 defines the signed host+dext packaging preflight for future local System Extension activation.

This phase is packaging preflight only.

This phase does not build signed artifacts.

This phase does not codesign anything.

This phase does not install anything.

This phase does not submit an activation request.

This phase does not submit a deactivation request.

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

## Required Future Packaging Layout

Expected signed host app layout for a future local test:

- H1mekaRTXHost.app
- H1mekaRTXHost.app/Contents/Info.plist
- H1mekaRTXHost.app/Contents/MacOS/H1mekaRTXHost
- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext
- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist
- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver

## Required Future Signing Inputs

- Apple Developer Team ID
- valid Developer ID Application or development signing identity
- host app entitlement: com.apple.developer.system-extension.install
- dext entitlement: com.apple.developer.driverkit
- dext entitlement: com.apple.developer.driverkit.transport.pci
- provisioning profile if required
- bundle ID dev.h1meka.H1mekaRTXHost
- bundle ID dev.h1meka.H1mekaRTXDriver

## Required Future Pre-Activation Checks

- codesign verification passes for host app
- codesign verification passes for dext
- entitlements are dumped and checked
- dext is nested inside host app under Contents/Library/SystemExtensions
- systemextensionsctl status captured before activation
- rollback/deactivation command available
- user approval is expected and allowed
- provider open remains disabled
- BAR mapping remains disabled
- GPU command submission remains disabled

## Dock / Transparency / Blur Timing

Dock/transparency/blur remains blocked until after:

1. signed package proof
2. user-approved activation proof
3. deactivation/rollback proof
4. dext load proof
5. provider match proof
6. safe provider-open proof
7. real GPU command execution proof
8. RTX 5070 workload attribution proof
9. WindowServer/Core Animation/QuartzCore/Metal compositor attribution proof
10. before/after UI metric proof
11. Dock/transparency/blur scenario proof

## Classification

- CLASSIFICATION_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT
- CLASSIFICATION_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_SIGNING_NO_INSTALL_NO_ACTIVATION

## Current State

- SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT_READY: True
- PACKAGING_PREFLIGHT_ONLY: True
- SIGNED_PACKAGE_CREATED: False
- CODESIGN_ATTEMPTED: False
- INSTALL_ATTEMPTED: False
- SUBMIT_ACTIVATION_ALLOWED_NOW: False
- SUBMIT_DEACTIVATION_ALLOWED_NOW: False
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
