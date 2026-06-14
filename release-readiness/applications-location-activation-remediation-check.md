# Applications Location Activation Remediation Check

- Decision: `PASS_APPLICATIONS_LOCATION_ACTIVATION_REMEDIATION_READY`
- Default Refuses Staging: `True`
- Default Refuses Activation: `True`
- CI Staging Attempted: `False`
- CI Activation Attempted: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/applications-location-activation-remediation.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/applications-location-activation-remediation.md |
| `script_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/applications-location-activation-remediation.py |
| `phase60g_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/activation-error-remediation-plan.json |
| `phase60f_summary_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/activation-delegate-diagnostics-remediation-summary.json |
| `manifest_schema` | PASS | manifest schema |
| `phase60g_schema` | PASS | phase60g schema |
| `phase60f_summary_schema` | PASS | phase60f summary schema |
| `manifest_applications_location_activation_remediation_ready_true` | PASS | applications_location_activation_remediation_ready |
| `manifest_default_refuses_staging_true` | PASS | default_refuses_staging |
| `manifest_default_refuses_activation_true` | PASS | default_refuses_activation |
| `manifest_hard_optin_flags_required_true` | PASS | hard_optin_flags_required |
| `manifest_ci_staging_attempted_false` | PASS | ci_staging_attempted |
| `manifest_ci_activation_attempted_false` | PASS | ci_activation_attempted |
| `manifest_activation_submitted_by_default_false` | PASS | activation_submitted_by_default |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `script_contains___i_understand_applications_staging` | PASS | --i-understand-applications-staging |
| `script_contains___stage_to_applications` | PASS | --stage-to-applications |
| `script_contains___submit_activation` | PASS | --submit-activation |
| `script_contains___signing_identity` | PASS | --signing-identity |
| `script_contains___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
| `script_contains___replace_existing` | PASS | --replace-existing |
| `script_contains___use_sudo` | PASS | --use-sudo |
| `script_contains__Applications_H1mekaRTXHost.app` | PASS | /Applications/H1mekaRTXHost.app |
| `script_contains_ditto` | PASS | ditto |
| `script_contains_systemextensionsctl` | PASS | systemextensionsctl |
| `script_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `script_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `script_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `script_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
| `phase60f_error_domain_os_system_extension` | PASS | OSSystemExtensionErrorDomain |
| `phase60f_error_code_3` | PASS | 3 |
