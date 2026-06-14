# Dext Load + Provider Match Status Check

- Decision: `PASS_DEXT_LOAD_PROVIDER_MATCH_STATUS_EVIDENCE_READY`
- Read-Only Status Evidence Only: `True`
- Activation Submitted By This Phase: `False`
- Deactivation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/dext-load-provider-match-status-evidence.md |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/dext-load-provider-match-status-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/dext-load-provider-match-status-summary.md |
| `phase58_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/local-activation-report-status-sanitizer.json |
| `phase57b_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-activation-hard-optin.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase58_schema` | PASS | phase58 schema |
| `phase57b_schema` | PASS | phase57b schema |
| `manifest_read_only_status_evidence_only_true` | PASS | read_only_status_evidence_only |
| `manifest_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `manifest_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `manifest_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `summary_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `manifest_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `summary_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `summary_install_attempted_false` | PASS | install_attempted |
| `manifest_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `summary_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `summary_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `summary_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `summary_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `summary_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `summary_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `summary_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `summary_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `summary_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `activation_report_present` | PASS | activation report |
| `activation_command_completed_recorded` | PASS | activation command completed |
| `systemextensionsctl_available_recorded` | PASS | systemextensionsctl |
| `ioreg_available_recorded` | PASS | ioreg |
| `rtx_vendor_recorded` | PASS | vendor |
| `rtx_device_recorded` | PASS | device |
| `provider_match_readiness_present` | PASS | readiness |
| `provider_open_allowed_false` | PASS | provider open false |
| `derived_provider_open_still_blocked_true` | PASS | provider_open_still_blocked |
| `derived_ioserviceopen_still_blocked_true` | PASS | ioserviceopen_still_blocked |
| `derived_bar_mapping_still_blocked_true` | PASS | bar_mapping_still_blocked |
| `derived_gpu_command_submission_still_blocked_true` | PASS | gpu_command_submission_still_blocked |
| `derived_dock_transparency_blur_proof_still_blocked_true` | PASS | dock_transparency_blur_proof_still_blocked |
| `no_raw_stdout_key_in_dext-load-provider-match-status-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_dext-load-provider-match-status-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_dext-load-provider-match-status-summary.json` | PASS | command_key |
| `no_home_path_in_dext-load-provider-match-status-summary.json` | PASS | home_path |
| `no_tmp_path_in_dext-load-provider-match-status-summary.json` | PASS | tmp_path |
| `no_email_like_in_dext-load-provider-match-status-summary.json` | PASS | email_like |
| `no_developer_id_application_in_dext-load-provider-match-status-summary.json` | PASS | developer_id_application |
| `no_apple_development_in_dext-load-provider-match-status-summary.json` | PASS | apple_development |
| `no_raw_stdout_key_in_dext-load-provider-match-status-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_dext-load-provider-match-status-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_dext-load-provider-match-status-summary.md` | PASS | command_key |
| `no_home_path_in_dext-load-provider-match-status-summary.md` | PASS | home_path |
| `no_tmp_path_in_dext-load-provider-match-status-summary.md` | PASS | tmp_path |
| `no_email_like_in_dext-load-provider-match-status-summary.md` | PASS | email_like |
| `no_developer_id_application_in_dext-load-provider-match-status-summary.md` | PASS | developer_id_application |
| `no_apple_development_in_dext-load-provider-match-status-summary.md` | PASS | apple_development |
