# Xcode DriverKit Project Materialization Plan Check

- Decision: `PASS_XCODE_DRIVERKIT_PROJECT_MATERIALIZATION_PLAN_READY`
- Project Inputs Only: `True`
- Expected Project: `apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj`
- Expected Project Exists: `False`
- Xcodebuild Attempted By This Phase: `False`
- Activation Submitted By This Phase: `False`
- Provider Open Attempted: `False`
- IOServiceOpen Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`
- Next Gate If Project Missing: `phase60n-xcodeproj-materialization-helper`
- Next Gate If Project Exists: `phase60l-real-driverkit-dext-build-gate-local-run`

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-xcode-materialization/xcode-driverkit-project-materialization-plan.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/xcode-driverkit-project-materialization-plan.md |
| `manual_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/README.md |
| `host_source_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Sources/H1mekaRTXHost/H1mekaRTXHost.swift |
| `dext_source_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Sources/H1mekaRTXDriver/H1mekaRTXDriver.cpp |
| `host_plist_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Config/H1mekaRTXHost-Info.plist |
| `dext_plist_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Config/H1mekaRTXDriver-Info.plist |
| `host_entitlements_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Config/H1mekaRTXHost.entitlements |
| `dext_entitlements_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/Config/H1mekaRTXDriver.entitlements |
| `phase60l_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/real-driverkit-dext-build-gate.json |
| `manifest_schema` | PASS | manifest schema |
| `phase60l_manifest_schema` | PASS | phase60l schema |
| `expected_project_not_required_yet` | PASS | /Users/h1meka/Dev/H1mekaRTX/apps/H1mekaRTXDriverKit/H1mekaRTXDriverKit.xcodeproj |
| `expected_project_currently_exists_recorded` | PASS | False |
| `host_bundle_id` | PASS | dev.h1meka.H1mekaRTXHost |
| `host_executable` | PASS | H1mekaRTXHost |
| `dext_bundle_id` | PASS | dev.h1meka.H1mekaRTXDriver |
| `dext_executable` | PASS | H1mekaRTXDriver |
| `dext_provider_class_iopcidevice` | PASS | IOPCIDevice |
| `dext_iopcimatch` | PASS | 0x2f0410de |
| `host_src_contains_SystemExtensions` | PASS | SystemExtensions |
| `host_src_contains_OSSystemExtensionRequest` | PASS | OSSystemExtensionRequest |
| `host_src_contains_default_no_activation` | PASS | default_no_activation |
| `host_src_contains_submit_activation_request` | PASS | submit_activation_request |
| `dext_src_contains_DriverKit_IOService.h` | PASS | DriverKit/IOService.h |
| `dext_src_contains_Start(IOService*_provider)` | PASS | Start(IOService* provider) |
| `dext_src_contains_no_provider_open` | PASS | no provider open |
| `dext_src_contains_no_BAR_mapping` | PASS | no BAR mapping |
| `dext_src_contains_no_GPU_command_submission` | PASS | no GPU command submission |
| `manifest_project_materialization_plan_ready_true` | PASS | project_materialization_plan_ready |
| `manifest_project_inputs_only_true` | PASS | project_inputs_only |
| `manifest_xcodebuild_attempted_by_this_phase_false` | PASS | xcodebuild_attempted_by_this_phase |
| `manifest_activation_submitted_by_this_phase_false` | PASS | activation_submitted_by_this_phase |
| `manifest_deactivation_submitted_by_this_phase_false` | PASS | deactivation_submitted_by_this_phase |
| `manifest_install_attempted_false` | PASS | install_attempted |
| `manifest_manual_dext_load_attempted_false` | PASS | manual_dext_load_attempted |
| `manifest_provider_open_attempted_false` | PASS | provider_open_attempted |
| `manifest_ioserviceopen_attempted_false` | PASS | ioserviceopen_attempted |
| `manifest_bar_mapping_attempted_false` | PASS | bar_mapping_attempted |
| `manifest_bar_mmio_mutation_attempted_false` | PASS | bar_mmio_mutation_attempted |
| `manifest_configuration_writes_attempted_false` | PASS | configuration_writes_attempted |
| `manifest_gpu_command_submission_attempted_false` | PASS | gpu_command_submission_attempted |
| `manifest_ui_compositor_proof_claimed_false` | PASS | ui_compositor_proof_claimed |
| `manifest_metal_proof_claimed_false` | PASS | metal_proof_claimed |
