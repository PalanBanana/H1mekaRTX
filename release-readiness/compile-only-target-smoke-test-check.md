# Compile-Only Target Smoke Test Check

- Decision: `PASS_COMPILE_ONLY_TARGET_SMOKE_TEST_READY`
- Compile Only Evidence Only: `True`
- Host Report Bundle Local Only: `True`
- Build Artifact Created: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Status

{
  "compile_failures_allowed_at_preflight_stage": true,
  "compile_only_attempts_recorded": true,
  "driverkit_cpp_fsyntax_only_ran": true,
  "driverkit_cpp_fsyntax_only_returncode": 1,
  "host_swift_typecheck_ran": true,
  "host_swift_typecheck_returncode": 0,
  "plist_parse_all_ok": true
}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/compile-only-target-smoke-test.json |
| `local_report_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/compile-only-smoke/compile-only-target-smoke-test.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/compile-only-target-smoke-test.md |
| `manifest_schema` | PASS | manifest schema |
| `local_report_schema` | PASS | local report schema |
| `manifest_build_artifact_created_false` | PASS | build_artifact_created |
| `manifest_signing_attempted_false` | PASS | signing_attempted |
| `manifest_install_attempted_false` | PASS | install_attempted |
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
| `local_report_build_artifact_created_false` | PASS | build_artifact_created |
| `local_report_signing_attempted_false` | PASS | signing_attempted |
| `local_report_install_attempted_false` | PASS | install_attempted |
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
| `compile_only_attempts_recorded` | PASS | compile-only attempts recorded |
| `commands_recorded` | PASS | commands recorded |
| `plist_results_recorded` | PASS | plist results recorded |
| `plist_parse_all_ok` | PASS | plist parse all ok |
| `compile_failures_allowed_at_preflight_stage` | PASS | failures recorded only |
