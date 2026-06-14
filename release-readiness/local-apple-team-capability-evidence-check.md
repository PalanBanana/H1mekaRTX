# Local Apple Team Capability Evidence Check

- Decision: `PASS_LOCAL_APPLE_TEAM_CAPABILITY_EVIDENCE_READY`
- Local Evidence Only: `True`
- Raw Outputs Local Only: `True`
- Phase 61 Allowed Now: `False`
- Xcodebuild Build Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/local-apple-team-capability-evidence-collector.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/local-apple-team-capability-evidence-collector.md |
| `collector_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/collect-local-apple-team-capability-evidence.py |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-apple-team-capability-evidence-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-apple-team-capability-evidence-summary.md |
| `phase60r_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/apple-developer-entitlement-request-checklist.json |
| `phase60q_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/provisioning-entitlement-hardblock-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase60r_schema` | PASS | phase60r schema |
| `phase60q_schema` | PASS | phase60q schema |
| `manifest_local_apple_team_capability_evidence_collector_ready_true` | PASS | local_apple_team_capability_evidence_collector_ready |
| `manifest_local_evidence_only_true` | PASS | local_evidence_only |
| `manifest_raw_outputs_local_only_true` | PASS | raw_outputs_local_only |
| `manifest_xcodebuild_build_attempted_by_this_phase_false` | PASS | xcodebuild_build_attempted_by_this_phase |
| `summary_xcodebuild_build_attempted_by_this_phase_false` | PASS | xcodebuild_build_attempted_by_this_phase |
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
| `collector_contains_xcodebuild` | PASS | xcodebuild |
| `collector_contains__showBuildSettings` | PASS | -showBuildSettings |
| `collector_contains_security` | PASS | security |
| `collector_contains_find_identity` | PASS | find-identity |
| `collector_contains_Personal_development_teams` | PASS | Personal development teams |
| `collector_contains_Please_enable_Driverkit` | PASS | Please enable Driverkit |
| `collector_contains_dev_h1meka_H1mekaRTXHost` | PASS | dev.h1meka.H1mekaRTXHost |
| `collector_contains_dev_h1meka_H1mekaRTXDriver` | PASS | dev.h1meka.H1mekaRTXDriver |
| `collector_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `collector_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `collector_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `collector_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
| `summary_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `summary_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `summary_xcode_present_recorded` | PASS | xcode_present |
| `summary_driverkit_sdk_present_recorded` | PASS | driverkit_sdk_present |
| `summary_macosx_sdk_present_recorded` | PASS | macosx_sdk_present |
| `summary_apple_development_identity_present_recorded` | PASS | apple_development_identity_present |
| `summary_xcode_project_present_recorded` | PASS | xcode_project_present |
| `summary_personal_team_blocker_observed_recorded` | PASS | personal_team_blocker_observed |
| `summary_system_extension_capability_blocker_observed_recorded` | PASS | system_extension_capability_blocker_observed |
| `summary_driverkit_enable_blocker_observed_recorded` | PASS | driverkit_enable_blocker_observed |
| `summary_host_profile_missing_observed_recorded` | PASS | host_profile_missing_observed |
| `summary_dext_profile_missing_observed_recorded` | PASS | dext_profile_missing_observed |
| `summary_paid_team_proven_recorded` | PASS | paid_team_proven |
| `summary_driverkit_entitlement_approval_proven_recorded` | PASS | driverkit_entitlement_approval_proven |
| `summary_pci_transport_entitlement_approval_proven_recorded` | PASS | pci_transport_entitlement_approval_proven |
| `summary_system_extension_capability_proven_recorded` | PASS | system_extension_capability_proven |
| `summary_phase61_allowed_now_recorded` | PASS | phase61_allowed_now |
| `summary_phase61_false` | PASS | phase61 false |
| `summary_provider_open_false` | PASS | provider false |
| `no_raw_stdout_key_in_local-apple-team-capability-evidence-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_local-apple-team-capability-evidence-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_local-apple-team-capability-evidence-summary.json` | PASS | command_key |
| `no_home_path_in_local-apple-team-capability-evidence-summary.json` | PASS | home_path |
| `no_tmp_path_in_local-apple-team-capability-evidence-summary.json` | PASS | tmp_path |
| `no_email_like_in_local-apple-team-capability-evidence-summary.json` | PASS | email_like |
| `no_apple_development_in_local-apple-team-capability-evidence-summary.json` | PASS | apple_development |
| `no_developer_id_application_in_local-apple-team-capability-evidence-summary.json` | PASS | developer_id_application |
| `no_raw_stdout_key_in_local-apple-team-capability-evidence-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_local-apple-team-capability-evidence-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_local-apple-team-capability-evidence-summary.md` | PASS | command_key |
| `no_home_path_in_local-apple-team-capability-evidence-summary.md` | PASS | home_path |
| `no_tmp_path_in_local-apple-team-capability-evidence-summary.md` | PASS | tmp_path |
| `no_email_like_in_local-apple-team-capability-evidence-summary.md` | PASS | email_like |
| `no_apple_development_in_local-apple-team-capability-evidence-summary.md` | PASS | apple_development |
| `no_developer_id_application_in_local-apple-team-capability-evidence-summary.md` | PASS | developer_id_application |
