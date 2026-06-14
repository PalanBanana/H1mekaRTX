# ValidationFailed Root-Cause Gate

## Purpose

Phase 60K summarizes local validationFailed diagnostics after /Applications staging.

Observed local state:

- /Applications staging succeeded
- activation was submitted from /Applications
- delegate failed with OSSystemExtensionErrorDomain code 9
- plist validation passed
- codesign verify passed
- spctl rejected host app
- spctl rejected dext
- dext executable is a generic Mach-O executable, not proven as a real DriverKit-built driver binary
- embedded DriverKit and PCI transport entitlements are present in the signature output, but approval/provisioning validity is not proven

This phase commits only sanitized release-readiness output.

This phase does not submit activation.

This phase does not submit deactivation.

This phase does not install anything.

This phase does not manually load a dext.

This phase does not open a provider.

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

## Root-Cause Categories

Phase 60K classifies validationFailed into these likely blockers:

1. Gatekeeper / spctl rejection

The app and dext are currently rejected by spctl.

2. Development mode not proven

Developer-mode status is not yet recorded in sanitized output.

3. DriverKit entitlement approval not proven

The signature shows requested entitlements, but Apple-approved entitlement/provisioning validity is not proven.

4. PCI transport entitlement approval not proven

The signature shows PCI transport entries, but actual OS validation acceptance is not proven.

5. Real DriverKit binary not proven

The dext executable is currently a generic Mach-O stub. A real Xcode-built DriverKit dext binary is required before provider match/open work can progress.

## Recommended Next Gate

Phase 60L should create a real buildable DriverKit dext target/project plan and local build gate.

Phase 60L must still keep:

- provider open blocked
- IOServiceOpen blocked
- BAR mapping blocked
- GPU command submission blocked
- Metal proof blocked
- Dock/transparency/blur proof blocked

## Classification

- CLASSIFICATION_VALIDATIONFAILED_ROOT_CAUSE_GATE
- CLASSIFICATION_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION
- CLASSIFICATION_REMEDIATION_GATE_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS
