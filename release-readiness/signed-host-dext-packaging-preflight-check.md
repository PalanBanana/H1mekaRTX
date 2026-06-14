# Signed Host + Dext Packaging Preflight Check

- Decision: `PASS_SIGNED_HOST_DEXT_PACKAGING_PREFLIGHT_READY`
- Packaging Preflight Only: `True`
- Signed Package Created: `False`
- Codesign Attempted: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- Submit Deactivation Allowed Now: `False`
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
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/signed-host-dext-packaging-preflight.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/signed-host-dext-packaging-preflight.md |
| `phase47_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/manual-activation-approval-readiness-gate.json |
| `phase46_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/user-approved-system-extension-activation-path.json |
| `manifest_schema` | PASS | manifest schema |
| `phase47_user_approval_allowed` | PASS | phase47 user approval |
| `phase46_activation_code_exists` | PASS | phase46 activation path |
| `manifest_packaging_preflight_only_true` | PASS | packaging_preflight_only |
| `manifest_signed_host_dext_packaging_preflight_ready_true` | PASS | signed_host_dext_packaging_preflight_ready |
| `manifest_signed_package_created_false` | PASS | signed_package_created |
| `manifest_codesign_attempted_false` | PASS | codesign_attempted |
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
| `layout_contains_H1mekaRTXHost.app_Contents_Library_SystemExtensions_dev.h1meka.H1mekaRTXDriver.dext` | PASS | H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext |
| `layout_contains_H1mekaRTXHost.app_Contents_Library_SystemExtensions_dev.h1meka.H1mekaRTXDriver.dext_Contents_Info.plist` | PASS | H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/Info.plist |
| `layout_contains_H1mekaRTXHost.app_Contents_Library_SystemExtensions_dev.h1meka.H1mekaRTXDriver.dext_Contents_MacOS_H1mekaRTXDriver` | PASS | H1mekaRTXHost.app/Contents/Library/SystemExtensions/dev.h1meka.H1mekaRTXDriver.dext/Contents/MacOS/H1mekaRTXDriver |
| `signing_contains_Apple_Developer_Team_ID` | PASS | Apple Developer Team ID |
| `signing_contains_com_apple_developer_system-extension_install` | PASS | com.apple.developer.system-extension.install |
| `signing_contains_com_apple_developer_driverkit` | PASS | com.apple.developer.driverkit |
| `signing_contains_com_apple_developer_driverkit_transport_pci` | PASS | com.apple.developer.driverkit.transport.pci |
| `signing_contains_bundle_ID_dev_h1meka_H1mekaRTXHost` | PASS | bundle ID dev.h1meka.H1mekaRTXHost |
| `signing_contains_bundle_ID_dev_h1meka_H1mekaRTXDriver` | PASS | bundle ID dev.h1meka.H1mekaRTXDriver |
| `pre_activation_contains_codesign_verification_passes_for_host_app` | PASS | codesign verification passes for host app |
| `pre_activation_contains_codesign_verification_passes_for_dext` | PASS | codesign verification passes for dext |
| `pre_activation_contains_entitlements_are_dumped_and_checked` | PASS | entitlements are dumped and checked |
| `pre_activation_contains_dext_nested_under_Contents_Library_SystemExtensions` | PASS | dext nested under Contents/Library/SystemExtensions |
| `pre_activation_contains_systemextensionsctl_status_captured_before_activation` | PASS | systemextensionsctl status captured before activation |
| `pre_activation_contains_rollback_deactivation_command_available` | PASS | rollback/deactivation command available |
| `pre_activation_contains_user_approval_is_expected_and_allowed` | PASS | user approval is expected and allowed |
| `pre_activation_contains_provider_open_remains_disabled` | PASS | provider open remains disabled |
| `pre_activation_contains_BAR_mapping_remains_disabled` | PASS | BAR mapping remains disabled |
| `pre_activation_contains_GPU_command_submission_remains_disabled` | PASS | GPU command submission remains disabled |
