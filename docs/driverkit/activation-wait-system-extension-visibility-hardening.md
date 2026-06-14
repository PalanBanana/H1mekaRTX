# Activation Wait + System Extension Visibility Hardening

## Purpose

Phase 60D adds a hard opt-in local activation visibility hardening script.

Phase 60B was blocked because the expected extension identifier was not observed in sanitized system extension status evidence.

This phase adds a script that can rerun local activation and poll systemextensionsctl until the extension identifier becomes visible or a timeout expires.

Default behavior refuses activation.

CI verification must not submit activation.

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

## Required Runtime Flags

Actual local activation visibility hardening is allowed only when all flags are present:

- --i-understand-local-activation-visibility
- --submit-activation
- --signing-identity <IDENTITY_OR_SHA1>
- --output-under-host-report-bundle

Optional:

- --wait-seconds <N>
- --poll-interval-seconds <N>

## What The Script May Do With Opt-In

- verify Phase 56 activation_preflight_ready=true
- rebuild activation-capable Swift host executable into the local app bundle
- re-sign embedded dext
- re-sign host app
- submit activation using the signed host executable
- capture systemextensionsctl list repeatedly
- detect dev.h1meka.H1mekaRTXDriver visibility
- write local-only raw activation visibility report under host-report-bundle

## What The Script Must Not Do

- no provider open
- no IOServiceOpen
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

- CLASSIFICATION_ACTIVATION_WAIT_SYSTEM_EXTENSION_VISIBILITY_HARDENING
- CLASSIFICATION_PROVIDER_MATCH_PERSONALITY_ENTITLEMENT_FIX_PLAN
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- ACTIVATION_WAIT_VISIBILITY_HARDENING_READY: True
- DEFAULT_REFUSES_ACTIVATION: True
- HARD_OPTIN_FLAGS_REQUIRED: True
- CI_ACTIVATION_ATTEMPTED: False
- ACTIVATION_SUBMITTED_BY_DEFAULT: False
- PROVIDER_OPEN_ATTEMPTED: False
- IOSERVICEOPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
