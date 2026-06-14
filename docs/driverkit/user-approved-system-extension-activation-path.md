# User-Approved System Extension Activation Path

## Purpose

Phase 46 adds an official user-approved SystemExtensions activation/deactivation path to the host scaffold.

This phase adds activation-capable source code but does not execute activation in CI.

This phase allows future local manual testing only when the user explicitly runs the host with:

- --submit-activation
- --submit-deactivation

Default mode remains status-only.

Dry-run mode remains non-submitting.

This phase does not automatically approve anything.

This phase does not bypass System Settings approval.

This phase does not bypass SIP.

This phase does not bypass AMFI.

This phase does not install anything in CI.

This phase does not activate a System Extension in CI.

This phase does not deactivate a System Extension in CI.

This phase does not load a dext in CI.

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

## Manual Approval Policy

Manual approval is allowed only for an intentionally started local test.

Required manual preconditions before running submit mode in a future phase:

- signed host app exists
- signed dext exists
- bundle IDs match
- entitlements are valid
- disposable test environment is used
- rollback/deactivation command is available
- user is physically present to approve
- no provider open path is enabled
- no BAR mapping path is enabled
- no GPU command submission path is enabled

## Classification

- CLASSIFICATION_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH
- CLASSIFICATION_REAL_DEVELOPMENT_BUILD_SCOPE
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_CI_RUNTIME_ACTIVATION

## Current State

- USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH_READY: True
- ACTIVATION_CAPABLE_CODE_ADDED: True
- DEACTIVATION_CAPABLE_CODE_ADDED: True
- DEFAULT_MODE_STATUS_ONLY: True
- DRY_RUN_MODE_NON_SUBMITTING: True
- CI_ACTIVATION_ATTEMPTED: False
- CI_DEACTIVATION_ATTEMPTED: False
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
