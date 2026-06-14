# Local Read-Only UI Baseline Collector Check

- Generated At UTC: `2026-06-14T01:43:12.961100+00:00`
- Decision: `PASS_LOCAL_READONLY_UI_BASELINE_COLLECTOR_READY`
- Classification: `CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR`
- Scope: `Phase 36 local read-only UI baseline collector`
- Local Baseline Only: `True`
- Host Report Bundle Local Only: `True`
- Measurement Not Acceleration Proof: `True`
- UI Compositor Proof Not Claimed: `True`
- Metal Proof Not Claimed: `True`
- Dock Acceleration Not Claimed: `True`
- Transparency Acceleration Not Claimed: `True`
- Blur Acceleration Not Claimed: `True`
- Local Read-Only UI Baseline State: `COLLECTED_OR_UNAVAILABLE`
- UI Frame Pacing / Latency Measurement State: `NOT_ATTEMPTED`
- WindowServer Attribution Proof State: `NOT_ATTEMPTED`
- UI Compositor Proof State: `NOT_ATTEMPTED`
- Metal Proof State: `NOT_ATTEMPTED`
- Real GPU Command Execution Attempted: `False`
- RTX5070 Workload Attribution Claimed: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Timing

Phase 36 collects local read-only UI baseline information only.

The local host-report-bundle output is intentionally not committed.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
| `contract_file_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/hackintosh/local-readonly-ui-baseline-collector.md |
| `collector_manifest_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-activation/local-readonly-ui-baseline-collector.json |
| `local_baseline_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/ui-baseline/local-readonly-ui-baseline.json |
| `local_baseline_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/ui-baseline/local-readonly-ui-baseline.md |
| `metrics_schema_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-activation/ui-frame-pacing-latency-metrics.json |
| `attribution_schema_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-activation/windowserver-ca-quartzcore-attribution.json |
| `scenario_matrix_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-activation/ui-compositor-scenario-matrix.json |
| `requires_contract_token_classification_local_readonly_ui_baseline_collector` | PASS | CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR |
| `requires_contract_token_classification_ui_frame_pacing_latency_metric_schema` | PASS | CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA |
| `requires_contract_token_classification_windowserver_ca_quartzcore_attribution_schema` | PASS | CLASSIFICATION_WINDOWSERVER_CA_QUARTZCORE_ATTRIBUTION_SCHEMA |
| `requires_contract_token_classification_static_contract` | PASS | CLASSIFICATION_STATIC_CONTRACT |
| `requires_contract_token_local_readonly_ui_baseline_collector_only_true` | PASS | LOCAL_READONLY_UI_BASELINE_COLLECTOR_ONLY: True |
| `requires_contract_token_local_baseline_only_true` | PASS | LOCAL_BASELINE_ONLY: True |
| `requires_contract_token_host_report_bundle_local_only_true` | PASS | HOST_REPORT_BUNDLE_LOCAL_ONLY: True |
| `requires_contract_token_measurement_not_acceleration_proof_true` | PASS | MEASUREMENT_NOT_ACCELERATION_PROOF: True |
| `requires_contract_token_ui_compositor_proof_not_claimed_true` | PASS | UI_COMPOSITOR_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_metal_proof_not_claimed_true` | PASS | METAL_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_dock_acceleration_not_claimed_true` | PASS | DOCK_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_transparency_acceleration_not_claimed_true` | PASS | TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_blur_acceleration_not_claimed_true` | PASS | BLUR_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_mission_control_acceleration_not_claimed_true` | PASS | MISSION_CONTROL_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_launchpad_acceleration_not_claimed_true` | PASS | LAUNCHPAD_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_stage_manager_acceleration_not_claimed_true` | PASS | STAGE_MANAGER_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_objective_metrics_required_true` | PASS | OBJECTIVE_METRICS_REQUIRED: True |
| `requires_contract_token_before_after_baseline_required_true` | PASS | BEFORE_AFTER_BASELINE_REQUIRED: True |
| `requires_contract_token_windowserver_attribution_required_true` | PASS | WINDOWSERVER_ATTRIBUTION_REQUIRED: True |
| `requires_contract_token_core_animation_quartzcore_evidence_required_true` | PASS | CORE_ANIMATION_QUARTZCORE_EVIDENCE_REQUIRED: True |
| `requires_contract_token_metal_compositor_evidence_required_true` | PASS | METAL_COMPOSITOR_EVIDENCE_REQUIRED: True |
| `requires_contract_token_real_gpu_command_evidence_required_true` | PASS | REAL_GPU_COMMAND_EVIDENCE_REQUIRED: True |
| `requires_contract_token_rtx5070_workload_attribution_required_true` | PASS | RTX5070_WORKLOAD_ATTRIBUTION_REQUIRED: True |
| `requires_contract_token_local_readonly_ui_baseline_commands` | PASS | LOCAL_READONLY_UI_BASELINE_COMMANDS |
| `requires_contract_token_local_outputs_ignored_by_git` | PASS | LOCAL_OUTPUTS_IGNORED_BY_GIT |
| `requires_contract_token_committed_check_outputs` | PASS | COMMITTED_CHECK_OUTPUTS |
| `requires_contract_token_local_readonly_ui_baseline_buckets` | PASS | LOCAL_READONLY_UI_BASELINE_BUCKETS |
| `requires_contract_token_windowserver` | PASS | WindowServer |
| `requires_contract_token_dock` | PASS | Dock |
| `requires_contract_token_core_animation` | PASS | Core Animation |
| `requires_contract_token_quartzcore` | PASS | QuartzCore |
| `requires_contract_token_metal_compositor` | PASS | Metal compositor |
| `requires_contract_token_local_readonly_ui_baseline_state_collected_or_unavailable` | PASS | LOCAL_READONLY_UI_BASELINE_STATE: COLLECTED_OR_UNAVAILABLE |
| `requires_contract_token_ui_frame_pacing_latency_measurement_state_not_attempted` | PASS | UI_FRAME_PACING_LATENCY_MEASUREMENT_STATE: NOT_ATTEMPTED |
| `requires_contract_token_windowserver_attribution_proof_state_not_attempted` | PASS | WINDOWSERVER_ATTRIBUTION_PROOF_STATE: NOT_ATTEMPTED |
| `requires_contract_token_ui_compositor_proof_state_not_attempted` | PASS | UI_COMPOSITOR_PROOF_STATE: NOT_ATTEMPTED |
| `requires_contract_token_metal_proof_state_not_attempted` | PASS | METAL_PROOF_STATE: NOT_ATTEMPTED |
| `requires_contract_token_real_gpu_command_execution_attempted_false` | PASS | REAL_GPU_COMMAND_EXECUTION_ATTEMPTED: False |
| `requires_contract_token_rtx5070_workload_attribution_claimed_false` | PASS | RTX5070_WORKLOAD_ATTRIBUTION_CLAIMED: False |
| `requires_contract_token_real_gpu_acceleration_claimed_false` | PASS | REAL_GPU_ACCELERATION_CLAIMED: False |
| `requires_contract_token_ui_compositor_proof_claimed_false` | PASS | UI_COMPOSITOR_PROOF_CLAIMED: False |
| `requires_contract_token_metal_proof_claimed_false` | PASS | METAL_PROOF_CLAIMED: False |
| `manifest_schema_matches` | PASS | manifest schema |
| `baseline_schema_matches` | PASS | baseline schema |
| `metrics_schema_loaded` | PASS | metrics schema |
| `attribution_schema_loaded` | PASS | attribution schema |
| `scenario_matrix_loaded` | PASS | scenario matrix |
| `manifest_local_baseline_only` | PASS | local_baseline_only=true |
| `manifest_not_acceleration_proof` | PASS | measurement_not_acceleration_proof=true |
| `manifest_ui_not_claimed` | PASS | UI proof not claimed |
| `manifest_metal_not_claimed` | PASS | Metal proof not claimed |
| `baseline_local_baseline_only` | PASS | local_baseline_only=true |
| `baseline_not_acceleration_proof` | PASS | measurement_not_acceleration_proof=true |
| `baseline_ui_not_claimed` | PASS | UI proof not claimed |
| `baseline_metal_not_claimed` | PASS | Metal proof not claimed |
| `required_command_keys_present` | PASS | dock_recent_log,ioreg_display_connect,ioreg_framebuffer,process_table,sw_vers,system_profiler_displays_json,system_profiler_hardware_json,uname,windowserver_recent_log |
| `windowserver_visibility_recorded` | PASS | WindowServer |
| `dock_visibility_recorded` | PASS | Dock |
| `baseline_ui_frame_pacing_latency_measurement_state_not_attempted` | PASS | ui_frame_pacing_latency_measurement_state=NOT_ATTEMPTED |
| `baseline_windowserver_attribution_proof_state_not_attempted` | PASS | windowserver_attribution_proof_state=NOT_ATTEMPTED |
| `baseline_core_animation_attribution_proof_state_not_attempted` | PASS | core_animation_attribution_proof_state=NOT_ATTEMPTED |
| `baseline_quartzcore_attribution_proof_state_not_attempted` | PASS | quartzcore_attribution_proof_state=NOT_ATTEMPTED |
| `baseline_metal_compositor_attribution_proof_state_not_attempted` | PASS | metal_compositor_attribution_proof_state=NOT_ATTEMPTED |
| `baseline_ui_compositor_proof_state_not_attempted` | PASS | ui_compositor_proof_state=NOT_ATTEMPTED |
| `baseline_metal_proof_state_not_attempted` | PASS | metal_proof_state=NOT_ATTEMPTED |
| `baseline_real_gpu_command_execution_attempted_false` | PASS | real_gpu_command_execution_attempted=false |
| `baseline_rtx5070_workload_attribution_claimed_false` | PASS | rtx5070_workload_attribution_claimed=false |
| `baseline_real_gpu_acceleration_claimed_false` | PASS | real_gpu_acceleration_claimed=false |
| `baseline_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed=false |
| `baseline_metal_proof_claimed_false` | PASS | metal_proof_claimed=false |

## Conclusion

This phase adds local read-only UI baseline collection only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
