# Real DriverKit Dext Build Gate Check

- Decision: `PASS_REAL_DRIVERKIT_DEXT_BUILD_GATE_READY`
- Local Build Gate Only: `True`
- CI Xcodebuild Attempted: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/real-driverkit-dext-build-gate.md |
| `script_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/real-driverkit-dext-build-gate.py |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/real-driverkit-dext-build-gate-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/real-driverkit-dext-build-gate-summary.md |
| `phase60k_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/validationfailed-root-cause-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase60k_schema` | PASS | phase60k schema |
| `manifest_real_driverkit_dext_build_gate_ready_true` | PASS | real_driverkit_dext_build_gate_ready |
| `manifest_default_refuses_build_true` | PASS | default_refuses_build |
| `manifest_hard_optin_flags_required_true` | PASS | hard_optin_flags_required |
| `manifest_ci_xcodebuild_attempted_false` | PASS | ci_xcodebuild_attempted |
| `manifest_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `manifest_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `script_contains___i_understand_local_driverkit_build` | PASS | --i-understand-local-driverkit-build |
| `script_contains___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
| `script_contains___project` | PASS | --project |
| `script_contains___workspace` | PASS | --workspace |
| `script_contains___scheme` | PASS | --scheme |
| `script_contains_xcodebuild` | PASS | xcodebuild |
| `script_contains___sdk` | PASS | --sdk |
| `script_contains_driverkit` | PASS | driverkit |
| `script_contains_star_dext` | PASS | *.dext |
| `script_contains_codesign` | PASS | codesign |
| `script_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `script_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `script_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `script_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
| `summary_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `summary_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `summary_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `summary_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `summary_install_attempted_false` | PASS | install_attempted |
| `summary_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `summary_provider_open_attempted_false` | PASS | provider_open_attempted |
| `summary_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `summary_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `summary_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `summary_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `summary_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `summary_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `summary_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `summary_real_driverkit_dext_built_recorded` | PASS | real dext built recorded |
| `summary_phase61_allowed_false` | PASS | phase61 false |
| `no_raw_stdout_key_in_real-driverkit-dext-build-gate-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_real-driverkit-dext-build-gate-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_real-driverkit-dext-build-gate-summary.json` | PASS | command_key |
| `no_home_path_in_real-driverkit-dext-build-gate-summary.json` | PASS | home_path |
| `no_tmp_path_in_real-driverkit-dext-build-gate-summary.json` | PASS | tmp_path |
| `no_email_like_in_real-driverkit-dext-build-gate-summary.json` | PASS | email_like |
| `no_developer_id_application_in_real-driverkit-dext-build-gate-summary.json` | PASS | developer_id_application |
| `no_apple_development_in_real-driverkit-dext-build-gate-summary.json` | PASS | apple_development |
| `no_raw_stdout_key_in_real-driverkit-dext-build-gate-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_real-driverkit-dext-build-gate-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_real-driverkit-dext-build-gate-summary.md` | PASS | command_key |
| `no_home_path_in_real-driverkit-dext-build-gate-summary.md` | PASS | home_path |
| `no_tmp_path_in_real-driverkit-dext-build-gate-summary.md` | PASS | tmp_path |
| `no_email_like_in_real-driverkit-dext-build-gate-summary.md` | PASS | email_like |
| `no_developer_id_application_in_real-driverkit-dext-build-gate-summary.md` | PASS | developer_id_application |
| `no_apple_development_in_real-driverkit-dext-build-gate-summary.md` | PASS | apple_development |
