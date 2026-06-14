# Codesign Identity + Entitlement Dry-Run Check

- Decision: `PASS_CODESIGN_IDENTITY_ENTITLEMENT_DRYRUN_READY`
- Dry-Run Evidence Only: `True`
- Host Report Bundle Local Only: `True`
- Codesign Identity Discovery Attempted: `True`
- Codesign Signing Attempted: `False`
- Signed Package Created: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Summary

| Key | Value |
| --- | --- |
| `codesign_available` | `True` |
| `codesigning_identity_detected` | `True` |
| `codesigning_identity_line_count` | `1` |
| `dext_bundle_id_matches` | `True` |
| `dext_driverkit_entitlement_present` | `True` |
| `dext_entitlements_parse_ok` | `True` |
| `dext_info_parse_ok` | `True` |
| `dext_pci_transport_entitlement_present` | `True` |
| `host_bundle_id_matches` | `True` |
| `host_entitlements_parse_ok` | `True` |
| `host_info_parse_ok` | `True` |
| `host_system_extension_entitlement_present` | `True` |
| `security_available` | `True` |

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json |
| `local_report_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/codesign-entitlement-dryrun/codesign-identity-entitlement-dryrun.json |
| `summary_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/codesign-identity-entitlement-dryrun-summary.json |
| `summary_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/codesign-identity-entitlement-dryrun-summary.md |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/codesign-identity-entitlement-dryrun-evidence.md |
| `manifest_schema` | PASS | manifest schema |
| `local_report_schema` | PASS | local report schema |
| `summary_schema` | PASS | summary schema |
| `manifest_codesign_signing_attempted_false` | PASS | codesign_signing_attempted |
| `manifest_signed_package_created_false` | PASS | signed_package_created |
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
| `local_report_codesign_signing_attempted_false` | PASS | codesign_signing_attempted |
| `local_report_signed_package_created_false` | PASS | signed_package_created |
| `local_report_install_attempted_false` | PASS | install_attempted |
| `local_report_submit_activation_allowed_now_false` | PASS | submit_activation_allowed_now |
| `local_report_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `local_report_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `local_report_dext_load_attempted_false` | PASS | dext_load_attempted |
| `local_report_provider_open_attempted_false` | PASS | provider_open_attempted |
| `local_report_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `local_report_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `local_report_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `local_report_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `local_report_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `local_report_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `summary_codesign_signing_attempted_false` | PASS | codesign_signing_attempted |
| `summary_signed_package_created_false` | PASS | signed_package_created |
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
| `summary_host_info_parse_ok_true` | PASS | host_info_parse_ok |
| `summary_dext_info_parse_ok_true` | PASS | dext_info_parse_ok |
| `summary_host_entitlements_parse_ok_true` | PASS | host_entitlements_parse_ok |
| `summary_dext_entitlements_parse_ok_true` | PASS | dext_entitlements_parse_ok |
| `summary_host_bundle_id_matches_true` | PASS | host_bundle_id_matches |
| `summary_dext_bundle_id_matches_true` | PASS | dext_bundle_id_matches |
| `summary_host_system_extension_entitlement_present_true` | PASS | host_system_extension_entitlement_present |
| `summary_dext_driverkit_entitlement_present_true` | PASS | dext_driverkit_entitlement_present |
| `summary_dext_pci_transport_entitlement_present_true` | PASS | dext_pci_transport_entitlement_present |
| `command_summary_present` | PASS | command summary |
| `codesign_help_probe_raw_stdout_not_committed` | PASS | codesign_help_probe |
| `codesign_help_probe_raw_stderr_not_committed` | PASS | codesign_help_probe |
| `security_find_identity_codesigning_raw_stdout_not_committed` | PASS | security_find_identity_codesigning |
| `security_find_identity_codesigning_raw_stderr_not_committed` | PASS | security_find_identity_codesigning |
| `no_raw_stdout_key_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | raw_stderr_key |
| `no_home_path_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | home_path |
| `no_tmp_path_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | tmp_path |
| `no_email_like_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | email_like |
| `no_host_report_bundle_raw_path_in_codesign-identity-entitlement-dryrun-summary.json` | PASS | host_report_bundle_raw_path |
| `no_raw_stdout_key_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | raw_stdout_key |
| `no_raw_stderr_key_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | raw_stderr_key |
| `no_home_path_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | home_path |
| `no_tmp_path_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | tmp_path |
| `no_email_like_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | email_like |
| `no_host_report_bundle_raw_path_in_codesign-identity-entitlement-dryrun-summary.md` | PASS | host_report_bundle_raw_path |
