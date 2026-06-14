# Codesign Dry-Run Command Plan

## Purpose

Phase 52 defines the exact future codesign command plan for the unsigned local host+dext bundle.

This phase is command-plan only.

This phase does not execute codesign.

This phase does not create signed artifacts.

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

## Future Signing Order

Future local signing must happen in this order:

1. sign embedded dext first
2. verify embedded dext signature
3. sign host app after embedded dext
4. verify host app signature
5. dump host entitlements
6. dump dext entitlements
7. capture systemextensionsctl status before activation

## Planned Commands

The command plan uses placeholders and must not be executed by Phase 52.

- SIGNING_IDENTITY_PLACEHOLDER
- TEAM_ID_PLACEHOLDER
- UNSIGNED_BUNDLE_ROOT_PLACEHOLDER

## Classification

- CLASSIFICATION_CODESIGN_DRYRUN_COMMAND_PLAN
- CLASSIFICATION_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT
- CLASSIFICATION_NO_SIGNING_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_COMMAND_PLAN_ONLY

## Current State

- CODESIGN_DRYRUN_COMMAND_PLAN_READY: True
- COMMAND_PLAN_ONLY: True
- CODESIGN_EXECUTED: False
- CODESIGN_SIGNING_ATTEMPTED: False
- SIGNED_PACKAGE_CREATED: False
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
