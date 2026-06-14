# Baseline Privacy / Redaction Audit Gate

## Purpose

This Phase 38 contract defines a privacy and redaction audit gate for local UI baseline summaries.

This phase audits committed release-readiness outputs to ensure local baseline summaries do not include raw local logs, raw command stdout, private home paths, email-like identifiers, or host-report-bundle raw artifacts.

This phase does not collect new local logs.

This phase does not commit host-report-bundle outputs.

This phase does not measure real acceleration.

This phase does not prove UI compositor acceleration.

This phase does not claim Dock acceleration.

This phase does not claim transparency acceleration.

This phase does not claim blur acceleration.

This phase does not claim Mission Control acceleration.

This phase does not claim Launchpad acceleration.

This phase does not claim Stage Manager acceleration.

This phase does not open a provider.

This phase does not map BAR memory.

This phase does not write PCI configuration space.

This phase does not read or write MMIO.

This phase does not submit GPU commands.

This phase does not load firmware.

This phase does not reset the GPU.

This phase does not initialize framebuffer or display-engine paths.

This phase does not load a dext.

This phase does not execute activation or deactivation.


## Sanitization Step

Before the privacy/redaction audit runs, committed release-readiness local UI baseline summaries are sanitized:

- repository root paths are replaced with `<REPO_ROOT>`
- user home paths are replaced with `<USER_HOME>`
- temporary folder paths are replaced with `<TMP_PATH>`
- raw local host-report-bundle artifact paths are replaced with symbolic placeholders
- raw stdout and stderr content remains excluded

## Audit Policy

BASELINE_PRIVACY_REDACTION_AUDIT_POLICY:

1. host-report-bundle paths must not be staged for commit.
2. release-readiness summaries must not contain raw command stdout.
3. release-readiness summaries must not contain raw command stderr.
4. release-readiness summaries must not contain raw unified log content.
5. release-readiness summaries must not contain private absolute home paths.
6. release-readiness summaries must not contain email-like identifiers.
7. release-readiness summaries must not contain long raw process-table lines.
8. release-readiness summaries may contain boolean summaries and return-code summaries.
9. release-readiness summaries may contain proof-state fields.
10. release-readiness summaries may contain command-key names only.

## Input Scope

BASELINE_PRIVACY_REDACTION_AUDIT_INPUTS:

- release-readiness/local-ui-baseline-artifact-summary.json
- release-readiness/local-ui-baseline-artifact-summary.md
- release-readiness/local-ui-baseline-artifact-summary-check.json
- release-readiness/local-ui-baseline-artifact-summary-check.md
- release-readiness/local-readonly-ui-baseline-check.json
- release-readiness/local-readonly-ui-baseline-check.md

## Local-Only Paths

LOCAL_ONLY_PATHS:

- host-report-bundle/
- host-report-bundle/ui-baseline/
- host-report-bundle/ui-baseline/local-readonly-ui-baseline.json
- host-report-bundle/ui-baseline/local-readonly-ui-baseline.md

These paths must not be staged or committed.

## Allowed Summary Fields

ALLOWED_SUMMARY_FIELDS:

- baseline_artifact_present
- baseline_schema_valid
- baseline_generated_at_utc_present
- windowserver_visibility_recorded
- dock_visibility_recorded
- windowserver_visible
- dock_visible
- windowserver_matching_line_count
- dock_matching_line_count
- displays_json_parse_ok
- hardware_json_parse_ok
- command_summary
- present
- available
- returncode
- stdout_present
- stderr_present
- proof states
- false acceleration claim flags

## Classification

All Phase 38 outputs must be labeled only as:

- CLASSIFICATION_BASELINE_PRIVACY_REDACTION_AUDIT_GATE
- CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER
- CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR
- CLASSIFICATION_STATIC_CONTRACT

## Safety Boundary

Required safety markers:

