# DriverKit Local Toolchain Build Preflight Check

- Decision: `PASS_DRIVERKIT_LOCAL_TOOLCHAIN_BUILD_PREFLIGHT_READY`
- Local Preflight Only: `True`
- Host Report Bundle Local Only: `True`
- Build Attempted: `False`
- Signing Attempted: `False`
- Install Attempted: `False`
- System Extension Activation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived Toolchain Status

{
  "clangxx_available": true,
  "driverkit_sdk_available": true,
  "macos_sdk_available": true,
  "scaffold_inputs_present": true,
  "swiftc_available": true,
  "xcodebuild_available": true,
  "xcrun_available": true
}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/driverkit-local-toolchain-build-preflight.json |
| `local_report_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/driverkit-toolchain-preflight/driverkit-local-toolchain-build-preflight.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/driverkit-local-toolchain-build-preflight.md |
| `manifest_schema` | PASS | manifest schema |
| `local_report_schema` | PASS | local report schema |
| `manifest_build_attempted_false` | PASS | build_attempted |
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
| `local_report_build_attempted_false` | PASS | build_attempted |
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
| `scaffold_inputs_present` | PASS | scaffold inputs |
| `toolchain_status_recorded` | PASS | toolchain commands recorded |
