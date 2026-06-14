# Local Entitlement Request Status Collector Check

- Decision: `PASS_LOCAL_ENTITLEMENT_REQUEST_STATUS_COLLECTOR_READY`
- RTX 5070 Target Retained: `True`
- Fallback GPU Substitution Allowed: `False`
- Entitlement Status Only: `True`
- Submission To Apple Performed By This Phase: `False`
- Provider Match Attempted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- Current RTX 5070 Metal Acceleration Claimed: `False`
- Current RTX 5070 UI Smoothness Claimed: `False`
- Next Gate: `phase62d-provider-match-readiness-gate`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/local-entitlement-request-status-collector.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/hackintosh/local-entitlement-request-status-collector.md |
| `collector_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/collect-local-entitlement-request-status.py |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-entitlement-request-status-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/local-entitlement-request-status-summary.md |
| `package_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/hackintosh/apple-driverkit-pcidriverkit-entitlement-request-package.json |
| `manifest_schema` | PASS | schema |
| `summary_schema` | PASS | schema |
| `package_schema_if_present` | PASS | package schema |
| `manifest_local_entitlement_request_status_collector_ready_true` | PASS | local_entitlement_request_status_collector_ready |
| `manifest_entitlement_status_only_true` | PASS | entitlement_status_only |
| `manifest_rtx5070_target_retained_true` | PASS | rtx5070_target_retained |
| `manifest_raw_outputs_local_only_true` | PASS | raw_outputs_local_only |
| `manifest_fallback_gpu_substitution_allowed_false` | PASS | fallback_gpu_substitution_allowed |
| `summary_fallback_gpu_substitution_allowed_false` | PASS | fallback_gpu_substitution_allowed |
| `manifest_apple_private_data_committed_false` | PASS | apple_private_data_committed |
| `summary_apple_private_data_committed_false` | PASS | apple_private_data_committed |
| `manifest_apple_team_id_value_committed_false` | PASS | apple_team_id_value_committed |
| `summary_apple_team_id_value_committed_false` | PASS | apple_team_id_value_committed |
| `manifest_apple_email_committed_false` | PASS | apple_email_committed |
| `summary_apple_email_committed_false` | PASS | apple_email_committed |
| `manifest_submission_to_apple_performed_by_this_phase_false` | PASS | submission_to_apple_performed_by_this_phase |
| `summary_submission_to_apple_performed_by_this_phase_false` | PASS | submission_to_apple_performed_by_this_phase |
| `manifest_provider_match_attempted_by_this_phase_false` | PASS | provider_match_attempted_by_this_phase |
| `summary_provider_match_attempted_by_this_phase_false` | PASS | provider_match_attempted_by_this_phase |
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
| `manifest_framebuffer_init_attempted_false` | PASS | framebuffer_init_attempted |
| `summary_framebuffer_init_attempted_false` | PASS | framebuffer_init_attempted |
| `manifest_display_engine_init_attempted_false` | PASS | display_engine_init_attempted |
| `summary_display_engine_init_attempted_false` | PASS | display_engine_init_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `summary_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `summary_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `manifest_current_rtx5070_metal_acceleration_claimed_false` | PASS | current_rtx5070_metal_acceleration_claimed |
| `summary_current_rtx5070_metal_acceleration_claimed_false` | PASS | current_rtx5070_metal_acceleration_claimed |
| `manifest_current_rtx5070_ui_smoothness_claimed_false` | PASS | current_rtx5070_ui_smoothness_claimed |
| `summary_current_rtx5070_ui_smoothness_claimed_false` | PASS | current_rtx5070_ui_smoothness_claimed |
| `required_ready_field_apple_developer_program_active` | PASS | apple_developer_program_active |
| `summary_records_apple_developer_program_active` | PASS | apple_developer_program_active |
| `collector_template_has_apple_developer_program_active` | PASS | apple_developer_program_active |
| `required_ready_field_apple_team_id_available` | PASS | apple_team_id_available |
| `summary_records_apple_team_id_available` | PASS | apple_team_id_available |
| `collector_template_has_apple_team_id_available` | PASS | apple_team_id_available |
| `required_ready_field_driverkit_entitlement_request_submitted` | PASS | driverkit_entitlement_request_submitted |
| `summary_records_driverkit_entitlement_request_submitted` | PASS | driverkit_entitlement_request_submitted |
| `collector_template_has_driverkit_entitlement_request_submitted` | PASS | driverkit_entitlement_request_submitted |
| `required_ready_field_pcidriverkit_transport_entitlement_request_submitted` | PASS | pcidriverkit_transport_entitlement_request_submitted |
| `summary_records_pcidriverkit_transport_entitlement_request_submitted` | PASS | pcidriverkit_transport_entitlement_request_submitted |
| `collector_template_has_pcidriverkit_transport_entitlement_request_submitted` | PASS | pcidriverkit_transport_entitlement_request_submitted |
| `required_ready_field_system_extension_capability_requested` | PASS | system_extension_capability_requested |
| `summary_records_system_extension_capability_requested` | PASS | system_extension_capability_requested |
| `collector_template_has_system_extension_capability_requested` | PASS | system_extension_capability_requested |
| `required_ready_field_host_app_id_configured` | PASS | host_app_id_configured |
| `summary_records_host_app_id_configured` | PASS | host_app_id_configured |
| `collector_template_has_host_app_id_configured` | PASS | host_app_id_configured |
| `required_ready_field_driver_app_id_configured` | PASS | driver_app_id_configured |
| `summary_records_driver_app_id_configured` | PASS | driver_app_id_configured |
| `collector_template_has_driver_app_id_configured` | PASS | driver_app_id_configured |
| `required_ready_field_driverkit_entitlement_approved` | PASS | driverkit_entitlement_approved |
| `summary_records_driverkit_entitlement_approved` | PASS | driverkit_entitlement_approved |
| `collector_template_has_driverkit_entitlement_approved` | PASS | driverkit_entitlement_approved |
| `required_ready_field_pcidriverkit_transport_entitlement_approved` | PASS | pcidriverkit_transport_entitlement_approved |
| `summary_records_pcidriverkit_transport_entitlement_approved` | PASS | pcidriverkit_transport_entitlement_approved |
| `collector_template_has_pcidriverkit_transport_entitlement_approved` | PASS | pcidriverkit_transport_entitlement_approved |
| `required_ready_field_system_extension_capability_approved` | PASS | system_extension_capability_approved |
| `summary_records_system_extension_capability_approved` | PASS | system_extension_capability_approved |
| `collector_template_has_system_extension_capability_approved` | PASS | system_extension_capability_approved |
| `required_ready_field_provisioning_profiles_regenerated_after_approval` | PASS | provisioning_profiles_regenerated_after_approval |
| `summary_records_provisioning_profiles_regenerated_after_approval` | PASS | provisioning_profiles_regenerated_after_approval |
| `collector_template_has_provisioning_profiles_regenerated_after_approval` | PASS | provisioning_profiles_regenerated_after_approval |
| `summary_ready_for_provider_match_recorded` | PASS | ready flag |
| `summary_next_gate` | PASS | next gate |
| `manifest_next_gate` | PASS | next gate |
| `no_home_path_in_local-entitlement-request-status-summary.json` | PASS | home_path |
| `no_tmp_path_in_local-entitlement-request-status-summary.json` | PASS | tmp_path |
| `no_email_like_in_local-entitlement-request-status-summary.json` | PASS | email_like |
| `no_team_id_label_in_local-entitlement-request-status-summary.json` | PASS | team_id_label |
| `no_home_path_in_local-entitlement-request-status-summary.md` | PASS | home_path |
| `no_tmp_path_in_local-entitlement-request-status-summary.md` | PASS | tmp_path |
| `no_email_like_in_local-entitlement-request-status-summary.md` | PASS | email_like |
| `no_team_id_label_in_local-entitlement-request-status-summary.md` | PASS | team_id_label |
