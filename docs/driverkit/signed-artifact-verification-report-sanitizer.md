# Signed Artifact Verification Report Sanitizer

## Purpose

Phase 55 adds a sanitizer for local signing and verification reports.

This phase summarizes the local signing report without committing raw stdout, raw stderr, absolute local paths, signing identity names, certificate details, or entitlement dump bodies.

This phase may read:

- host-report-bundle/local-signing/actual-local-signing-hard-optin-report.json

This phase commits only sanitized release-readiness outputs.

This phase does not execute codesign signing.

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

## Sanitized Summary Policy

Allowed committed fields:

- local signing report present flag
- local signing decision
- hard opt-in satisfied flag
- local scope ok flag
- codesign executed flag
- codesign signing attempted flag
- signed package created flag
- each signing/verification command return code
- each signing/verification command stdout/stderr present flag
- derived verification booleans
- activation blocked flag
- provider-open blocked flag
- BAR mapping blocked flag
- GPU command submission blocked flag

Forbidden committed fields:

- raw stdout
- raw stderr
- full signing identity
- certificate names
- certificate hashes
- entitlement dump bodies
- absolute user paths
- host-report-bundle raw artifact paths

## Classification

- CLASSIFICATION_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER
- CLASSIFICATION_ACTUAL_LOCAL_SIGNING_HARD_OPTIN
- CLASSIFICATION_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_LOCAL_REPORT_SANITIZER_ONLY

## Current State

- SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER_READY: True
- LOCAL_REPORT_SANITIZER_ONLY: True
- RAW_STDOUT_NOT_COMMITTED: True
- RAW_STDERR_NOT_COMMITTED: True
- SIGNING_IDENTITY_NOT_COMMITTED: True
- ENTITLEMENT_DUMP_BODY_NOT_COMMITTED: True
- CODESIGN_EXECUTED_BY_SANITIZER: False
- CODESIGN_SIGNING_ATTEMPTED_BY_SANITIZER: False
- SIGNED_PACKAGE_CREATED_BY_SANITIZER: False
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
