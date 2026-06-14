# Provider Match Personality / Entitlement / Activation Visibility Fix Plan

## Purpose

Phase 60C records a fix plan for provider-match readiness when Phase 60B is blocked.

Observed Phase 60B block reasons may include:

- extension_status_observed_false
- repaired_provider_match_ready_false

This means the local activation command may have completed, but the expected dext identifier is not yet observed in sanitized system extension status evidence.

This phase is a fix plan only.

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

## Likely Fix Areas

1. Activation host wait/visibility hardening

The activation host must submit OSSystemExtensionRequest and wait long enough for delegate callbacks or systemextensionsctl visibility.

2. Exact extension identifier confirmation

The submitted identifier must match:

- dev.h1meka.H1mekaRTXDriver

3. Bundle layout confirmation

The dext must remain embedded at:

- H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext

4. IOKit personality confirmation

The dext Info.plist must contain:

- CFBundleIdentifier: dev.h1meka.H1mekaRTXDriver
- IOProviderClass: IOPCIDevice
- IOPCIMatch: 0x2f0410de

5. Entitlement confirmation

The signed dext entitlements must include DriverKit and PCI transport entitlement expectations.

6. Developer-mode / approval status confirmation

systemextensionsctl list must be captured after activation and after any user approval.

## Next Implementation Path

If Phase 60B is blocked because extension_status_observed_false, the next implementation phase should be:

- Phase 60D activation wait + system extension visibility hardening

Phase 60D should:

- add --wait-seconds to the activation script
- capture systemextensionsctl list repeatedly
- detect extension identifier visibility after submit
- preserve activation raw output under host-report-bundle only
- keep provider open blocked
- keep IOServiceOpen blocked
- keep BAR mapping blocked
- keep GPU command submission blocked

## Classification

- CLASSIFICATION_PROVIDER_MATCH_PERSONALITY_ENTITLEMENT_FIX_PLAN
- CLASSIFICATION_PROVIDER_MATCH_REPAIR_READINESS_BRIDGE
- CLASSIFICATION_FIX_PLAN_ONLY
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- PROVIDER_MATCH_PERSONALITY_ENTITLEMENT_FIX_PLAN_READY: True
- FIX_PLAN_ONLY: True
- PROVIDER_OPEN_ALLOWED_NOW: False
- IOSERVICEOPEN_ALLOWED_NOW: False
- BAR_MAPPING_ALLOWED_NOW: False
- GPU_COMMAND_SUBMISSION_ALLOWED_NOW: False
- ACTIVATION_SUBMITTED_BY_THIS_PHASE: False
- DEACTIVATION_SUBMITTED_BY_THIS_PHASE: False
- INSTALL_ATTEMPTED: False
- MANUAL_DEXT_LOAD_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- IOSERVICEOPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