- BASELINE_PRIVACY_REDACTION_AUDIT_GATE_ONLY: True
- PRIVACY_REDACTION_AUDIT_ONLY: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- HOST_REPORT_BUNDLE_NOT_STAGED: True
- RAW_LOCAL_LOGS_NOT_COMMITTED: True
- RAW_COMMAND_STDOUT_NOT_COMMITTED: True
- RAW_COMMAND_STDERR_NOT_COMMITTED: True
- PRIVATE_PATHS_NOT_COMMITTED: True
- EMAIL_LIKE_IDENTIFIERS_NOT_COMMITTED: True
- MEASUREMENT_NOT_ACCELERATION_PROOF: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True
- FIRMWARE_LOAD_FORBIDDEN: True
- GPU_RESET_FORBIDDEN: True
- FRAMEBUFFER_INIT_FORBIDDEN: True
- DISPLAY_ENGINE_INIT_FORBIDDEN: True
- GPU_COMMAND_SUBMISSION_FORBIDDEN: True
- CONFIGURATION_WRITES_FORBIDDEN: True
- BAR_MAPPING_FORBIDDEN: True
- BAR_MMIO_MUTATION_FORBIDDEN: True
- PROVIDER_OPEN_FORBIDDEN: True
- EXECUTE_MODE_STILL_BLOCKED: True
- LEDGER_READY_REQUIRED_FOR_EXECUTE: True
- REAL_ACTIVATION_NOT_ATTEMPTED: True
- REAL_DEACTIVATION_NOT_ATTEMPTED: True
- NO_DRIVER_ACTIVATION: True
- NO_SYSTEM_EXTENSION_ACTIVATION: True
- NO_SYSTEM_EXTENSION_DEACTIVATION: True
- NO_DEXT_LOAD: True
- NO_PROVIDER_OPEN: True
- NO_BAR_MAPPING: True
- NO_BAR_MMIO_MUTATION: True
- NO_CONFIGURATION_WRITES: True
- NO_COMMAND_SUBMISSION: True
- NO_FIRMWARE_LOAD: True
- NO_GPU_RESET: True
- NO_FRAMEBUFFER_INIT: True
- NO_DISPLAY_ENGINE_INIT: True
- NO_DIRECT_DOCK_INJECTION: True
- NO_WINDOWSERVER_PATCHING: True
- NO_PRIVATE_FRAMEWORK_PATCHING: True
- NO_FAKE_METAL_DEVICE_SPOOFING: True

## Current Proof States

- BASELINE_PRIVACY_REDACTION_AUDIT_STATE: ENFORCED
- LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_STATE: SUMMARY_ONLY
- LOCAL_READONLY_UI_BASELINE_STATE: COLLECTED_OR_UNAVAILABLE
- UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED
- WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- CORE_ANIMATION_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- QUARTZCORE_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- METAL_COMPOSITOR_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_PROOF_STATE: NOT_ATTEMPTED
- RTX5070_WORKLOAD_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED

## Current Contract State

- PHASE38_BASELINE_PRIVACY_REDACTION_AUDIT_GATE_READY: True
- BASELINE_PRIVACY_REDACTION_AUDIT_GATE_ONLY: True
- PRIVACY_REDACTION_AUDIT_ONLY: True
- HOST_REPORT_BUNDLE_LOCAL_ONLY: True
- HOST_REPORT_BUNDLE_NOT_STAGED: True
- RAW_LOCAL_LOGS_NOT_COMMITTED: True
- RAW_COMMAND_STDOUT_NOT_COMMITTED: True
- RAW_COMMAND_STDERR_NOT_COMMITTED: True
- PRIVATE_PATHS_NOT_COMMITTED: True
- EMAIL_LIKE_IDENTIFIERS_NOT_COMMITTED: True
- BASELINE_PRIVACY_REDACTION_AUDIT_STATE: ENFORCED
- MEASUREMENT_NOT_ACCELERATION_PROOF: True
- UI_COMPOSITOR_PROOF_NOT_CLAIMED: True
- METAL_PROOF_NOT_CLAIMED: True
- DOCK_ACCELERATION_NOT_CLAIMED: True
- TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True
- BLUR_ACCELERATION_NOT_CLAIMED: True
- LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_STATE: SUMMARY_ONLY
- UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED
- METAL_PROOF_STATE: NOT_ATTEMPTED
- REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False
- RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False
- REAL_GPU_ACCELERATION_CLAIMED: False
- UI_COMPOSITOR_PROOF_CLAIMED: False
- METAL_PROOF_CLAIMED: False
