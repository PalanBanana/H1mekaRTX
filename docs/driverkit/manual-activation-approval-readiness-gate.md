# Manual Activation Approval Readiness Gate

## Purpose

Phase 47 records that the user is willing to approve a future local System Extension activation prompt.

This phase does not submit an activation request.

This phase does not submit a deactivation request.

This phase does not install anything.

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

## User Approval Position

- USER_WILL_APPROVE_FUTURE_LOCAL_PROMPT: True
- MANUAL_APPROVAL_ALLOWED_FOR_FUTURE_LOCAL_TEST: True
- AUTO_APPROVAL_NOT_POSSIBLE: True
- USER_MUST_APPROVE_IN_SYSTEM_SETTINGS_IF_PROMPTED: True

## Still Required Before Submit Mode

Before running the host with --submit-activation in a future phase, all of the following must be true:

- signed host app exists
- signed dext exists
- host app contains the dext under Contents/Library/SystemExtensions
- host app bundle ID is dev.h1meka.H1mekaRTXHost
- dext bundle ID is dev.h1meka.H1mekaRTXDriver
- entitlements are valid
- DriverKit entitlement is approved
- PCI transport entitlement is approved
- Team ID is known
- signing identity is valid
- rollback/deactivation command is available
- disposable test environment is confirmed
- systemextensionsctl status is captured before submit
- activation logs are captured locally only
- no provider-open path is enabled
- no BAR mapping path is enabled
- no GPU command submission path is enabled

## Dock / Transparency / Blur Timing

Dock/transparency/blur proof remains blocked until these future milestones are proven:

1. signed host+dext packaging proof
2. manual user-approved activation proof
3. manual deactivation/rollback proof
4. dext load proof
5. provider match proof
6. safe provider-open proof
7. read-only device evidence proof
8. real GPU command execution proof
9. RTX 5070 workload attribution proof
10. WindowServer/Core Animation/QuartzCore/Metal compositor attribution proof
11. before/after UI frame pacing and latency measurement proof
12. Dock/transparency/blur scenario proof

## Classification

- CLASSIFICATION_MANUAL_ACTIVATION_APPROVAL_READINESS_GATE
- CLASSIFICATION_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH
- CLASSIFICATION_OFFICIAL_SYSTEMEXTENSIONS_PATH
- CLASSIFICATION_NO_SUBMIT_IN_CI

## Current State

- MANUAL_ACTIVATION_APPROVAL_READINESS_GATE_READY: True
- USER_WILL_APPROVE_FUTURE_LOCAL_PROMPT: True
- MANUAL_APPROVAL_ALLOWED_FOR_FUTURE_LOCAL_TEST: True
- SUBMIT_ACTIVATION_ALLOWED_NOW: False
- SUBMIT_DEACTIVATION_ALLOWED_NOW: False
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
