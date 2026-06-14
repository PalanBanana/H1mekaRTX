# Metal HUD / Frame Pacing Capture Plan Check

- Decision: `PASS_METAL_HUD_FRAME_PACING_CAPTURE_PLAN_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Capture Plan Only: `True`
- Metal HUD Enabled By This Phase: `False`
- Metal Workload Run By This Phase: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Phase 61 Allowed Now: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate: `phase60z-local-metal-hud-capture-manifest`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/metal-hud-frame-pacing-capture-plan.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/hackintosh/metal-hud-frame-pacing-capture-plan.md |
| `aggregation_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/scenario-marker-aggregation.json |
| `matrix_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/rtx5070-ui-smoothness-evidence-matrix.json |
| `manifest_schema` | PASS | manifest schema |
| `aggregation_schema_if_present` | PASS | aggregation schema |
| `matrix_schema_if_present` | PASS | matrix schema |
| `manifest_metal_hud_frame_pacing_capture_plan_ready_true` | PASS | metal_hud_frame_pacing_capture_plan_ready |
| `manifest_rtx5070_target_retained_true` | PASS | rtx5070_target_retained |
| `manifest_dock_transparency_blur_scope_retained_true` | PASS | dock_transparency_blur_scope_retained |
| `manifest_capture_plan_only_true` | PASS | capture_plan_only |
| `manifest_raw_outputs_local_only_true` | PASS | raw_outputs_local_only |
| `manifest_fallback_gpu_substitution_allowed_false` | PASS | fallback_gpu_substitution_allowed |
| `manifest_metal_hud_enabled_by_this_phase_false` | PASS | metal_hud_enabled_by_this_phase |
| `manifest_metal_workload_run_by_this_phase_false` | PASS | metal_workload_run_by_this_phase |
| `manifest_current_rtx5070_metal_acceleration_claimed_false` | PASS | current_rtx5070_metal_acceleration_claimed |
| `manifest_current_rtx5070_ui_smoothness_claimed_false` | PASS | current_rtx5070_ui_smoothness_claimed |
| `manifest_current_windowserver_attribution_to_rtx5070_proven_false` | PASS | current_windowserver_attribution_to_rtx5070_proven |
| `manifest_current_core_animation_attribution_to_rtx5070_proven_false` | PASS | current_core_animation_attribution_to_rtx5070_proven |
| `manifest_current_quartzcore_attribution_to_rtx5070_proven_false` | PASS | current_quartzcore_attribution_to_rtx5070_proven |
| `manifest_current_metal_compositor_attribution_to_rtx5070_proven_false` | PASS | current_metal_compositor_attribution_to_rtx5070_proven |
| `manifest_phase61_allowed_now_false` | PASS | phase61_allowed_now |
| `manifest_xcodebuild_build_attempted_by_this_phase_false` | PASS | xcodebuild_build_attempted_by_this_phase |
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
| `manifest_rtx5070_vendor_id` | PASS | rtx5070_vendor_id=0x10de |
| `manifest_rtx5070_device_id` | PASS | rtx5070_device_id=0x2f04 |
| `manifest_rtx5070_iopcimatch` | PASS | rtx5070_iopcimatch=0x2f0410de |
| `manifest_next_gate` | PASS | next_gate=phase60z-local-metal-hud-capture-manifest |
| `scenario_dock_magnification` | PASS | dock_magnification |
| `scenario_dock_hide_show` | PASS | dock_hide_show |
| `scenario_dock_launch_animation` | PASS | dock_launch_animation |
| `scenario_menu_bar_transparency` | PASS | menu_bar_transparency |
| `scenario_window_transparency` | PASS | window_transparency |
| `scenario_sheet_blur` | PASS | sheet_blur |
| `scenario_sidebar_blur` | PASS | sidebar_blur |
| `scenario_window_movement` | PASS | window_movement |
| `scenario_window_resize` | PASS | window_resize |
| `scenario_mission_control` | PASS | mission_control |
| `scenario_launchpad` | PASS | launchpad |
| `scenario_stage_manager` | PASS | stage_manager |
| `scenario_desktop_space_switching` | PASS | desktop_space_switching |
| `metric_gpu_time_avg` | PASS | gpu_time_avg |
| `metric_cpu_time_avg` | PASS | cpu_time_avg |
| `metric_frame_time_avg` | PASS | frame_time_avg |
| `metric_frame_time_min` | PASS | frame_time_min |
| `metric_frame_time_max` | PASS | frame_time_max |
| `metric_frame_time_p50` | PASS | frame_time_p50 |
| `metric_frame_time_p95` | PASS | frame_time_p95 |
| `metric_frame_time_p99` | PASS | frame_time_p99 |
| `metric_present_delay_avg` | PASS | present_delay_avg |
| `metric_dropped_frame_count` | PASS | dropped_frame_count |
| `metric_hitch_count` | PASS | hitch_count |
| `metric_encoder_count` | PASS | encoder_count |
| `metric_shader_compilation_event_count` | PASS | shader_compilation_event_count |
| `metric_before_after_delta` | PASS | before_after_delta |
| `metric_scenario_marker_duration_seconds` | PASS | scenario_marker_duration_seconds |
| `attribution_scenario_marker_timing` | PASS | scenario_marker_timing |
| `attribution_metal_hud_frame_pacing_timing` | PASS | metal_hud_frame_pacing_timing |
| `attribution_windowserver_attribution` | PASS | windowserver_attribution |
| `attribution_core_animation_attribution` | PASS | core_animation_attribution |
| `attribution_quartzcore_attribution` | PASS | quartzcore_attribution |
| `attribution_metal_compositor_attribution` | PASS | metal_compositor_attribution |
| `attribution_rtx5070_attribution` | PASS | rtx5070_attribution |
| `attribution_fallback_gpu_attribution` | PASS | fallback_gpu_attribution |
| `doc_contains_Metal_HUD___Frame_Pacing_Capture_Plan` | PASS | Metal HUD / Frame Pacing Capture Plan |
| `doc_contains_The_target_remains_RTX_5070_only` | PASS | The target remains RTX 5070 only |
| `doc_contains_Fallback_GPU_substitution_is_not_accepted_as_RTX_5070_proof` | PASS | Fallback GPU substitution is not accepted as RTX 5070 proof |
| `doc_contains_This_phase_does_not_enable_Metal_HUD` | PASS | This phase does not enable Metal HUD |
| `doc_contains_This_phase_does_not_run_a_Metal_workload` | PASS | This phase does not run a Metal workload |
| `doc_contains_gpu_time_avg` | PASS | gpu_time_avg |
| `doc_contains_frame_time_p95` | PASS | frame_time_p95 |
| `doc_contains_present_delay_avg` | PASS | present_delay_avg |
| `doc_contains_shader_compilation_event_count` | PASS | shader_compilation_event_count |
| `doc_contains_WindowServer_attribution` | PASS | WindowServer attribution |
| `doc_contains_Core_Animation_attribution` | PASS | Core Animation attribution |
| `doc_contains_QuartzCore_attribution` | PASS | QuartzCore attribution |
| `doc_contains_Metal_compositor_attribution` | PASS | Metal compositor attribution |
| `doc_contains_RTX_5070_attribution` | PASS | RTX 5070 attribution |
| `doc_contains_provider_open_remains_blocked` | PASS | provider open remains blocked |
| `doc_contains_BAR_mapping_remains_blocked` | PASS | BAR mapping remains blocked |
| `doc_contains_GPU_command_submission_remains_blocked` | PASS | GPU command submission remains blocked |
| `doc_contains_Metal_proof_remains_blocked` | PASS | Metal proof remains blocked |
| `doc_contains_Dock_transparency_blur_proof_remains_blocked` | PASS | Dock/transparency/blur proof remains blocked |
