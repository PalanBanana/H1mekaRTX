# Scenario Marker Aggregation Check

- Decision: `PASS_SCENARIO_MARKER_AGGREGATION_READY`
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
- Next Gate: `phase60y-metal-hud-frame-pacing-capture-plan`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/scenario-marker-aggregation.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/hackintosh/scenario-marker-aggregation.md |
| `aggregator_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/aggregate-scenario-marker-events.py |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/scenario-marker-aggregation-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/scenario-marker-aggregation-summary.md |
| `phase60w_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/dock-transparency-blur-scenario-marker.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase60w_schema_if_present` | PASS | phase60w schema |
| `manifest_scenario_marker_aggregation_ready_true` | PASS | scenario_marker_aggregation_ready |
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
| `aggregator_contains_scenario-events.json` | PASS | scenario-events.json |
| `aggregator_contains_dock_magnification` | PASS | dock_magnification |
| `aggregator_contains_dock_hide_show` | PASS | dock_hide_show |
| `aggregator_contains_menu_bar_transparency` | PASS | menu_bar_transparency |
| `aggregator_contains_window_transparency` | PASS | window_transparency |
| `aggregator_contains_mission_control` | PASS | mission_control |
| `aggregator_contains_launchpad` | PASS | launchpad |
| `aggregator_contains_stage_manager` | PASS | stage_manager |
| `aggregator_contains_duration_seconds_avg` | PASS | duration_seconds_avg |
| `aggregator_contains_rtx5070_target_retained` | PASS | rtx5070_target_retained |
| `aggregator_contains_fallback_gpu_substitution_allowed` | PASS | fallback_gpu_substitution_allowed |
| `aggregator_contains_provider_open_attempted` | PASS | provider_open_attempted |
| `aggregator_contains_ioserviceopen_attempted` | PASS | ioserviceopen_attempted |
| `aggregator_contains_bar_mapping_attempted` | PASS | bar_mapping_attempted |
| `aggregator_contains_gpu_command_submission_attempted` | PASS | gpu_command_submission_attempted |
| `summary_scenario_marker_events_present_recorded` | PASS | scenario_marker_events_present |
| `summary_scenario_marker_event_count_recorded` | PASS | scenario_marker_event_count |
| `summary_supported_scenario_count_recorded` | PASS | supported_scenario_count |
| `summary_observed_scenario_count_recorded` | PASS | observed_scenario_count |
| `summary_completed_scenario_session_count_recorded` | PASS | completed_scenario_session_count |
| `summary_duration_seconds_count_recorded` | PASS | duration_seconds_count |
| `summary_duration_seconds_min_recorded` | PASS | duration_seconds_min |
| `summary_duration_seconds_max_recorded` | PASS | duration_seconds_max |
| `summary_duration_seconds_avg_recorded` | PASS | duration_seconds_avg |
| `summary_per_scenario_recorded` | PASS | per_scenario |
| `summary_next_gate_recorded` | PASS | next_gate |
| `summary_next_gate` | PASS | next gate |
| `summary_per_scenario_dict` | PASS | per_scenario dict |
| `no_raw_stdout_key_in_scenario-marker-aggregation-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_scenario-marker-aggregation-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_scenario-marker-aggregation-summary.json` | PASS | command_key |
| `no_home_path_in_scenario-marker-aggregation-summary.json` | PASS | home_path |
| `no_tmp_path_in_scenario-marker-aggregation-summary.json` | PASS | tmp_path |
| `no_email_like_in_scenario-marker-aggregation-summary.json` | PASS | email_like |
| `no_raw_stdout_key_in_scenario-marker-aggregation-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_scenario-marker-aggregation-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_scenario-marker-aggregation-summary.md` | PASS | command_key |
| `no_home_path_in_scenario-marker-aggregation-summary.md` | PASS | home_path |
| `no_tmp_path_in_scenario-marker-aggregation-summary.md` | PASS | tmp_path |
| `no_email_like_in_scenario-marker-aggregation-summary.md` | PASS | email_like |
