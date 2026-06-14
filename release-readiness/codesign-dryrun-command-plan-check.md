# Codesign Dry-Run Command Plan Check

- Decision: `PASS_CODESIGN_DRYRUN_COMMAND_PLAN_READY`
- Command Plan Only: `True`
- Codesign Executed: `False`
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

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json |
| `generated_json_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/codesign-dryrun-command-plan.json |
| `generated_md_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/release-readiness/codesign-dryrun-command-plan.md |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/codesign-dryrun-command-plan.md |
| `phase51_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/local-unsigned-bundle-manifest-lock.json |
| `phase50_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json |
| `manifest_schema` | PASS | manifest schema |
| `generated_schema` | PASS | generated schema |
| `phase51_schema` | PASS | phase51 schema |
| `phase50_schema` | PASS | phase50 schema |
| `manifest_command_plan_only_true` | PASS | command_plan_only |
| `manifest_codesign_executed_false` | PASS | codesign_executed |
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
| `generated_command_plan_only_true` | PASS | command_plan_only |
| `generated_codesign_executed_false` | PASS | codesign_executed |
| `generated_codesign_signing_attempted_false` | PASS | codesign_signing_attempted |
| `generated_signed_package_created_false` | PASS | signed_package_created |
| `generated_install_attempted_false` | PASS | install_attempted |
| `generated_submit_activation_allowed_now_false` | PASS | submit_activation_allowed_now |
| `generated_system_extension_activation_attempted_false` | PASS | system_extension_activation_attempted |
| `generated_system_extension_deactivation_attempted_false` | PASS | system_extension_deactivation_attempted |
| `generated_dext_load_attempted_false` | PASS | dext_load_attempted |
| `generated_provider_open_attempted_false` | PASS | provider_open_attempted |
| `generated_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `generated_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `generated_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `generated_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `generated_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `generated_metal_proof_claimed_false` | PASS | metal_proof_claimed |
| `contains_command_sign_embedded_dext` | PASS | sign_embedded_dext |
| `contains_command_verify_embedded_dext` | PASS | verify_embedded_dext |
| `contains_command_sign_host_app` | PASS | sign_host_app |
| `contains_command_verify_host_app` | PASS | verify_host_app |
| `contains_command_dump_host_entitlements` | PASS | dump_host_entitlements |
| `contains_command_dump_dext_entitlements` | PASS | dump_dext_entitlements |
| `contains_command_capture_systemextensionsctl_status_before_activation` | PASS | capture_systemextensionsctl_status_before_activation |
| `planned_order_exact` | PASS | planned order |
| `sign_embedded_dext_execute_now_false` | PASS | sign_embedded_dext |
| `sign_embedded_dext_command_nonempty` | PASS | sign_embedded_dext |
| `verify_embedded_dext_execute_now_false` | PASS | verify_embedded_dext |
| `verify_embedded_dext_command_nonempty` | PASS | verify_embedded_dext |
| `sign_host_app_execute_now_false` | PASS | sign_host_app |
| `sign_host_app_command_nonempty` | PASS | sign_host_app |
| `verify_host_app_execute_now_false` | PASS | verify_host_app |
| `verify_host_app_command_nonempty` | PASS | verify_host_app |
| `dump_host_entitlements_execute_now_false` | PASS | dump_host_entitlements |
| `dump_host_entitlements_command_nonempty` | PASS | dump_host_entitlements |
| `dump_dext_entitlements_execute_now_false` | PASS | dump_dext_entitlements |
| `dump_dext_entitlements_command_nonempty` | PASS | dump_dext_entitlements |
| `capture_systemextensionsctl_status_before_activation_execute_now_false` | PASS | capture_systemextensionsctl_status_before_activation |
| `capture_systemextensionsctl_status_before_activation_command_nonempty` | PASS | capture_systemextensionsctl_status_before_activation |
| `derived_all_commands_marked_execute_now_false_true` | PASS | all_commands_marked_execute_now_false |
| `derived_contains_sign_embedded_dext_true` | PASS | contains_sign_embedded_dext |
| `derived_contains_verify_embedded_dext_true` | PASS | contains_verify_embedded_dext |
| `derived_contains_sign_host_app_true` | PASS | contains_sign_host_app |
| `derived_contains_verify_host_app_true` | PASS | contains_verify_host_app |
| `derived_contains_entitlement_dump_true` | PASS | contains_entitlement_dump |
| `derived_contains_systemextensionsctl_status_capture_true` | PASS | contains_systemextensionsctl_status_capture |
| `no_real_identity_in_md` | PASS | no real identity |
| `placeholder_identity_used` | PASS | placeholder identity |
