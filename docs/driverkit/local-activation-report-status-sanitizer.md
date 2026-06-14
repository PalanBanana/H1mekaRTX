# Local Activation Report + System Extension Status Sanitizer

## Purpose

Phase 58 summarizes the local activation report and systemextensionsctl status without committing raw local logs.

This phase may read:

- host-report-bundle/local-activation/actual-local-activation-hard-optin-report.json

This phase may run:

- systemextensionsctl list

This phase commits only sanitized release-readiness summaries.

This phase does not submit activation.

This phase does not submit deactivation.

This phase does not install anything.

This phase does not load a dext manually.

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

## Sanitized Fields

Allowed committed fields:

- local activation report present
- local activation decision
- activation submitted flag
- activation command return code
- systemextensionsctl available flag
- systemextensionsctl return code
- extension identifier observed flag
- sanitized status tokens if detected
- runtime safety boundary booleans

Forbidden committed fields:

- raw stdout
- raw stderr
- absolute user paths
- signing identity
- certificate hashes
- entitlement dump bodies

## Classification

- CLASSIFICATION_LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER
- CLASSIFICATION_ACTUAL_LOCAL_ACTIVATION_HARD_OPTIN
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_PROVIDER_OPEN_NO_BAR_NO_GPU_COMMANDS

## Current State

- LOCAL_ACTIVATION_REPORT_STATUS_SANITIZER_READY: True
- SANITIZER_ONLY: True
- RAW_STDOUT_NOT_COMMITTED: True
- RAW_STDERR_NOT_COMMITTED: True
- ACTIVATION_SUBMITTED_BY_SANITIZER: False
- DEACTIVATION_SUBMITTED_BY_SANITIZER: False
- INSTALL_ATTEMPTED: False
- PROVIDER_OPEN_ATTEMPTED: False
- BAR_MAPPING_ATTEMPTED: False
- BAR_MMIO_MUTATION_ATTEMPTED: False
- CONFIGURATION_WRITES_ATTEMPTED: False
- GPU_COMMAND_SUBMISSION_ATTEMPTED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
