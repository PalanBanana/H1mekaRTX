# Actual Local Signing Hard Opt-In Check

- Decision: `PASS_ACTUAL_LOCAL_SIGNING_HARD_OPTIN_READY`
- Default Refuses Signing: `True`
- Hard Opt-In Flags Required: `True`
- CI Signing Attempted: `False`
- Codesign Executed By Default: `False`
- Codesign Signing Attempted In CI: `False`
- Signed Package Created In CI: `False`
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
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/actual-local-signing-hard-optin.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/actual-local-signing-hard-optin.md |
| `signer_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/scripts/actual-local-signing-hard-optin.py |
| `phase53_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-local-signing-opt-in-gate.json |
| `phase52_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json |
| `manifest_schema` | PASS | manifest schema |
| `phase53_schema` | PASS | phase53 schema |
| `phase52_schema` | PASS | phase52 schema |
| `manifest_actual_local_signing_hard_optin_ready_true` | PASS | actual_local_signing_hard_optin_ready |
| `manifest_default_refuses_signing_true` | PASS | default_refuses_signing |
| `manifest_hard_optin_flags_required_true` | PASS | hard_optin_flags_required |
| `manifest_ci_signing_attempted_false` | PASS | ci_signing_attempted |
| `manifest_codesign_executed_by_default_false` | PASS | codesign_executed_by_default |
| `manifest_codesign_signing_attempted_in_ci_false` | PASS | codesign_signing_attempted_in_ci |
| `manifest_signed_package_created_in_ci_false` | PASS | signed_package_created_in_ci |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_submit_activation_allowed_now_false` | PASS | submit_activation_allowed_now |
| `manifest_submit_deactivation_allowed_now_false` | PASS | submit_deactivation_allowed_now |
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
| `manifest_requires___i_understand_local_signing` | PASS | --i-understand-local-signing |
| `signer_parses___i_understand_local_signing` | PASS | --i-understand-local-signing |
| `manifest_requires___signing_identity` | PASS | --signing-identity |
| `signer_parses___signing_identity` | PASS | --signing-identity |
| `manifest_requires___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
| `signer_parses___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
| `signer_contains_REFUSE_SIGNING_HARD_OPTIN_NOT_SATISFIED` | PASS | REFUSE_SIGNING_HARD_OPTIN_NOT_SATISFIED |
| `signer_contains_local_scope_ok` | PASS | local_scope_ok |
| `signer_contains_host_report_bundle` | PASS | host-report-bundle |
| `signer_contains_codesign` | PASS | codesign |
| `signer_contains_sign_embedded_dext` | PASS | sign_embedded_dext |
| `signer_contains_verify_embedded_dext` | PASS | verify_embedded_dext |
| `signer_contains_sign_host_app` | PASS | sign_host_app |
| `signer_contains_verify_host_app` | PASS | verify_host_app |
| `signer_contains_dump_host_entitlements` | PASS | dump_host_entitlements |
| `signer_contains_dump_dext_entitlements` | PASS | dump_dext_entitlements |
| `signer_contains_activation_still_blocked` | PASS | activation_still_blocked |
| `signer_contains_provider_open_still_blocked` | PASS | provider_open_still_blocked |
| `signer_contains_bar_mapping_still_blocked` | PASS | bar_mapping_still_blocked |
| `signer_contains_gpu_command_submission_still_blocked` | PASS | gpu_command_submission_still_blocked |
