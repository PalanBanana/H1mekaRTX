# User-Approved System Extension Activation Path Check

- Decision: `PASS_USER_APPROVED_SYSTEM_EXTENSION_ACTIVATION_PATH_READY`
- Activation Capable Code Added: `True`
- Deactivation Capable Code Added: `True`
- Default Mode Status Only: `True`
- Dry-Run Mode Non-Submitting: `True`
- Manual Approval Allowed For Future Local Test: `True`
- CI Activation Attempted: `False`
- CI Deactivation Attempted: `False`
- System Extension Activation Attempted: `False`
- System Extension Deactivation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/user-approved-system-extension-activation-path.md |
| `host_swift_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/H1mekaRTXHost/H1mekaRTXHost.swift |
| `manifest_schema` | PASS | manifest schema |
| `activation_request_code_present` | PASS | activation request |
| `deactivation_request_code_present` | PASS | deactivation request |
| `submit_request_code_present` | PASS | submitRequest |
| `manual_submit_activation_flag_present` | PASS | --submit-activation |
| `manual_submit_deactivation_flag_present` | PASS | --submit-deactivation |
| `default_status_only_present` | PASS | status only |
| `dry_run_non_submitting_present` | PASS | dry-run |
| `provider_open_false_marker` | PASS | provider open false |
| `bar_mapping_false_marker` | PASS | bar mapping false |
| `gpu_command_false_marker` | PASS | gpu command false |
| `manifest_ci_activation_attempted_false` | PASS | ci_activation_attempted |
| `manifest_ci_deactivation_attempted_false` | PASS | ci_deactivation_attempted |
| `manifest_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `manifest_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `manifest_dext_load_attempted_false` | PASS | dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `manifest_activation_capable_code_added_true` | PASS | activation_capable_code_added |
| `manifest_deactivation_capable_code_added_true` | PASS | deactivation_capable_code_added |
| `manifest_default_mode_status_only_true` | PASS | default_mode_status_only |
| `manifest_dry_run_mode_non_submitting_true` | PASS | dry_run_mode_non_submitting |
| `manifest_manual_approval_allowed_for_future_local_test_true` | PASS | manual_approval_allowed_for_future_local_test |
