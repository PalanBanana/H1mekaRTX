# Manual Local Signing Opt-In Gate

## Purpose

Phase 53 adds a manual local signing opt-in gate for H1mekaRTX.

This phase records that local signing may be allowed later only when the user explicitly opts in.

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

## User Opt-In Position

- USER_MAY_OPT_IN_TO_LOCAL_SIGNING: True
- LOCAL_SIGNING_REQUIRES_EXPLICIT_FLAG: True
- LOCAL_SIGNING_ALLOWED_NOW: False
- CODESIGN_EXECUTED: False

## Required Before Actual Signing

Before actual local signing in a future phase:

- codesign dry-run command plan exists
- unsigned bundle manifest lock exists
- codesign identity evidence exists
- host entitlement parse proof exists
- dext entitlement parse proof exists
- host bundle ID matches
- dext bundle ID matches
- user passes an explicit future signing flag
- signing identity is selected explicitly
- signing output remains local-only
- signed artifact manifest is generated
- activation remains blocked after signing until verify gates pass

## Future Signing Safety Order

1. confirm user opt-in flag
2. choose signing identity explicitly
3. sign embedded dext first
4. verify embedded dext
5. sign host app second
6. verify host app
7. dump host entitlements
8. dump dext entitlements
9. create signed artifact manifest
10. keep activation blocked until separate activation gate

## Classification

- CLASSIFICATION_MANUAL_LOCAL_SIGNING_OPT_IN_GATE
- CLASSIFICATION_CODESIGN_DRYRUN_COMMAND_PLAN
- CLASSIFICATION_NO_SIGNING_NO_INSTALL_NO_ACTIVATION
- CLASSIFICATION_COMMAND_GATE_ONLY

## Current State

- MANUAL_LOCAL_SIGNING_OPT_IN_GATE_READY: True
- USER_MAY_OPT_IN_TO_LOCAL_SIGNING: True
- LOCAL_SIGNING_REQUIRES_EXPLICIT_FLAG: True
- LOCAL_SIGNING_ALLOWED_NOW: False
- COMMAND_GATE_ONLY: True
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
