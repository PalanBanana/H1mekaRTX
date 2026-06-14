# Actual Local Signing Script With Hard Opt-In

## Purpose

Phase 54 adds an actual local signing script guarded by hard opt-in flags.

This phase adds a script that can sign the local unsigned host+dext bundle only when the user explicitly passes all required flags.

Default behavior is refusal.

CI verification must not execute signing.

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

## Required Runtime Flags For Actual Signing

Actual signing is allowed only when all flags are present:

- --i-understand-local-signing
- --signing-identity <IDENTITY>
- --output-under-host-report-bundle

## Signing Scope

Allowed only for local paths under:

- host-report-bundle/unsigned-app-bundle/H1mekaRTXHost.app

Signing order:

1. sign embedded dext first
2. verify embedded dext
3. sign host app second
4. verify host app
5. dump host entitlements locally
6. dump dext entitlements locally
7. write local signed artifact report under host-report-bundle

## Activation Boundary

Even after signing succeeds:

- activation remains blocked
- deactivation remains blocked
- dext load remains blocked
- provider open remains blocked
- BAR mapping remains blocked
- GPU command submission remains blocked
- Dock/transparency/blur proof remains blocked

## Classification

- CLASSIFICATION_ACTUAL_LOCAL_SIGNING_HARD_OPTIN
- CLASSIFICATION_MANUAL_LOCAL_SIGNING_OPT_IN_GATE
- CLASSIFICATION_LOCAL_SIGNING_ONLY
- CLASSIFICATION_NO_INSTALL_NO_ACTIVATION

## Current State

- ACTUAL_LOCAL_SIGNING_HARD_OPTIN_READY: True
- DEFAULT_REFUSES_SIGNING: True
- HARD_OPTIN_FLAGS_REQUIRED: True
- CI_SIGNING_ATTEMPTED: False
- CODESIGN_EXECUTED_BY_DEFAULT: False
- CODESIGN_SIGNING_ATTEMPTED_IN_CI: False
- SIGNED_PACKAGE_CREATED_IN_CI: False
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
