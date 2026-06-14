# ValidationFailed Root-Cause Gate Check

- Decision: `PASS_VALIDATIONFAILED_ROOT_CAUSE_GATE_READY`
- Remediation Gate Only: `True`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60l-real-driverkit-dext-build-gate`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/validationfailed-root-cause-gate.md |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/validationfailed-root-cause-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/validationfailed-root-cause-summary.md |
| `phase60i_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/applications-location-activation-remediation.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase60i_schema` | PASS | phase60i schema |
| `manifest_validationfailed_root_cause_gate_ready_true` | PASS | validationfailed_root_cause_gate_ready |
| `manifest_remediation_gate_only_true` | PASS | remediation_gate_only |
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
| `summary_error_domain_code9_recorded` | PASS | OSSystemExtensionErrorDomain/9 |
| `summary_applications_staged` | PASS | staged |
| `summary_activation_submitted` | PASS | activation submitted |
| `summary_spctl_host_rejected_recorded` | PASS | spctl host |
| `summary_spctl_dext_rejected_recorded` | PASS | spctl dext |
| `summary_driverkit_entitlement_recorded` | PASS | driverkit entitlement |
| `summary_pci_entitlement_recorded` | PASS | pci entitlement |
| `summary_xcode_driverkit_binary_proven_recorded` | PASS | real DriverKit binary |
| `summary_next_gate_phase60l` | PASS | phase60l |
| `summary_phase61_allowed_false` | PASS | phase61 false |
| `no_raw_stdout_key_in_validationfailed-root-cause-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_validationfailed-root-cause-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_validationfailed-root-cause-summary.json` | PASS | command_key |
| `no_home_path_in_validationfailed-root-cause-summary.json` | PASS | home_path |
| `no_tmp_path_in_validationfailed-root-cause-summary.json` | PASS | tmp_path |
| `no_email_like_in_validationfailed-root-cause-summary.json` | PASS | email_like |
| `no_developer_id_application_in_validationfailed-root-cause-summary.json` | PASS | developer_id_application |
| `no_apple_development_in_validationfailed-root-cause-summary.json` | PASS | apple_development |
| `no_raw_stdout_key_in_validationfailed-root-cause-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_validationfailed-root-cause-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_validationfailed-root-cause-summary.md` | PASS | command_key |
| `no_home_path_in_validationfailed-root-cause-summary.md` | PASS | home_path |
| `no_tmp_path_in_validationfailed-root-cause-summary.md` | PASS | tmp_path |
| `no_email_like_in_validationfailed-root-cause-summary.md` | PASS | email_like |
| `no_developer_id_application_in_validationfailed-root-cause-summary.md` | PASS | developer_id_application |
| `no_apple_development_in_validationfailed-root-cause-summary.md` | PASS | apple_development |
