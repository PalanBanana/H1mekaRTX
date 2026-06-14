# Compile-Only Failure Sanitizer Summary

## Purpose

Phase 45 summarizes Phase 44 compile-only smoke-test results without committing raw local stdout or stderr.

This phase is sanitizer-summary only.

This phase may read the local-only Phase 44 report from host-report-bundle.

This phase commits only sanitized release-readiness summaries.

This phase does not create build artifacts.

This phase does not sign anything.

This phase does not install anything.

This phase does not activate a System Extension.

This phase does not deactivate a System Extension.

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

- target name
- command key
- tool available flag
- return code
- failed flag
- stdout present flag
- stderr present flag
- plist parse status
- compile-only attempt recorded flag

Forbidden committed fields:

- raw stdout
- raw stderr
- private absolute paths
- email-like identifiers
- host-report-bundle raw artifact content
- user home paths
- temporary folder paths

## Classification

- CLASSIFICATION_COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY
- CLASSIFICATION_COMPILE_ONLY_TARGET_SMOKE_TEST
- CLASSIFICATION_REAL_DEVELOPMENT_BUILD_SCOPE
- CLASSIFICATION_NO_RUNTIME_ACTIVATION

## Current State

- COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY_READY: True
- COMPILE_ONLY_FAILURE_SANITIZER_SUMMARY_ONLY: True
- RAW_STDOUT_NOT_COMMITTED: True
- RAW_STDERR_NOT_COMMITTED: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- BUILD_ARTIFACT_CREATED: False
- SIGNING_ATTEMPTED: False
- INSTALL_ATTEMPTED: False
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
