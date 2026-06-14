# Unsigned Local App Bundle Layout Check

- Decision: `PASS_UNSIGNED_LOCAL_APP_BUNDLE_LAYOUT_READY`
- Local Output Only: `True`
- Host Report Bundle Local Only: `True`
- Signed Package Created: `False`
- Codesign Attempted: `False`
- Install Attempted: `False`
- Submit Activation Allowed Now: `False`
- System Extension Activation Attempted: `False`
- System Extension Deactivation Attempted: `False`
- Dext Load Attempted: `False`
- Provider Open Attempted: `False`
- BAR Mapping Attempted: `False`
- GPU Command Submission Attempted: `False`
- UI Compositor Proof Claimed: `False`
- Metal Proof Claimed: `False`

## Derived

{
  "all_plists_parse_ok": true,
  "contains_dext_under_systemextensions": true,
  "contains_systemextensions_dir": true,
  "layout_created": true,
  "unsigned_placeholders_only": true
}

## Checks

| Check | Status | Detail |
| --- | --- | --- |
| `manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/unsigned-local-app-bundle-layout-generator.json |
| `local_report_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/host-report-bundle/unsigned-app-bundle/unsigned-local-app-bundle-layout.json |
| `doc_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/docs/driverkit/unsigned-local-app-bundle-layout-generator.md |
| `phase48_manifest_exists` | PASS | /Users/h1meka/Dev/H1mekaRTX/tools/driverkit-buildable-scaffold/signed-host-dext-packaging-preflight.json |
| `manifest_schema` | PASS | manifest schema |
| `local_report_schema` | PASS | local report schema |
| `phase48_schema` | PASS | phase48 schema |
| `manifest_signed_package_created_false` | PASS | signed_package_created |
| `manifest_codesign_attempted_false` | PASS | codesign_attempted |
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
| `local_report_signed_package_created_false` | PASS | signed_package_created |
| `local_report_codesign_attempted_false` | PASS | codesign_attempted |
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
| `layout_created` | PASS | layout created |
| `all_plists_parse_ok` | PASS | plists parse |
| `contains_systemextensions_dir` | PASS | SystemExtensions dir |
| `contains_dext_under_systemextensions` | PASS | dext under SystemExtensions |
| `unsigned_placeholders_only` | PASS | unsigned placeholders only |
| `path_app_root_present` | PASS | app_root |
| `path_host_info_present` | PASS | host_info |
| `path_host_placeholder_present` | PASS | host_placeholder |
| `path_systemextensions_dir_present` | PASS | systemextensions_dir |
| `path_dext_root_present` | PASS | dext_root |
| `path_dext_info_present` | PASS | dext_info |
| `path_dext_placeholder_present` | PASS | dext_placeholder |
