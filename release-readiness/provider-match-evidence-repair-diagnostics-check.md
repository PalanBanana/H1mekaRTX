# Provider Match Evidence Repair Diagnostics Check

- Decision: `PASS_PROVIDER_MATCH_EVIDENCE_REPAIR_DIAGNOSTICS_READY`
- Read-Only Diagnostics Only: `True`
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
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-evidence-repair-diagnostics.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/provider-match-evidence-repair-diagnostics.md |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/provider-match-evidence-repair-diagnostics-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/provider-match-evidence-repair-diagnostics-summary.md |
| `phase60_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provider-match-without-open-readiness-gate.json |
| `phase59_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/dext-load-provider-match-status-evidence.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase60_schema` | PASS | phase60 schema |
| `phase59_schema` | PASS | phase59 schema |
| `manifest_read_only_diagnostics_only_true` | PASS | read_only_diagnostics_only |
| `summary_read_only_diagnostics_only_true` | PASS | read_only_diagnostics_only |
| `manifest_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `summary_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `manifest_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `summary_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
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
| `derived_host_bundle_exists_recorded` | PASS | host_bundle_exists |
| `derived_dext_bundle_exists_recorded` | PASS | dext_bundle_exists |
| `derived_host_info_parse_ok_recorded` | PASS | host_info_parse_ok |
| `derived_dext_info_parse_ok_recorded` | PASS | dext_info_parse_ok |
| `derived_host_bundle_id_matches_recorded` | PASS | host_bundle_id_matches |
| `derived_dext_bundle_id_matches_recorded` | PASS | dext_bundle_id_matches |
| `derived_dext_personalities_present_recorded` | PASS | dext_personalities_present |
| `derived_dext_personality_provider_class_matches_recorded` | PASS | dext_personality_provider_class_matches |
| `derived_dext_personality_iopcimatch_matches_recorded` | PASS | dext_personality_iopcimatch_matches |
| `derived_systemextensionsctl_available_recorded` | PASS | systemextensionsctl_available |
| `derived_ioreg_available_recorded` | PASS | ioreg_available |
| `derived_provider_open_still_blocked_recorded` | PASS | provider_open_still_blocked |
| `derived_ioserviceopen_still_blocked_recorded` | PASS | ioserviceopen_still_blocked |
| `derived_bar_mapping_still_blocked_recorded` | PASS | bar_mapping_still_blocked |
| `derived_gpu_command_submission_still_blocked_recorded` | PASS | gpu_command_submission_still_blocked |
| `derived_dock_transparency_blur_proof_still_blocked_recorded` | PASS | dock_transparency_blur_proof_still_blocked |
| `repair_decision_present` | PASS | repair decision |
| `repair_provider_open_allowed_false` | PASS | provider open false |
| `repair_ready_recorded` | PASS | repair ready |
| `no_raw_stdout_key_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | command_key |
| `no_home_path_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | home_path |
| `no_tmp_path_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | tmp_path |
| `no_email_like_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | email_like |
| `no_developer_id_application_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | developer_id_application |
| `no_apple_development_in_provider-match-evidence-repair-diagnostics-summary.json` | PASS | apple_development |
| `no_raw_stdout_key_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | command_key |
| `no_home_path_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | home_path |
| `no_tmp_path_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | tmp_path |
| `no_email_like_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | email_like |
| `no_developer_id_application_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | developer_id_application |
| `no_apple_development_in_provider-match-evidence-repair-diagnostics-summary.md` | PASS | apple_development |
