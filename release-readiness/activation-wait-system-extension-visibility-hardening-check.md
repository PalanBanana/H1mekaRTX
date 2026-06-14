# Activation Wait System Extension Visibility Hardening Check

- Decision: `PASS_ACTIVATION_WAIT_VISIBILITY_HARDENING_READY`
- Default Refuses Activation: `True`
- Hard Opt-In Flags Required: `True`
- CI Activation Attempted: `False`
- Activation Submitted By Default: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/activation-wait-system-extension-visibility-hardening.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/activation-wait-system-extension-visibility-hardening.md |
| `script_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/activation-wait-system-extension-visibility-hardening.py |
| `phase60c_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-personality-entitlement-fix-plan.json |
| `phase57b_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json |
| `manifest_schema` | PASS | manifest schema |
| `phase60c_schema` | PASS | phase60c schema |
| `phase57b_schema` | PASS | phase57b schema |
| `manifest_activation_wait_visibility_hardening_ready_true` | PASS | activation_wait_visibility_hardening_ready |
| `manifest_default_refuses_activation_true` | PASS | default_refuses_activation |
| `manifest_hard_optin_flags_required_true` | PASS | hard_optin_flags_required |
| `manifest_ci_activation_attempted_false` | PASS | ci_activation_attempted |
| `manifest_activation_submitted_by_default_false` | PASS | activation_submitted_by_default |
| `manifest_deactivation_submitted_by_default_false` | PASS | deactivation_submitted_by_default |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `script_contains___i_understand_local_activation_visibility` | PASS | --i-understand-local-activation-visibility |
| `script_contains___submit_activation` | PASS | --submit-activation |
| `script_contains___signing_identity` | PASS | --signing-identity |
| `script_contains___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
| `script_contains___wait_seconds` | PASS | --wait-seconds |
| `script_contains___poll_interval_seconds` | PASS | --poll-interval-seconds |
| `script_contains_systemextensionsctl` | PASS | systemextensionsctl |
| `script_contains_dev_h1meka_H1mekaRTXDriver` | PASS | dev.h1meka.H1mekaRTXDriver |
| `script_contains_visibility_poll_attempted` | PASS | visibility_poll_attempted |
| `script_contains_extension_identifier_observed` | PASS | extension_identifier_observed |
| `script_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `script_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `script_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `script_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
