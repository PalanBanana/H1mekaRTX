# Manual Local Signing Opt-In Gate Check

- Decision: `PASS_MANUAL_LOCAL_SIGNING_OPT_IN_GATE_READY`
- User May Opt In To Local Signing: `True`
- Local Signing Requires Explicit Flag: `True`
- Local Signing Allowed Now: `False`
- Command Gate Only: `True`
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
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-local-signing-opt-in-gate.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/manual-local-signing-opt-in-gate.md |
| `phase52_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-dryrun-command-plan.json |
| `phase51_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/local-unsigned-bundle-manifest-lock.json |
| `phase50_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/codesign-identity-entitlement-dryrun-evidence.json |
| `manifest_schema` | PASS | manifest schema |
| `phase52_schema` | PASS | phase52 schema |
| `phase51_schema` | PASS | phase51 schema |
| `phase50_schema` | PASS | phase50 schema |
| `manifest_manual_local_signing_opt_in_gate_ready_true` | PASS | manual_local_signing_opt_in_gate_ready |
| `manifest_user_may_opt_in_to_local_signing_true` | PASS | user_may_opt_in_to_local_signing |
| `manifest_local_signing_requires_explicit_flag_true` | PASS | local_signing_requires_explicit_flag |
| `manifest_command_gate_only_true` | PASS | command_gate_only |
| `manifest_local_signing_allowed_now_false` | PASS | local_signing_allowed_now |
| `manifest_codesign_executed_false` | PASS | codesign_executed |
| `manifest_codesign_signing_attempted_false` | PASS | codesign_signing_attempted |
| `manifest_signed_package_created_false` | PASS | signed_package_created |
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
| `required_before_contains_codesign_dry_run_command_plan_exists` | PASS | codesign dry-run command plan exists |
| `required_before_contains_unsigned_bundle_manifest_lock_exists` | PASS | unsigned bundle manifest lock exists |
| `required_before_contains_codesign_identity_evidence_exists` | PASS | codesign identity evidence exists |
| `required_before_contains_host_entitlement_parse_proof_exists` | PASS | host entitlement parse proof exists |
| `required_before_contains_dext_entitlement_parse_proof_exists` | PASS | dext entitlement parse proof exists |
| `required_before_contains_host_bundle_ID_matches` | PASS | host bundle ID matches |
| `required_before_contains_dext_bundle_ID_matches` | PASS | dext bundle ID matches |
| `required_before_contains_user_passes_an_explicit_future_signing_flag` | PASS | user passes an explicit future signing flag |
| `required_before_contains_signing_identity_is_selected_explicitly` | PASS | signing identity is selected explicitly |
| `required_before_contains_signing_output_remains_local_only` | PASS | signing output remains local-only |
| `required_before_contains_signed_artifact_manifest_is_generated` | PASS | signed artifact manifest is generated |
| `required_before_contains_activation_remains_blocked_after_signing_until_verify_gates_pass` | PASS | activation remains blocked after signing until verify gates pass |
| `future_signing_order_exact` | PASS | future signing order |
| `future_flag_contains___i_understand_local_signing` | PASS | --i-understand-local-signing |
| `future_flag_contains___signing_identity` | PASS | --signing-identity |
| `future_flag_contains___output_under_host_report_bundle` | PASS | --output-under-host-report-bundle |
