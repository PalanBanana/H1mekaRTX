# Local UI Baseline Artifact Summary Check

- Generated At UTC: `2026-06-14T01:54:02.328916+00:00`
- Decision: `PASS_LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_READY`
- Classification: `CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER`
- Scope: `Phase 37 local UI baseline artifact summarizer`
- Local Baseline Summary Only: `True`
- Host Report Bundle Local Only: `True`
- Raw Local Logs Not Committed: `True`
- Raw Command Stdout Not Committed: `True`
- Measurement Not Acceleration Proof: `True`
- UI Compositor Proof Not Claimed: `True`
- Metal Proof Not Claimed: `True`
- Summary JSON Present: `True`
- Local Baseline Input Present: `True`
- Real GPU Command Execution Attempted: `False`
- RTX5070 Workload Attribution Claimed: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Timing

Phase 37 summarizes local-only UI baseline artifacts into release-readiness fields.

It does not commit raw local logs or raw command stdout.

## Contract Checks

| Check Name | Status | Detail |
| --- | --- | --- |
| `contract_file_exists` | PASS | <REPO_ROOT>/docs/hackintosh/local-ui-baseline-artifact-summarizer.md |
| `summarizer_manifest_json_exists` | PASS | <REPO_ROOT>/tools/driverkit-activation/local-ui-baseline-artifact-summarizer.json |
| `summary_json_exists` | PASS | <REPO_ROOT>/release-readiness/local-ui-baseline-artifact-summary.json |
| `summary_md_exists` | PASS | <REPO_ROOT>/release-readiness/local-ui-baseline-artifact-summary.md |
| `local_baseline_input_exists` | PASS | <LOCAL_READONLY_UI_BASELINE_JSON> |
| `collector_manifest_exists` | PASS | <REPO_ROOT>/tools/driverkit-activation/local-readonly-ui-baseline-collector.json |
| `requires_contract_token_classification_local_ui_baseline_artifact_summarizer` | PASS | CLASSIFICATION_LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER |
| `requires_contract_token_classification_local_readonly_ui_baseline_collector` | PASS | CLASSIFICATION_LOCAL_READONLY_UI_BASELINE_COLLECTOR |
| `requires_contract_token_classification_ui_frame_pacing_latency_metric_schema` | PASS | CLASSIFICATION_UI_FRAME_PACING_LATENCY_METRIC_SCHEMA |
| `requires_contract_token_classification_static_contract` | PASS | CLASSIFICATION_STATIC_CONTRACT |
| `requires_contract_token_local_ui_baseline_artifact_summarizer_only_true` | PASS | LOCAL_UI_BASELINE_ARTIFACT_SUMMARIZER_ONLY: True |
| `requires_contract_token_local_baseline_summary_only_true` | PASS | LOCAL_BASELINE_SUMMARY_ONLY: True |
| `requires_contract_token_host_report_bundle_local_only_true` | PASS | HOST_REPORT_BUNDLE_LOCAL_ONLY: True |
| `requires_contract_token_raw_local_logs_not_committed_true` | PASS | RAW_LOCAL_LOGS_NOT_COMMITTED: True |
| `requires_contract_token_raw_command_stdout_not_committed_true` | PASS | RAW_COMMAND_STDOUT_NOT_COMMITTED: True |
| `requires_contract_token_measurement_not_acceleration_proof_true` | PASS | MEASUREMENT_NOT_ACCELERATION_PROOF: True |
| `requires_contract_token_ui_compositor_proof_not_claimed_true` | PASS | UI_COMPOSITOR_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_metal_proof_not_claimed_true` | PASS | METAL_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_dock_acceleration_not_claimed_true` | PASS | DOCK_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_transparency_acceleration_not_claimed_true` | PASS | TRANSPARENCY_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_blur_acceleration_not_claimed_true` | PASS | BLUR_ACCELERATION_NOT_CLAIMED: True |
| `requires_contract_token_windowserver_attribution_proof_not_claimed_true` | PASS | WINDOWSERVER_ATTRIBUTION_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_core_animation_attribution_proof_not_claimed_true` | PASS | CORE_ANIMATION_ATTRIBUTION_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_quartzcore_attribution_proof_not_claimed_true` | PASS | QUARTZCORE_ATTRIBUTION_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_metal_compositor_attribution_proof_not_claimed_true` | PASS | METAL_COMPOSITOR_ATTRIBUTION_PROOF_NOT_CLAIMED: True |
| `requires_contract_token_local_ui_baseline_summarizer_inputs` | PASS | LOCAL_UI_BASELINE_SUMMARIZER_INPUTS |
| `requires_contract_token_committed_summary_outputs` | PASS | COMMITTED_SUMMARY_OUTPUTS |
| `requires_contract_token_local_outputs_ignored_by_git` | PASS | LOCAL_OUTPUTS_IGNORED_BY_GIT |
| `requires_contract_token_local_ui_baseline_artifact_summary_buckets` | PASS | LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_BUCKETS |
| `requires_contract_token_local_ui_baseline_artifact_summary_state_summary_only` | PASS | LOCAL_UI_BASELINE_ARTIFACT_SUMMARY_STATE: SUMMARY_ONLY |
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
| `summary_schema_matches` | PASS | summary schema |
| `collector_manifest_loaded` | PASS | collector manifest |
| `manifest_summary_only` | PASS | summary only |
| `manifest_host_report_local_only` | PASS | host report local only |
| `manifest_raw_logs_not_committed` | PASS | raw logs not committed |
| `manifest_raw_stdout_not_committed` | PASS | raw stdout not committed |
| `manifest_not_acceleration_proof` | PASS | not acceleration proof |
| `manifest_ui_not_claimed` | PASS | UI proof not claimed |
| `manifest_metal_not_claimed` | PASS | Metal proof not claimed |
| `summary_summary_only` | PASS | summary only |
| `summary_host_report_local_only` | PASS | host report local only |
| `summary_raw_logs_not_committed` | PASS | raw logs not committed |
| `summary_raw_stdout_not_committed` | PASS | raw stdout not committed |
| `summary_not_acceleration_proof` | PASS | not acceleration proof |
| `summary_ui_not_claimed` | PASS | UI proof not claimed |
| `summary_metal_not_claimed` | PASS | Metal proof not claimed |
| `required_command_keys_present` | PASS | dock_recent_log,ioreg_display_connect,ioreg_framebuffer,process_table,sw_vers,system_profiler_displays_json,system_profiler_hardware_json,uname,windowserver_recent_log |
| `command_dock_recent_log_does_not_include_stdout` | PASS | dock_recent_log |
| `command_dock_recent_log_does_not_include_stderr` | PASS | dock_recent_log |
| `command_ioreg_display_connect_does_not_include_stdout` | PASS | ioreg_display_connect |
| `command_ioreg_display_connect_does_not_include_stderr` | PASS | ioreg_display_connect |
| `command_ioreg_framebuffer_does_not_include_stdout` | PASS | ioreg_framebuffer |
| `command_ioreg_framebuffer_does_not_include_stderr` | PASS | ioreg_framebuffer |
| `command_process_table_does_not_include_stdout` | PASS | process_table |
| `command_process_table_does_not_include_stderr` | PASS | process_table |
| `command_sw_vers_does_not_include_stdout` | PASS | sw_vers |
| `command_sw_vers_does_not_include_stderr` | PASS | sw_vers |
| `command_system_profiler_displays_json_does_not_include_stdout` | PASS | system_profiler_displays_json |
| `command_system_profiler_displays_json_does_not_include_stderr` | PASS | system_profiler_displays_json |
| `command_system_profiler_hardware_json_does_not_include_stdout` | PASS | system_profiler_hardware_json |
| `command_system_profiler_hardware_json_does_not_include_stderr` | PASS | system_profiler_hardware_json |
| `command_uname_does_not_include_stdout` | PASS | uname |
| `command_uname_does_not_include_stderr` | PASS | uname |
| `command_windowserver_recent_log_does_not_include_stdout` | PASS | windowserver_recent_log |
| `command_windowserver_recent_log_does_not_include_stderr` | PASS | windowserver_recent_log |
| `summary_ui_frame_pacing_latency_measurement_state_not_attempted` | PASS | ui_frame_pacing_latency_measurement_state=NOT_ATTEMPTED |
| `summary_windowserver_attribution_proof_state_not_attempted` | PASS | windowserver_attribution_proof_state=NOT_ATTEMPTED |
| `summary_core_animation_attribution_proof_state_not_attempted` | PASS | core_animation_attribution_proof_state=NOT_ATTEMPTED |
| `summary_quartzcore_attribution_proof_state_not_attempted` | PASS | quartzcore_attribution_proof_state=NOT_ATTEMPTED |
| `summary_metal_compositor_attribution_proof_state_not_attempted` | PASS | metal_compositor_attribution_proof_state=NOT_ATTEMPTED |
| `summary_ui_compositor_proof_state_not_attempted` | PASS | ui_compositor_proof_state=NOT_ATTEMPTED |
| `summary_metal_proof_state_not_attempted` | PASS | metal_proof_state=NOT_ATTEMPTED |
| `summary_real_gpu_command_execution_proof_state_not_attempted` | PASS | real_gpu_command_execution_proof_state=NOT_ATTEMPTED |
| `summary_rtx5070_workload_attribution_proof_state_not_attempted` | PASS | rtx5070_workload_attribution_proof_state=NOT_ATTEMPTED |
| `summary_real_gpu_command_execution_attempted_false` | PASS | real_gpu_command_execution_attempted=false |
| `summary_rtx5070_workload_attribution_claimed_false` | PASS | rtx5070_workload_attribution_claimed=false |
| `summary_real_gpu_acceleration_claimed_false` | PASS | real_gpu_acceleration_claimed=false |
| `summary_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed=false |
| `summary_metal_proof_claimed_false` | PASS | metal_proof_claimed=false |

## Conclusion

This phase adds local UI baseline artifact summarization only. It does not prove provider match, activate or deactivate a System Extension, load a dext, open a provider, map BAR memory, mutate configuration space, mutate MMIO, submit GPU commands, initialize firmware/reset/display paths, measure real acceleration, or claim RTX 5070 UI compositor acceleration.
