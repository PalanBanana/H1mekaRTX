# Local Read-Only RTX 5070 UI Baseline Check

- Decision: `PASS_LOCAL_READONLY_RTX5070_UI_BASELINE_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60w-dock-transparency-blur-scenario-marker`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/local-readonly-rtx5070-ui-baseline-collector.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/hackintosh/local-readonly-rtx5070-ui-baseline-collector.md |
| `collector_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/collect-local-readonly-rtx5070-ui-baseline.py |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-readonly-rtx5070-ui-baseline-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-readonly-rtx5070-ui-baseline-summary.md |
| `matrix_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `matrix_schema_if_present` | PASS | matrix schema |
| `manifest_local_readonly_rtx5070_ui_baseline_collector_ready_true` | PASS | local_readonly_rtx5070_ui_baseline_collector_ready |
| `manifest_rtx5070_target_retained_true` | PASS | rtx5070_target_retained |
| `manifest_dock_transparency_blur_scope_retained_true` | PASS | dock_transparency_blur_scope_retained |
| `manifest_raw_outputs_local_only_true` | PASS | raw_outputs_local_only |
| `manifest_fallback_gpu_substitution_allowed_false` | PASS | fallback_gpu_substitution_allowed |
| `summary_fallback_gpu_substitution_allowed_false` | PASS | fallback_gpu_substitution_allowed |
| `manifest_current_rtx5070_metal_acceleration_claimed_false` | PASS | current_rtx5070_metal_acceleration_claimed |
| `summary_current_rtx5070_metal_acceleration_claimed_false` | PASS | current_rtx5070_metal_acceleration_claimed |
| `manifest_current_rtx5070_ui_smoothness_claimed_false` | PASS | current_rtx5070_ui_smoothness_claimed |
| `summary_current_rtx5070_ui_smoothness_claimed_false` | PASS | current_rtx5070_ui_smoothness_claimed |
| `manifest_current_windowserver_attribution_to_rtx5070_proven_false` | PASS | current_windowserver_attribution_to_rtx5070_proven |
| `summary_current_windowserver_attribution_to_rtx5070_proven_false` | PASS | current_windowserver_attribution_to_rtx5070_proven |
| `manifest_current_core_animation_attribution_to_rtx5070_proven_false` | PASS | current_core_animation_attribution_to_rtx5070_proven |
| `summary_current_core_animation_attribution_to_rtx5070_proven_false` | PASS | current_core_animation_attribution_to_rtx5070_proven |
| `manifest_current_quartzcore_attribution_to_rtx5070_proven_false` | PASS | current_quartzcore_attribution_to_rtx5070_proven |
| `summary_current_quartzcore_attribution_to_rtx5070_proven_false` | PASS | current_quartzcore_attribution_to_rtx5070_proven |
| `manifest_current_metal_compositor_attribution_to_rtx5070_proven_false` | PASS | current_metal_compositor_attribution_to_rtx5070_proven |
| `summary_current_metal_compositor_attribution_to_rtx5070_proven_false` | PASS | current_metal_compositor_attribution_to_rtx5070_proven |
| `manifest_phase61_allowed_now_false` | PASS | phase61_allowed_now |
| `summary_phase61_allowed_now_false` | PASS | phase61_allowed_now |
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
| `manifest_rtx5070_vendor_id` | PASS | rtx5070_vendor_id=0x10de |
| `manifest_rtx5070_device_id` | PASS | rtx5070_device_id=0x2f04 |
| `manifest_rtx5070_iopcimatch` | PASS | rtx5070_iopcimatch=0x2f0410de |
| `manifest_next_gate` | PASS | next_gate=phase60w-dock-transparency-blur-scenario-marker |
| `collector_contains_system_profiler` | PASS | system_profiler |
| `collector_contains_SPDisplaysDataType` | PASS | SPDisplaysDataType |
| `collector_contains_IOPCIDevice` | PASS | IOPCIDevice |
| `collector_contains_IOAccelerator` | PASS | IOAccelerator |
| `collector_contains_IODisplayConnect` | PASS | IODisplayConnect |
| `collector_contains_WindowServer` | PASS | WindowServer |
| `collector_contains_Dock` | PASS | Dock |
| `collector_contains_reduceTransparency` | PASS | reduceTransparency |
| `collector_contains_0x10de` | PASS | 0x10de |
| `collector_contains_0x2f04` | PASS | 0x2f04 |
| `collector_contains_0x2f0410de` | PASS | 0x2f0410de |
| `collector_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `collector_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `collector_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `collector_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
| `summary_local_baseline_report_present_true_or_recorded` | PASS | local_baseline_report_present |
| `summary_rtx5070_target_retained_true_or_recorded` | PASS | rtx5070_target_retained |
| `summary_raw_stdout_not_committed_true_or_recorded` | PASS | raw_stdout_not_committed |
| `summary_raw_stderr_not_committed_true_or_recorded` | PASS | raw_stderr_not_committed |
| `summary_display_inventory_collected_recorded` | PASS | display_inventory_collected |
| `summary_iopcidevice_inventory_collected_recorded` | PASS | iopcidevice_inventory_collected |
| `summary_rtx5070_identity_token_observed_recorded` | PASS | rtx5070_identity_token_observed |
| `summary_vendor_10de_observed_recorded` | PASS | vendor_10de_observed |
| `summary_device_2f04_observed_recorded` | PASS | device_2f04_observed |
| `summary_iopcimatch_2f0410de_observed_recorded` | PASS | iopcimatch_2f0410de_observed |
| `summary_metal_string_observed_in_display_inventory_recorded` | PASS | metal_string_observed_in_display_inventory |
| `summary_windowserver_process_observed_recorded` | PASS | windowserver_process_observed |
| `summary_dock_process_observed_recorded` | PASS | dock_process_observed |
| `summary_rtx5070_acceleration_claim_valid_recorded` | PASS | rtx5070_acceleration_claim_valid |
| `summary_rtx5070_ui_smoothness_claim_valid_recorded` | PASS | rtx5070_ui_smoothness_claim_valid |
| `summary_accel_claim_valid_false` | PASS | accel false |
| `summary_smoothness_claim_valid_false` | PASS | smoothness false |
| `no_raw_stdout_key_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | command_key |
| `no_home_path_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | home_path |
| `no_tmp_path_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | tmp_path |
| `no_email_like_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | email_like |
| `no_apple_development_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | apple_development |
| `no_developer_id_application_in_local-readonly-rtx5070-ui-baseline-summary.json` | PASS | developer_id_application |
| `no_raw_stdout_key_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | command_key |
| `no_home_path_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | home_path |
| `no_tmp_path_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | tmp_path |
| `no_email_like_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | email_like |
| `no_apple_development_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | apple_development |
| `no_developer_id_application_in_local-readonly-rtx5070-ui-baseline-summary.md` | PASS | developer_id_application |
