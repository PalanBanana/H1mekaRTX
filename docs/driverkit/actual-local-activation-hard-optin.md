# Actual Local Activation Script With Hard Opt-In

## Purpose

Phase 57B adds an actual local System Extension activation script guarded by hard opt-in flags.

This phase adds the script only.

CI verification must not submit activation.

The activation script is allowed to submit a local activation request only when all hard opt-in flags are passed by the user.

This phase keeps provider open blocked.

This phase keeps BAR mapping blocked.

This phase keeps BAR/MMIO mutation blocked.

This phase keeps PCI configuration writes blocked.

This phase keeps firmware load blocked.

This phase keeps GPU reset blocked.

This phase keeps framebuffer/display-engine init blocked.

This phase keeps GPU command submission blocked.

This phase keeps Metal proof blocked.

This phase keeps Dock/transparency/blur proof blocked.

## Required Runtime Flags For Actual Activation

Actual activation is allowed only when all flags are present:

- --i-understand-local-activation
- --submit-activation
- --signing-identity <IDENTITY_OR_SHA1>
- --output-under-host-report-bundle

## What The Script May Do With Opt-In

- require Phase 56 activation_preflight_ready=true
- rebuild activation-capable Swift host executable into the local app bundle
- re-sign embedded dext
- re-sign host app
- capture systemextensionsctl list before activation
- run the signed host executable with --submit-activation
- capture systemextensionsctl list after activation
- write local-only activation report under host-report-bundle

## What The Script Must Not Do

- no provider open
- no BAR mapping
- no BAR/MMIO mutation
- no PCI configuration writes
- no firmware load
- no GPU reset
- no framebuffer/display-engine init
- no GPU command submission
- no UI compositor proof claim
- no Metal proof claim
- no Dock/transparency/blur acceleration claim

## Classification

- CLASSIFICATION_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN
- CLASSIFICATION_MANUAL_ACTIVATION_PREFLIGHT_AFTER_SIGNED_VERIFICATION
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN_READY: True
- DEFAULT_REFUSES_ACTIVATION: True
- HARD_OPTIN_FLAGS_REQUIRED: True
- CI_ACTIVATION_ATTEMPTED: False
- ACTIVATION_SUBMITTED_BY_DEFAULT: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
