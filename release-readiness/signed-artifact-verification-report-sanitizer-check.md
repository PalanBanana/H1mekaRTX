# Signed Artifact Verification Report Sanitizer Check

- Decision: `PASS_SIGNED_ARTIFACT_VERIFICATION_REPORT_SANITIZER_READY`
- Local Report Sanitizer Only: `True`
- Raw Stdout Not Committed: `True`
- Raw Stderr Not Committed: `True`
- Signing Identity Not Committed: `True`
- Entitlement Dump Body Not Committed: `True`
- Codesign Executed By Sanitizer: `False`
- Codesign Signing Attempted By Sanitizer: `False`
- Signed Package Created By Sanitizer: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/signed-artifact-verification-report-sanitizer.json |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/signed-artifact-verification-report-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/signed-artifact-verification-report-summary.md |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/signed-artifact-verification-report-sanitizer.md |
| `phase54_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json |
| `manifest_schema` | PASS | manifest schema |
| `summary_schema` | PASS | summary schema |
| `phase54_schema` | PASS | phase54 schema |
| `manifest_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `manifest_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `manifest_signing_identity_not_committed_true` | PASS | signing_identity_not_committed |
| `manifest_entitlement_dump_body_not_committed_true` | PASS | entitlement_dump_body_not_committed |
| `manifest_codesign_executed_by_sanitizer_false` | PASS | codesign_executed_by_sanitizer |
| `manifest_codesign_signing_attempted_by_sanitizer_false` | PASS | codesign_signing_attempted_by_sanitizer |
| `manifest_signed_package_created_by_sanitizer_false` | PASS | signed_package_created_by_sanitizer |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_submit_activation_allowed_now_false` | PASS | submit_activation_allowed_now |
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
| `summary_raw_stdout_not_committed_true` | PASS | raw_stdout_not_committed |
| `summary_raw_stderr_not_committed_true` | PASS | raw_stderr_not_committed |
| `summary_signing_identity_not_committed_true` | PASS | signing_identity_not_committed |
| `summary_entitlement_dump_body_not_committed_true` | PASS | entitlement_dump_body_not_committed |
| `summary_codesign_executed_by_sanitizer_false` | PASS | codesign_executed_by_sanitizer |
| `summary_codesign_signing_attempted_by_sanitizer_false` | PASS | codesign_signing_attempted_by_sanitizer |
| `summary_signed_package_created_by_sanitizer_false` | PASS | signed_package_created_by_sanitizer |
| `summary_install_attempted_false` | PASS | install_attempted |
| `summary_submit_activation_allowed_now_false` | PASS | submit_activation_allowed_now |
| `summary_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `summary_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `summary_dext_load_attempted_false` | PASS | dext_load_attempted |
| `summary_provider_open_attempted_false` | PASS | provider_open_attempted |
| `summary_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `summary_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `summary_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `summary_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `summary_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `summary_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `sanitized_commands_present_or_no_report` | PASS | sanitized commands dict |
| `boundary_activation_still_blocked_true` | PASS | activation_still_blocked |
| `boundary_provider_open_still_blocked_true` | PASS | provider_open_still_blocked |
| `boundary_bar_mapping_still_blocked_true` | PASS | bar_mapping_still_blocked |
| `boundary_gpu_command_submission_still_blocked_true` | PASS | gpu_command_submission_still_blocked |
| `no_raw_stdout_key_in_signed-artifact-verification-report-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_signed-artifact-verification-report-summary.json` | PASS | raw_stderr_key |
| `no_command_key_in_signed-artifact-verification-report-summary.json` | PASS | command_key |
| `no_home_path_in_signed-artifact-verification-report-summary.json` | PASS | home_path |
| `no_tmp_path_in_signed-artifact-verification-report-summary.json` | PASS | tmp_path |
| `no_email_like_in_signed-artifact-verification-report-summary.json` | PASS | email_like |
| `no_developer_id_application_in_signed-artifact-verification-report-summary.json` | PASS | developer_id_application |
| `no_apple_development_in_signed-artifact-verification-report-summary.json` | PASS | apple_development |
| `no_host_report_bundle_raw_path_in_signed-artifact-verification-report-summary.json` | PASS | host_report_bundle_raw_path |
| `no_raw_stdout_key_in_signed-artifact-verification-report-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_signed-artifact-verification-report-summary.md` | PASS | raw_stderr_key |
| `no_command_key_in_signed-artifact-verification-report-summary.md` | PASS | command_key |
| `no_home_path_in_signed-artifact-verification-report-summary.md` | PASS | home_path |
| `no_tmp_path_in_signed-artifact-verification-report-summary.md` | PASS | tmp_path |
| `no_email_like_in_signed-artifact-verification-report-summary.md` | PASS | email_like |
| `no_developer_id_application_in_signed-artifact-verification-report-summary.md` | PASS | developer_id_application |
| `no_apple_development_in_signed-artifact-verification-report-summary.md` | PASS | apple_development |
| `no_host_report_bundle_raw_path_in_signed-artifact-verification-report-summary.md` | PASS | host_report_bundle_raw_path |
